from uuid import uuid4

from api_support import ApiTestCase


class DevicesApiTests(ApiTestCase):
    async def test_create_list_provision_and_reprovision(self):
        self.assertEqual((await self.client.get("/devices/")).json(), [])
        home_ids = [
            await self.create_home_object("first room"),
            await self.create_home_object("second room"),
        ]
        response = await self.client.post("/devices/sensor")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json())
        original = (await self.client.get("/devices/sensor")).json()
        self.assertEqual(original["device_status"], {"case": "UNPROVISIONED"})
        self.assertEqual(original["name"], "sensor")
        for index, home_id in enumerate(home_ids):
            payload = {"mac_address": f"mac-{index}", "home_object_id": home_id}
            response = await self.client.post("/devices/sensor/provision", json=payload)
            self.assertEqual(response.status_code, 200)
            self.assertIsNone(response.json())
            expected = {
                **original, "device_status": {"case": "PROVISIONED", **payload},
            }
            response = await self.client.get("/devices/sensor")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), expected)
            self.assertEqual((await self.client.get("/devices/")).json(), [expected])

    async def test_duplicate_and_missing_device_errors(self):
        self.assertEqual((await self.client.post("/devices/sensor")).status_code, 200)
        original = (await self.client.get("/devices/sensor")).json()
        response = await self.client.post("/devices/sensor")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Device already exists: sensor"})
        for method, path, payload in (
            ("GET", "/devices/missing", None),
            ("POST", "/devices/missing/provision", {
                "mac_address": "mac", "home_object_id": str(uuid4()),
            }),
        ):
            response = await self.client.request(method, path, json=payload)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json(), {"detail": "Device not found: missing"})
        self.assertEqual((await self.client.get("/devices/")).json(), [original])

    async def test_invalid_provisioning_preserves_existing_status(self):
        home_id = await self.create_home_object()
        self.assertEqual((await self.client.post("/devices/sensor")).status_code, 200)
        payload = {"mac_address": "original", "home_object_id": home_id}
        self.assertEqual(
            (await self.client.post("/devices/sensor/provision", json=payload)).status_code,
            200,
        )
        original = (await self.client.get("/devices/sensor")).json()
        missing_id = str(uuid4())
        for payload in (
            {},
            {"home_object_id": home_id},
            {"mac_address": "mac", "home_object_id": "not-a-uuid"},
            {"mac_address": "mac", "home_object_id": missing_id},
        ):
            with self.subTest(payload=payload):
                response = await self.client.post("/devices/sensor/provision", json=payload)
                self.assertEqual(response.status_code, 422)
                if payload.get("home_object_id") == missing_id:
                    self.assertEqual(response.json(), {
                        "detail": f"Home object not found: {missing_id}",
                    })
                self.assertEqual(
                    (await self.client.get("/devices/sensor")).json(), original
                )

    async def test_device_names_with_quotes_are_literal_lookup_values(self):
        names = ["sensor' OR '1'='1", "other"]
        for name in names:
            response = await self.client.post(f"/devices/{name}")
            self.assertEqual(response.status_code, 200)
        response = await self.client.get(f"/devices/{names[0]}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], names[0])
        self.assertEqual(
            [device["name"] for device in (await self.client.get("/devices/")).json()],
            names,
        )
