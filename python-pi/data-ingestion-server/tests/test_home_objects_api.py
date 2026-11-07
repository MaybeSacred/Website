from uuid import UUID, uuid4

from api_support import ApiTestCase, home_object_payload


class HomeObjectsApiTests(ApiTestCase):
    async def test_create_generated_id_and_read_back_all_fields(self):
        self.assertEqual((await self.client.get("/home-objects/")).json(), [])
        payload = home_object_payload()
        response = await self.client.post("/home-objects/", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json())
        response = await self.client.get("/home-objects/")
        self.assertEqual(response.status_code, 200)
        objects = response.json()
        self.assertEqual(len(objects), 1)
        created = objects[0]
        self.assertEqual(str(UUID(created["id"])), created["id"])
        self.assertIn("creation_date", created)
        for field, value in payload.items():
            self.assertEqual(created[field], value)
        response = await self.client.get(f"/home-objects/{created['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), created)

    async def test_update_each_field_preserves_identity_and_omitted_fields(self):
        object_id = await self.create_home_object()
        original = (await self.client.get(f"/home-objects/{object_id}")).json()
        expected = dict(original)
        for changes in (
            {"name": "renamed room"},
            {"tags": ["changed"]},
            {"user_data": {"new": "value"}},
            {"location": {"x": -10, "y": 20, "z": 30}},
            {"orientation": {"x": 0, "y": 1, "z": 0, "w": 0}},
        ):
            with self.subTest(changes=changes):
                response = await self.client.post(
                    f"/home-objects/{object_id}/update", json=changes
                )
                self.assertEqual(response.status_code, 200)
                self.assertIsNone(response.json())
                expected.update(changes)
                self.assertEqual(
                    (await self.client.get(f"/home-objects/{object_id}")).json(),
                    expected,
                )
        self.assertEqual((await self.client.get("/home-objects/")).json(), [expected])

    async def test_empty_and_null_updates_are_noops_and_empty_collections_clear(self):
        object_id = await self.create_home_object()
        original = (await self.client.get(f"/home-objects/{object_id}")).json()
        for changes in ({}, dict.fromkeys(home_object_payload(), None)):
            response = await self.client.post(
                f"/home-objects/{object_id}/update", json=changes
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                (await self.client.get(f"/home-objects/{object_id}")).json(), original
            )
        response = await self.client.post(
            f"/home-objects/{object_id}/update",
            json={"tags": [], "user_data": {}},
        )
        self.assertEqual(response.status_code, 200)
        original.update(tags=[], user_data={})
        self.assertEqual(
            (await self.client.get(f"/home-objects/{object_id}")).json(), original
        )

    async def test_duplicate_id_and_missing_object_errors_leave_data_unchanged(self):
        object_id = await self.create_home_object()
        original = (await self.client.get(f"/home-objects/{object_id}")).json()
        response = await self.client.post(
            f"/home-objects/{object_id}", json=home_object_payload("replacement")
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            "detail": f"Home object already exists: {object_id}",
        })
        missing_id = str(uuid4())
        for method, url, payload in (
            ("GET", f"/home-objects/{missing_id}", None),
            ("POST", f"/home-objects/{missing_id}/update", {"tags": []}),
        ):
            response = await self.client.request(method, url, json=payload)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json(), {
                "detail": f"Home object not found: {missing_id}",
            })
        self.assertEqual((await self.client.get("/home-objects/")).json(), [original])

    async def test_invalid_create_and_update_bodies_do_not_write(self):
        for payload in (
            {},
            {**home_object_payload(), "location": {"x": 0, "y": 0}},
            {**home_object_payload(), "orientation": {"w": "invalid"}},
            {**home_object_payload(), "user_data": []},
        ):
            with self.subTest(payload=payload):
                response = await self.client.post("/home-objects/", json=payload)
                self.assertEqual(response.status_code, 422)
                self.assertIn("detail", response.json())
        self.assertEqual((await self.client.get("/home-objects/")).json(), [])
        object_id = await self.create_home_object()
        original = (await self.client.get(f"/home-objects/{object_id}")).json()
        for payload in ({"location": {}}, {"tags": 123}, {"orientation": {"w": 1}}):
            response = await self.client.post(
                f"/home-objects/{object_id}/update", json=payload
            )
            self.assertEqual(response.status_code, 422)
        self.assertEqual((await self.client.get("/home-objects/")).json(), [original])
