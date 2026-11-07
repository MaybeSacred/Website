from io import BytesIO
from datetime import UTC, datetime
import unittest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient
from PIL import Image

from api_support import ApiTestCase, app, library_storage


class LibraryEndpointTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(self.client.close)
        self.library = {
            "id": uuid4(), "name": "Library", "creation_date": datetime.now(UTC),
        }
        self.document = {
            "id": uuid4(), "library_id": self.library["id"], "name": "Document",
            "creation_date": datetime.now(UTC), "description": None,
            "ocr_text": None, "has_image": False,
        }
        self.library_url = f"/libraries/{self.library['id']}"
        self.document_url = self.library_url + f"/documents/{self.document['id']}"

    def mock_storage(self, name, result):
        if name in ("read_library", "create_library", "update_library") and result is not None:
            result = library_storage.Library.model_validate(result)
        elif name == "read_libraries" and result is not None:
            result = [library_storage.Library.model_validate(row) for row in result]
        elif name == "read_documents" and result is not None:
            result = [library_storage.Document.model_validate(row) for row in result]
        elif name in ("read_document", "create_document", "update_document",
                      "write_document_image") and result is not None:
            result = library_storage.Document.model_validate(result)
        mocked = AsyncMock(return_value=result)
        patcher = patch.object(library_storage, name, mocked)
        patcher.start()
        self.addCleanup(patcher.stop)
        return mocked

    def test_library_routes_and_nested_document_serialization(self):
        self.mock_storage("read_libraries", [self.library])
        create = self.mock_storage("create_library", self.library)
        self.mock_storage("read_library", self.library)
        self.mock_storage("read_documents", [self.document])
        update = self.mock_storage("update_library", self.library)
        delete = self.mock_storage("delete_library", True)
        self.assertEqual(self.client.get("/libraries/").status_code, 200)
        self.assertEqual(self.client.post("/libraries/", json={"name": "Library"}).status_code, 201)
        assert create.await_args is not None
        self.assertEqual(create.await_args.args[0].name, "Library")
        response = self.client.get(self.library_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["documents"][0]["id"], str(self.document["id"]))
        self.assertEqual(self.client.patch(self.library_url, json={"name": "New"}).status_code, 200)
        assert update.await_args is not None
        self.assertEqual(update.await_args.args[1].name, "New")
        self.assertEqual(self.client.delete(self.library_url).status_code, 204)
        delete.assert_awaited_once_with(self.library["id"])

    def test_document_routes_and_nullable_updates(self):
        self.mock_storage("read_library", self.library)
        self.mock_storage("read_documents", [self.document])
        self.mock_storage("create_document", self.document)
        self.mock_storage("read_document", self.document)
        update = self.mock_storage("update_document", self.document)
        self.mock_storage("delete_document", True)
        collection = self.library_url + "/documents/"
        self.assertEqual(self.client.get(collection).status_code, 200)
        self.assertEqual(self.client.post(collection, json={"name": "Document"}).status_code, 201)
        self.assertEqual(self.client.get(self.document_url).status_code, 200)
        self.assertEqual(
            self.client.patch(self.document_url, json={"description": None}).status_code, 200
        )
        assert update.await_args is not None
        self.assertEqual(update.await_args.args[2].model_dump(exclude_unset=True), {"description": None})
        self.assertEqual(self.client.delete(self.document_url).status_code, 204)

    def test_invalid_metadata_is_rejected_before_storage(self):
        create = self.mock_storage("create_document", self.document)
        update = self.mock_storage("update_document", self.document)
        for payload in ({}, {"name": None}, {"name": " "}, {"name": "X", "extra": 1}):
            self.assertEqual(
                self.client.post(self.library_url + "/documents/", json=payload).status_code, 422
            )
        for payload in ({"name": None}, {"name": ""}, {"description": 42}):
            self.assertEqual(self.client.patch(self.document_url, json=payload).status_code, 422)
        create.assert_not_awaited()
        update.assert_not_awaited()

    def test_missing_resources_are_404(self):
        for name in ("read_library", "read_document", "create_document", "update_document",
                     "write_document_image", "read_document_image"):
            self.mock_storage(name, None)
        self.mock_storage("delete_library", False)
        self.mock_storage("delete_document", False)
        for method, url, payload in (
            ("GET", self.library_url, None),
            ("DELETE", self.library_url, None),
            ("GET", self.library_url + "/documents/", None),
            ("POST", self.library_url + "/documents/", {"name": "X"}),
            ("GET", self.document_url, None),
            ("PATCH", self.document_url, {"ocr_text": None}),
            ("DELETE", self.document_url, None),
            ("GET", self.document_url + "/image", None),
            ("DELETE", self.document_url + "/image", None),
        ):
            self.assertEqual(self.client.request(method, url, json=payload).status_code, 404)

    def test_image_endpoints_validate_and_preserve_original_bytes(self):
        self.mock_storage("read_document", self.document)
        write = self.mock_storage("write_document_image", {**self.document, "has_image": True})
        with BytesIO() as stream, Image.new("RGB", (20, 20), "white") as image:
            image.save(stream, format="PNG")
            payload = stream.getvalue()
        url = self.document_url + "/image"
        response = self.client.put(url, files={"image": ("image.png", payload, "text/plain")})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(response.json()["has_image"])
        write.assert_awaited_once_with(
            self.library["id"], self.document["id"], payload, "image/png"
        )
        self.mock_storage("read_document_image", (payload, "image/png"))
        response = self.client.get(url)
        self.assertEqual(response.content, payload)
        self.assertEqual(response.headers["content-type"], "image/png")
        write.reset_mock()
        for invalid, expected in ((b"", 422), (b"not an image", 422),
                                  (b"x" * (10 * 1024 * 1024 + 1), 413)):
            response = self.client.put(url, files={"image": ("bad", invalid)})
            self.assertEqual(response.status_code, expected, response.text)
        write.assert_not_awaited()
        self.assertEqual(self.client.put(url).status_code, 422)
        self.assertEqual(self.client.delete(url).status_code, 204)
        write.assert_awaited_once_with(self.library["id"], self.document["id"], None, None)


