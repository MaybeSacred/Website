from contextlib import AsyncExitStack
import importlib
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from uuid import uuid4

import httpx
import psycopg
from psycopg import sql

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
PACKAGE = "python-pi.data-ingestion-server"
storage = importlib.import_module(f"{PACKAGE}.postgres_data")
library_storage = importlib.import_module(f"{PACKAGE}.library_data")
app = importlib.import_module(f"{PACKAGE}.main").app


@unittest.skipUnless(os.getenv("TEST_POSTGRES_DSN"), "TEST_POSTGRES_DSN is not set")
class PostgresTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.dsn = os.environ["TEST_POSTGRES_DSN"]
        self.schema = "api_test_" + uuid4().hex
        async with await psycopg.AsyncConnection.connect(self.dsn) as connection:
            await connection.execute(
                sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema))
            )
        self.addAsyncCleanup(self.drop_schema)
        dsn_patch = patch.object(storage, "_postgres_dsn", return_value=self.dsn)
        dsn_patch.start()
        self.addCleanup(dsn_patch.stop)
        connect = storage._connect

        async def isolated_connect():
            connection = await connect()
            await connection.execute(
                sql.SQL("SET search_path TO {}").format(sql.Identifier(self.schema))
            )
            return connection

        connect_patch = patch.object(storage, "_connect", isolated_connect)
        connect_patch.start()
        self.addCleanup(connect_patch.stop)
        library_connect_patch = patch.object(library_storage, "_connect", isolated_connect)
        library_connect_patch.start()
        self.addCleanup(library_connect_patch.stop)
        await storage.initialize_database()
        await storage.initialize_database()

    async def drop_schema(self):
        async with await psycopg.AsyncConnection.connect(self.dsn) as connection:
            await connection.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(self.schema))
            )


class ApiTestCase(PostgresTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        stack = AsyncExitStack()
        self.addAsyncCleanup(stack.aclose)
        await stack.enter_async_context(app.router.lifespan_context(app))
        self.client = await stack.enter_async_context(httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ))

    async def create_home_object(self, name: str = "room") -> str:
        object_id = str(uuid4())
        response = await self.client.post(
            f"/home-objects/{object_id}", json=home_object_payload(name)
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIsNone(response.json())
        return object_id


def home_object_payload(name: str = "room") -> dict:
    return {
        "name": name,
        "tags": ["room", "upstairs"],
        "user_data": {"description": "test room"},
        "location": {"x": 1.5, "y": -2, "z": 3},
        "orientation": {"x": 0, "y": 0, "z": 0, "w": 1},
    }
