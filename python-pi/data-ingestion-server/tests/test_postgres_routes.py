import importlib
import os
from pathlib import Path
import sys
import unittest
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import httpx
from fastapi.testclient import TestClient

from api_support import PostgresTestCase

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
PACKAGE = "python-pi.data-ingestion-server"
storage = importlib.import_module(f"{PACKAGE}.postgres_data")
devices = importlib.import_module(f"{PACKAGE}.routers.devices")
ingestion = importlib.import_module(f"{PACKAGE}.routers.data_ingestion")
models = importlib.import_module(f"{PACKAGE}.domain.sensor_data")
home = importlib.import_module(f"{PACKAGE}.domain.home_object")
app = importlib.import_module(f"{PACKAGE}.main").app


class StorageTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.connection = AsyncMock()
        self.connection.__aenter__.return_value = self.connection
        self.cursor = self.connection.execute.return_value
        self.cursor.fetchall.return_value = []
        self.connect_patch = patch.object(
            storage, "_connect", AsyncMock(return_value=self.connection)
        )
        self.connect_patch.start()
        self.addCleanup(self.connect_patch.stop)

    async def test_initialization_includes_devices_and_index(self):
        await storage.initialize_database()
        statements = "\n".join(
            call.args[0] for call in self.connection.execute.await_args_list
        )
        for expected in (
            "CREATE TABLE IF NOT EXISTS versions",
            "CREATE TABLE IF NOT EXISTS home_objects",
            "CREATE TABLE IF NOT EXISTS devices",
            "REFERENCES home_objects(id)",
            "CREATE TABLE IF NOT EXISTS groups",
            "CREATE TABLE IF NOT EXISTS envelopes",
            "CREATE INDEX IF NOT EXISTS envelopes_device_event_time_idx",
        ):
            self.assertIn(expected, statements)
        self.assertEqual(
            self.connection.execute.await_args.args[0],
            "INSERT INTO versions (version) VALUES (1);",
        )

    async def test_initialization_skips_recorded_migrations(self):
        self.cursor.fetchall.return_value = [{"version": 0}, {"version": 1}]
        with (
            patch.object(storage, "migration_version_0", AsyncMock()) as migration,
            patch.object(storage, "migration_version_1", AsyncMock()) as library_migration,
        ):
            await storage.initialize_database()
            migration.assert_not_awaited()
            library_migration.assert_not_awaited()

    async def test_existing_database_applies_only_library_migration(self):
        self.cursor.fetchall.return_value = [{"version": 0}]
        with patch.object(storage, "migration_version_0", AsyncMock()) as migration:
            await storage.initialize_database()
            migration.assert_not_awaited()
        statements = "\n".join(call.args[0] for call in self.connection.execute.await_args_list)
        self.assertIn("CREATE TABLE libraries", statements)
        self.assertIn("CREATE TABLE documents", statements)
        self.assertIn("ON DELETE CASCADE", statements)
        self.assertIn("INSERT INTO versions (version) VALUES (1)", statements)

    async def test_failed_migration_does_not_record_version(self):
        self.connection.execute.side_effect = [
            self.cursor, self.cursor, self.cursor,
            storage.psycopg.OperationalError("migration failed"),
        ]
        with self.assertRaisesRegex(storage.psycopg.OperationalError, "migration failed"):
            await storage.initialize_database()
        statements = [call.args[0] for call in self.connection.execute.await_args_list]
        self.assertNotIn("INSERT INTO versions (version) VALUES (0);", statements)

    async def test_filtered_read_uses_bound_parameters_and_recording_time(self):
        mac = "device' OR true --"
        await storage.read_envelopes(
            mac, min_hours_ago=3, max_hours_ago=75,
            event_type="ENVIRONMENT_SENSOR",
        )
        sql, params = self.connection.execute.await_args.args
        sql = sql.as_string()
        self.assertNotIn(mac, sql)
        self.assertIn("recorded_at >= now() - %(max_age)s", sql)
        self.assertIn("recorded_at <= now() - %(min_age)s", sql)
        self.assertEqual(params, {
            "mac_address": mac, "event_type": "ENVIRONMENT_SENSOR",
            "max_age": timedelta(hours=75), "min_age": timedelta(hours=3),
        })

    async def test_unfiltered_read_has_no_time_or_event_restrictions(self):
        await storage.read_envelopes()
        sql, params = self.connection.execute.await_args.args
        sql = sql.as_string()
        self.assertNotIn("WHERE", sql)
        self.assertIn("ORDER BY recorded_at, id", sql)
        self.assertEqual(params, {})

    async def test_both_envelope_types_round_trip_all_fields(self):
        now = datetime.now(UTC)
        sensor = models.EnvironmentSensorDataDto(
            "ENVIRONMENT_SENSOR", "sensor", 1700000000,
            cpu_temperature=40, temperature=21, distance=12, humidity=50,
            lux=100, pressure=1013, uv=2, gas=3, water_depth_raw=4,
            moisture_percent=60,
        )
        heartbeat = models.HeartbeatDataDto(
            "HEARTBEAT", "sensor", "127.0.0.1", now
        )
        for data in (sensor, heartbeat):
            envelope = models.Envelope(uuid4(), now, data)
            await storage.write_envelope(envelope)
            _, values = self.connection.execute.await_args.args
            self.assertEqual(values["id"], envelope.id)
            self.assertEqual(values["recorded_at"], now)
            self.assertEqual(
                values["source_date"], storage._as_datetime(data.source_date)
            )
            self.cursor.fetchall.return_value = [values]
            result = (await storage.read_envelopes())[0]
            self.assertEqual(result.id, envelope.id)
            self.assertEqual(result.date, now)
            self.assertEqual(result.data.case, data.case)
            for field, value in vars(data).items():
                expected = storage._as_datetime(value) if field == "source_date" else value
                self.assertEqual(getattr(result.data, field), expected)

    async def test_unknown_event_is_not_silently_read_as_heartbeat(self):
        self.cursor.fetchall.return_value = [{"event_type": "UNKNOWN"}]
        with self.assertRaisesRegex(ValueError, "Unknown envelope event type"):
            await storage.read_envelopes()

    async def test_device_states_and_parameterized_lookup(self):
        device = devices.Device(
            uuid4(), "device'--", datetime.now(UTC),
            devices.UnprovisionedDevice("UNPROVISIONED"),
        )
        for status in (
            device.device_status,
            devices.ProvisionedDevice("PROVISIONED", "mac", uuid4()),
        ):
            device.device_status = status
            await storage.write_device(device)
            _, values = self.connection.execute.await_args.args
            self.cursor.fetchone.return_value = values
            self.assertEqual(await storage.read_device(device.name), device)
            sql, params = self.connection.execute.await_args.args
            self.assertNotIn(device.name, sql)
            self.assertEqual(params, (device.name,))
            self.cursor.fetchall.return_value = [values]
            self.assertEqual(await storage.read_devices(), [device])
        self.cursor.fetchone.return_value = None
        self.assertIsNone(await storage.read_device("missing"))

    async def test_delete_uses_strict_parameterized_cutoff(self):
        cutoff = datetime(2027, 1, 1, tzinfo=UTC)
        await storage.delete_envelopes_before(cutoff)
        sql, params = self.connection.execute.await_args.args
        self.assertEqual(sql, "DELETE FROM envelopes WHERE recorded_at < %s;")
        self.assertEqual(params, (cutoff,))

    async def test_database_failures_propagate(self):
        self.connection.execute.side_effect = storage.psycopg.OperationalError("offline")
        with self.assertRaises(storage.psycopg.OperationalError):
            await storage.read_devices()

    def test_timezone_normalization_and_required_configuration(self):
        self.assertEqual(
            storage._as_datetime(datetime(2026, 1, 1)),
            datetime(2026, 1, 1, tzinfo=UTC),
        )
        with patch.dict(os.environ, {"POSTGRES_DSN": ""}):
            with self.assertRaisesRegex(RuntimeError, "POSTGRES_DSN"):
                storage._postgres_dsn()
        with patch.dict(os.environ, {"POSTGRES_DSN": "configured-dsn"}):
            self.assertEqual(storage._postgres_dsn(), "configured-dsn")

    def test_pandas_timestamps_normalize_to_python_datetimes(self):
        for value in (
            storage.Timestamp("2026-01-01"),
            storage.Timestamp("2026-01-01T05:00:00+05:00"),
        ):
            result = storage._as_datetime(value)
            self.assertIs(type(result), datetime)
            self.assertEqual(result, datetime(2026, 1, 1, tzinfo=UTC))