class LibraryStorageTests(unittest.IsolatedAsyncioTestCase):
    async def test_partial_update_uses_bound_parameters_and_library_scope(self):
        connection = AsyncMock()
        cursor = AsyncMock()
        cursor.fetchone.return_value = None
        connection.execute.return_value = cursor
        connection.__aenter__.return_value = connection
        library_id, document_id = uuid4(), uuid4()
        data = library_storage.DocumentUpdateDto(description=None, ocr_text="' OR true --")
        with patch.object(library_storage, "_connect", AsyncMock(return_value=connection)):
            result = await library_storage.update_document(library_id, document_id, data)
        self.assertIsNone(result)
        query, params = connection.execute.await_args.args
        statement = query.as_string()
        self.assertIn('"description" = %s', statement)
        self.assertIn('"ocr_text" = %s', statement)
        self.assertNotIn('"name" =', statement)
        self.assertIn("WHERE library_id = %s AND id = %s", statement)
        self.assertNotIn("' OR true --", statement)
        self.assertEqual(params, (None, "' OR true --", library_id, document_id))


class LibrariesApiTests(ApiTestCase):
    async def create_library(self, name="Library"):
        response = await self.client.post("/libraries/", json={"name": name})
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    async def create_document(self, library_id, **fields):
        response = await self.client.post(
            f"/libraries/{library_id}/documents/", json={"name": "Document", **fields}
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    async def test_library_crud_and_cascading_delete(self):
        first = await self.create_library()
        second = await self.create_library("Other")
        document = await self.create_document(first["id"])
        url = f"/libraries/{first['id']}"
        self.assertEqual(
            (await self.client.get(url)).json(), {**first, "documents": [document]}
        )
        response = await self.client.patch(url, json={"name": "Renamed"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {**first, "name": "Renamed"})
        response = await self.client.patch(url, json={})
        self.assertEqual(response.json()["name"], "Renamed")
        self.assertEqual((await self.client.delete(url)).status_code, 204)
        self.assertEqual((await self.client.get(url)).status_code, 404)
        self.assertEqual((await self.client.delete(url)).status_code, 404)
        self.assertEqual((await self.client.get("/libraries/")).json(), [second])
        async with await library_storage._connect() as connection:
            cursor = await connection.execute(
                "SELECT count(*) AS count FROM documents WHERE library_id = %s", (first["id"],)
            )
            row = await cursor.fetchone()
            self.assertIsNotNone(row)
            assert row is not None
            self.assertEqual(row["count"], 0)

    async def test_document_crud_optional_fields_and_library_isolation(self):
        library = await self.create_library()
        other = await self.create_library("Other")
        document = await self.create_document(library["id"])
        url = f"/libraries/{library['id']}/documents/{document['id']}"
        self.assertIsNone(document["description"])
        self.assertIsNone(document["ocr_text"])
        self.assertFalse(document["has_image"])
        expected = document.copy()
        for changes in (
            {"description": "Notes", "ocr_text": "Recognized text"},
            {"name": "Renamed"},
            {"description": None},
            {"ocr_text": ""},
            {"ocr_text": None},
            {},
        ):
            response = await self.client.patch(url, json=changes)
            self.assertEqual(response.status_code, 200, response.text)
            expected.update(changes)
            self.assertEqual(response.json(), expected)
            self.assertEqual((await self.client.get(url)).json(), expected)
        self.assertEqual(
            (await self.client.get(f"/libraries/{library['id']}/documents/")).json(),
            [expected],
        )
        wrong_url = f"/libraries/{other['id']}/documents/{document['id']}"
        for method, payload in (("GET", None), ("PATCH", {"name": "Wrong"}), ("DELETE", None)):
            response = await self.client.request(method, wrong_url, json=payload)
            self.assertEqual(response.status_code, 404)
        self.assertEqual((await self.client.get(url)).json(), expected)
        self.assertEqual((await self.client.delete(url)).status_code, 204)
        self.assertEqual((await self.client.get(url)).status_code, 404)

    async def test_image_upload_replace_download_delete_and_invalid_input(self):
        library = await self.create_library()
        document = await self.create_document(library["id"], ocr_text="Keep this")
        url = f"/libraries/{library['id']}/documents/{document['id']}"
        image_url = url + "/image"
        self.assertEqual((await self.client.get(image_url)).status_code, 404)
        for format, content_type in (("PNG", "image/png"), ("JPEG", "image/jpeg")):
            with BytesIO() as stream, Image.new("RGB", (20, 10), "white") as image:
                image.save(stream, format=format)
                payload = stream.getvalue()
            response = await self.client.put(
                image_url, files={"image": ("upload", payload, "application/octet-stream")}
            )
            self.assertEqual(response.status_code, 200, response.text)
            self.assertTrue(response.json()["has_image"])
            self.assertEqual(response.json()["ocr_text"], "Keep this")
            response = await self.client.get(image_url)
            self.assertEqual(response.content, payload)
            self.assertEqual(response.headers["content-type"], content_type)
        saved_payload = payload
        for payload, status in ((b"", 422), (b"invalid", 422), (b"x" * (10 * 1024 * 1024 + 1), 413)):
            response = await self.client.put(image_url, files={"image": ("bad", payload)})
            self.assertEqual(response.status_code, status, response.text)
        self.assertEqual((await self.client.get(image_url)).content, saved_payload)

        self.assertEqual((await self.client.delete(image_url)).status_code, 204)
        self.assertEqual((await self.client.get(image_url)).status_code, 404)
        self.assertFalse((await self.client.get(url)).json()["has_image"])
        self.assertEqual((await self.client.get(url)).json()["ocr_text"], "Keep this")

    async def test_missing_resources_and_validation_do_not_write(self):
        missing = str(uuid4())
        for method, url, payload in (
            ("GET", f"/libraries/{missing}", None),
            ("PATCH", f"/libraries/{missing}", {"name": "X"}),
            ("DELETE", f"/libraries/{missing}", None),
            ("GET", f"/libraries/{missing}/documents/", None),
            ("POST", f"/libraries/{missing}/documents/", {"name": "X"}),
        ):
            response = await self.client.request(method, url, json=payload)
            self.assertEqual(response.status_code, 404)
        for payload in ({}, {"name": None}, {"name": " "}, {"name": "X", "unknown": 1}):
            self.assertEqual(
                (await self.client.post("/libraries/", json=payload)).status_code, 422
            )
        library = await self.create_library()
        url = f"/libraries/{library['id']}"
        for payload in ({"name": None}, {"name": ""}):
            self.assertEqual((await self.client.patch(url, json=payload)).status_code, 422)
        for payload in ({}, {"name": None}, {"name": ""}, {"name": "X", "description": 123}):
            self.assertEqual(
                (await self.client.post(url + "/documents/", json=payload)).status_code, 422
            )
        self.assertEqual((await self.client.get(url)).json()["documents"], [])
        self.assertEqual((await self.client.get("/libraries/invalid")).status_code, 422)
