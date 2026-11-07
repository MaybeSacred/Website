from uuid import UUID, uuid4

from api_support import ApiTestCase


def group_payload(name: str = "kitchen") -> dict:
    return {
        "name": name,
        "points": [
            {"x": 0, "y": 0, "z": 0},
            {"x": 100, "y": 0, "z": 0},
            {"x": 100, "y": -50.5, "z": 2},
        ],
    }


class GroupsApiTests(ApiTestCase):
    async def create_group(self, name: str = "kitchen") -> str:
        group_id = str(uuid4())
        response = await self.client.post(f"/groups/{group_id}", json=group_payload(name))
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIsNone(response.json())
        return group_id

    async def test_create_generated_id_and_read_back_all_fields(self):
        self.assertEqual((await self.client.get("/groups/")).json(), [])
        payload = group_payload()
        response = await self.client.post("/groups/", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json())
        groups = (await self.client.get("/groups/")).json()
        self.assertEqual(len(groups), 1)
        created = groups[0]
        self.assertEqual(str(UUID(created["id"])), created["id"])
        self.assertIn("creation_date", created)
        for field, value in payload.items():
            self.assertEqual(created[field], value)
        response = await self.client.get(f"/groups/{created['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), created)

    async def test_update_preserves_identity_and_omitted_fields(self):
        group_id = await self.create_group()
        expected = (await self.client.get(f"/groups/{group_id}")).json()
        for changes in (
            {"name": "renamed"},
            {"points": [{"x": -1, "y": 2, "z": 3}]},
            {"points": []},
            {},
            {"name": None, "points": None},
        ):
            with self.subTest(changes=changes):
                response = await self.client.post(f"/groups/{group_id}/update", json=changes)
                self.assertEqual(response.status_code, 200)
                expected.update({k: v for k, v in changes.items() if v is not None})
                self.assertEqual((await self.client.get(f"/groups/{group_id}")).json(), expected)

    async def test_delete_removes_only_that_group(self):
        group_id = await self.create_group("first")
        other_id = await self.create_group("second")
        response = await self.client.delete(f"/groups/{group_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json())
        self.assertEqual((await self.client.get(f"/groups/{group_id}")).status_code, 404)
        self.assertEqual(
            [group["id"] for group in (await self.client.get("/groups/")).json()],
            [other_id],
        )

    async def test_duplicate_and_missing_group_errors_leave_data_unchanged(self):
        group_id = await self.create_group()
        original = (await self.client.get(f"/groups/{group_id}")).json()
        response = await self.client.post(f"/groups/{group_id}", json=group_payload("other"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": f"Group already exists: {group_id}"})
        missing_id = str(uuid4())
        for method, url, payload in (
            ("GET", f"/groups/{missing_id}", None),
            ("POST", f"/groups/{missing_id}/update", {"name": "x"}),
            ("DELETE", f"/groups/{missing_id}", None),
        ):
            response = await self.client.request(method, url, json=payload)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json(), {"detail": f"Group not found: {missing_id}"})
        self.assertEqual((await self.client.get("/groups/")).json(), [original])

    async def test_invalid_bodies_and_ids_do_not_write(self):
        for payload in (
            {},
            {"name": "no points"},
            {**group_payload(), "points": [{"x": 0, "y": 0}]},
            {**group_payload(), "points": {"x": 0, "y": 0, "z": 0}},
        ):
            with self.subTest(payload=payload):
                response = await self.client.post("/groups/", json=payload)
                self.assertEqual(response.status_code, 422)
        self.assertEqual((await self.client.get("/groups/")).json(), [])
        self.assertEqual((await self.client.get("/groups/not-a-uuid")).status_code, 422)
        group_id = await self.create_group()
        original = (await self.client.get(f"/groups/{group_id}")).json()
        response = await self.client.post(
            f"/groups/{group_id}/update", json={"points": [{"x": "bad"}]}
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual((await self.client.get("/groups/")).json(), [original])