class RouteTests(unittest.TestCase):
    def setUp(self):
        # Startup is tested separately; route tests do not require a live database.
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def test_ingestion_posts_wait_for_postgres_and_keep_null_response(self):
        for path, data in (
            ("environment-sensor", {
                "case": "ENVIRONMENT_SENSOR", "mac_address": "mac",
                "source_date": 1700000000, "temperature": 21,
            }),
            ("heartbeat", {
                "case": "HEARTBEAT", "mac_address": "mac",
                "source_date": "2026-01-01T00:00:00Z", "ip_address": "127.0.0.1",
            }),
        ):
            with self.subTest(path=path), patch.object(
                ingestion, "write_envelope", new_callable=AsyncMock
            ) as write:
                response = self.client.post(f"/data-ingestion/{path}", json=data)
                self.assertEqual(response.status_code, 200)
                self.assertIsNone(response.json())
                write.assert_awaited_once()
                assert write.await_args is not None
                envelope = write.await_args.args[0]
                self.assertEqual(envelope.data.case, data["case"])
                self.assertIsNotNone(envelope.date.tzinfo)

    def test_environment_window_validation_and_defaults(self):
        with patch.object(ingestion, "read_envelopes", AsyncMock(return_value=[])) as read:
            for minimum, maximum in ((-1, 1), (0, -1), (5, 4), (0, 73)):
                response = self.client.get(
                    "/data-ingestion/mac",
                    params={"min_hours_ago": minimum, "max_hours_ago": maximum},
                )
                self.assertEqual(response.status_code, 400)
            read.assert_not_awaited()
            self.assertEqual(self.client.get("/data-ingestion/mac").json(), [])
            read.assert_awaited_once_with(
                "mac", min_hours_ago=0, max_hours_ago=72,
                event_type="ENVIRONMENT_SENSOR",
            )
            response = self.client.get(
                "/data-ingestion/mac", params={"min_hours_ago": 3, "max_hours_ago": 75}
            )
            self.assertEqual(response.status_code, 200)
            response = self.client.get(
                "/data-ingestion/mac", params={"min_hours_ago": 0, "max_hours_ago": 0}
            )
            self.assertEqual(response.status_code, 200)

    def test_all_envelopes_and_delete_routes(self):
        with patch.object(ingestion, "read_envelopes", AsyncMock(return_value=[])) as read:
            self.assertEqual(self.client.get("/data-ingestion/").json(), [])
            read.assert_awaited_once_with()
        with patch.object(ingestion, "delete_envelopes_before", AsyncMock()) as delete:
            self.assertEqual(self.client.delete("/data-ingestion/").status_code, 200)
            delete.assert_awaited_once_with(datetime(2027, 1, 1, tzinfo=UTC))

    def test_device_creation_and_existing_device_error(self):
        with patch.object(devices, "get_device", AsyncMock(return_value=None)), patch.object(
            devices, "write_device", AsyncMock()
        ) as write:
            self.assertEqual(self.client.post("/devices/new").status_code, 200)
            write.assert_awaited_once()
            assert write.await_args is not None
            self.assertEqual(write.await_args.args[0].device_status.case, "UNPROVISIONED")
        with patch.object(devices, "get_device", AsyncMock(return_value=object())), patch.object(
            devices, "write_device", AsyncMock()
        ) as write:
            self.assertEqual(self.client.post("/devices/new").status_code, 400)
            write.assert_not_awaited()

    def test_device_reads_and_provisioning_preserve_identity(self):
        device = devices.Device(
            uuid4(), "sensor", datetime.now(UTC),
            devices.UnprovisionedDevice("UNPROVISIONED"),
        )
        identity = (device.id, device.creation_date)
        home_id = uuid4()
        with patch.object(devices, "get_device", AsyncMock(return_value=device)), patch.object(
            devices, "get_home_object_by_id", AsyncMock(return_value=object())
        ), patch.object(devices, "write_device", AsyncMock()) as write, patch.object(
            devices, "read_devices", AsyncMock(return_value=[device])
        ):
            self.assertEqual(self.client.get("/devices/").json()[0]["id"], str(device.id))
            self.assertEqual(
                self.client.get("/devices/sensor").json()["device_status"],
                {"case": "UNPROVISIONED"},
            )
            response = self.client.post("/devices/sensor/provision", json={
                "mac_address": "mac", "home_object_id": str(home_id),
            })
            self.assertEqual(response.status_code, 200)
            write.assert_awaited_once_with(device)
            self.assertEqual((device.id, device.creation_date), identity)
            self.assertEqual(
                self.client.get("/devices/sensor").json()["device_status"],
                {"case": "PROVISIONED", "mac_address": "mac", "home_object_id": str(home_id)},
            )

    def test_missing_device_and_home_object_errors(self):
        body = {"mac_address": "mac", "home_object_id": str(uuid4())}
        with patch.object(devices, "get_device", AsyncMock(return_value=None)):
            self.assertEqual(self.client.get("/devices/missing").status_code, 404)
            self.assertEqual(
                self.client.post("/devices/missing/provision", json=body).status_code, 404
            )
        with patch.object(devices, "get_device", AsyncMock(return_value=object())), patch.object(
            devices, "get_home_object_by_id", AsyncMock(return_value=None)
        ), patch.object(devices, "write_device", AsyncMock()) as write:
            self.assertEqual(
                self.client.post("/devices/sensor/provision", json=body).status_code, 422
            )
            write.assert_not_awaited()

    def test_failed_write_does_not_report_success(self):
        with patch.object(
            ingestion, "write_envelope", AsyncMock(side_effect=RuntimeError("offline"))
        ):
            with self.assertRaisesRegex(RuntimeError, "offline"):
                self.client.post("/data-ingestion/heartbeat", json={
                    "case": "HEARTBEAT", "mac_address": "mac",
                    "source_date": 1700000000, "ip_address": "127.0.0.1",
                })


