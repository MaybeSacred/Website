import unittest

from fastapi.testclient import TestClient

from api_support import app


class ApplicationApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def test_root_item_route_and_invalid_item_id(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello World"})
        response = self.client.post("/items/42")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"item_id": 42})
        self.assertEqual(self.client.post("/items/invalid").status_code, 422)
        self.assertEqual(self.client.get("/").json(), {"message": "Hello World"})

    def test_openapi_documents_all_registered_api_operations(self):
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        operations = {
            (method.upper(), path)
            for path, methods in response.json()["paths"].items()
            for method in methods
        }
        self.assertEqual(operations, {
            ("GET", "/"), ("POST", "/items/{item_id}"),
            ("GET", "/libraries/"), ("POST", "/libraries/"),
            ("GET", "/libraries/{library_id}"),
            ("PATCH", "/libraries/{library_id}"),
            ("DELETE", "/libraries/{library_id}"),
            ("GET", "/libraries/{library_id}/documents/"),
            ("POST", "/libraries/{library_id}/documents/"),
            ("GET", "/libraries/{library_id}/documents/{document_id}"),
            ("PATCH", "/libraries/{library_id}/documents/{document_id}"),
            ("DELETE", "/libraries/{library_id}/documents/{document_id}"),
            ("PUT", "/libraries/{library_id}/documents/{document_id}/image"),
            ("GET", "/libraries/{library_id}/documents/{document_id}/image"),
            ("DELETE", "/libraries/{library_id}/documents/{document_id}/image"),
            ("GET", "/home-objects/"), ("POST", "/home-objects/"),
            ("GET", "/home-objects/{id}"), ("POST", "/home-objects/{id}"),
            ("POST", "/home-objects/{id}/update"),
            ("GET", "/groups/"), ("POST", "/groups/"),
            ("GET", "/groups/{id}"), ("POST", "/groups/{id}"),
            ("POST", "/groups/{id}/update"), ("DELETE", "/groups/{id}"),
            ("GET", "/devices/"), ("GET", "/devices/{name}"),
            ("POST", "/devices/{name}"), ("POST", "/devices/{name}/provision"),
            ("GET", "/data-ingestion/"), ("DELETE", "/data-ingestion/"),
            ("GET", "/data-ingestion/{mac_address}"),
            ("POST", "/data-ingestion/environment-sensor"),
            ("POST", "/data-ingestion/heartbeat"),
        })

    def test_cors_preflight_accepts_frontend_and_rejects_other_origins(self):
        for origin in ("http://localhost:8081", "http://127.0.0.1:8081"):
            response = self.client.options("/devices/", headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["access-control-allow-origin"], origin)
            self.assertEqual(response.headers["access-control-allow-credentials"], "true")
        response = self.client.options("/devices/", headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "POST",
        })
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("access-control-allow-origin", response.headers)
        response = self.client.get("/", headers={"Origin": "http://localhost:8081"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["access-control-allow-origin"], "http://localhost:8081"
        )

    def test_unknown_routes_and_unsupported_methods(self):
        self.assertEqual(self.client.get("/unknown").status_code, 404)
        self.assertEqual(self.client.get("/camera/still-image").status_code, 404)
        self.assertEqual(self.client.put("/devices/sensor").status_code, 405)
        self.assertEqual(self.client.get("/items/42").status_code, 405)
        self.assertEqual(self.client.get("/").status_code, 200)