class PostgresIntegrationTests(PostgresTestCase):
    async def test_migration_version_is_recorded_once_and_skipped_on_restart(self):
        async with await storage._connect() as connection:
            cursor = await connection.execute("SELECT version FROM versions;")
            self.assertEqual(await cursor.fetchall(), [{"version": 0}])
        with patch.object(storage, "migration_version_0", AsyncMock()) as migration:
            await storage.initialize_database()
            migration.assert_not_awaited()
        async with await storage._connect() as connection:
            cursor = await connection.execute("SELECT version FROM versions;")
            self.assertEqual(await cursor.fetchall(), [{"version": 0}])

    async def test_existing_unversioned_database_is_adopted_without_data_loss(self):
        device = devices.Device(
            uuid4(), "existing sensor", datetime.now(UTC),
            devices.UnprovisionedDevice("UNPROVISIONED"),
        )
        await storage.write_device(device)
        async with await storage._connect() as connection:
            await connection.execute("DROP TABLE versions;")
        await storage.initialize_database()
        self.assertEqual(await storage.read_devices(), [device])
        async with await storage._connect() as connection:
            cursor = await connection.execute("SELECT version FROM versions;")
            self.assertEqual(await cursor.fetchall(), [{"version": 0}])

    async def test_migration_failure_rolls_back_schema_and_version_record(self):
        async with await storage._connect() as connection:
            await connection.execute(
                "DROP TABLE versions, devices, envelopes, groups, home_objects;"
            )
        migrate = storage.migration_version_0

        async def fail_after_migration(connection):
            await migrate(connection)
            raise RuntimeError("migration failed")

        with patch.object(storage, "migration_version_0", fail_after_migration):
            with self.assertRaisesRegex(RuntimeError, "migration failed"):
                await storage.initialize_database()
        async with await storage._connect() as connection:
            cursor = await connection.execute(
                """
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = current_schema();
                """
            )
            self.assertEqual(await cursor.fetchall(), [])
        await storage.initialize_database()
        async with await storage._connect() as connection:
            cursor = await connection.execute("SELECT version FROM versions;")
            self.assertEqual(await cursor.fetchall(), [{"version": 0}])

    async def test_device_provisioning_and_home_object_round_trip(self):
        now = datetime.now(UTC)
        obj = home.HomeObject(
            uuid4(), "room", storage.Timestamp(now), [], {},
            home.Vector3Dto(0, 0, 0), home.QuaternionDto(0, 0, 0, 1),
        )
        await storage.write_home_object(obj)
        self.assertEqual(await storage.read_home_object(obj.id), obj)
        device = devices.Device(
            uuid4(), "sensor", now, devices.UnprovisionedDevice("UNPROVISIONED")
        )
        await storage.write_device(device)
        self.assertEqual(await storage.read_device("sensor"), device)
        device.device_status = devices.ProvisionedDevice("PROVISIONED", "mac", obj.id)
        await storage.write_device(device)
        self.assertEqual(await storage.read_devices(), [device])

    async def test_api_round_trip_against_postgres(self):
        async with app.router.lifespan_context(app), httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            home_id = str(uuid4())
            response = await client.post(f"/home-objects/{home_id}", json={
                "name": "room", "tags": [], "user_data": {},
                "location": {"x": 0, "y": 0, "z": 0},
                "orientation": {"x": 0, "y": 0, "z": 0, "w": 1},
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual((await client.post("/devices/sensor")).status_code, 200)
            original = (await client.get("/devices/sensor")).json()
            self.assertEqual((await client.post("/devices/sensor")).status_code, 400)
            response = await client.post("/devices/sensor/provision", json={
                "mac_address": "mac", "home_object_id": home_id,
            })
            self.assertEqual(response.status_code, 200)
            provisioned = (await client.get("/devices/sensor")).json()
            self.assertEqual(provisioned["id"], original["id"])
            self.assertEqual(provisioned["creation_date"], original["creation_date"])
            self.assertEqual(provisioned["device_status"]["home_object_id"], home_id)
            for path, data in (
                ("environment-sensor", {
                    "case": "ENVIRONMENT_SENSOR", "temperature": 21,
                }),
                ("heartbeat", {"case": "HEARTBEAT", "ip_address": "127.0.0.1"}),
            ):
                response = await client.post(f"/data-ingestion/{path}", json={
                    **data, "mac_address": "mac", "source_date": 1700000000,
                })
                self.assertEqual(response.status_code, 200)
            self.assertEqual(len((await client.get("/data-ingestion/")).json()), 2)
            data = (await client.get("/data-ingestion/mac")).json()
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["data"]["case"], "ENVIRONMENT_SENSOR")
            self.assertEqual(data[0]["data"]["temperature"], 21)

    async def test_envelope_filtering_upsert_and_delete_cutoff(self):
        now = datetime.now(UTC)
        source = datetime(2020, 1, 1, tzinfo=UTC)
        envelopes = [
            models.Envelope(uuid4(), now - timedelta(hours=hours), data)
            for hours, data in (
                (1, models.EnvironmentSensorDataDto("ENVIRONMENT_SENSOR", "mac", source, temperature=21)),
                (74, models.EnvironmentSensorDataDto("ENVIRONMENT_SENSOR", "mac", source)),
                (1, models.HeartbeatDataDto("HEARTBEAT", "mac", "127.0.0.1", source)),
                (1, models.EnvironmentSensorDataDto("ENVIRONMENT_SENSOR", "other", source)),
            )
        ]
        for envelope in envelopes:
            await storage.write_envelope(envelope)
        await storage.write_envelope(envelopes[0])
        self.assertEqual(len(await storage.read_envelopes()), 4)
        result = await storage.read_envelopes(
            "mac", min_hours_ago=0, max_hours_ago=72, event_type="ENVIRONMENT_SENSOR"
        )
        self.assertEqual(result, [envelopes[0]])
        self.assertEqual(len(await storage.read_envelopes("mac")), 3)
        cutoff = datetime(2027, 1, 1, tzinfo=UTC)
        boundary = models.Envelope(uuid4(), cutoff, envelopes[0].data)
        before = models.Envelope(uuid4(), cutoff - timedelta(microseconds=1), envelopes[0].data)
        await storage.write_envelope(boundary)
        await storage.write_envelope(before)
        await storage.delete_envelopes_before(cutoff)
        remaining_ids = {e.id for e in await storage.read_envelopes()}
        self.assertIn(boundary.id, remaining_ids)
        self.assertNotIn(before.id, remaining_ids)
