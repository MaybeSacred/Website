import importlib
import unittest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from api_support import PACKAGE, app

groups = importlib.import_module(f"{PACKAGE}.routers.groups")


class GroupValidationTests(unittest.TestCase):
    def test_polygon_validation_on_create_and_update(self):
        client = TestClient(app)
        self.addCleanup(client.close)
        invalid = [
            [(0, 0), (10, 10), (0, 10), (10, 0)],
            [(0, 0), (10, 0), (5, 0), (5, 10)],
            [(0, 0), (10, 0), (10, 10), (0, 0), (0, 10)],
            [(0, 0), (10, 0), (10, 0), (0, 10)],
        ]
        with patch.object(groups, "get_group_by_id", AsyncMock()) as read, \
                patch.object(groups, "write_group", AsyncMock()) as write:
            for coordinates in invalid:
                points = [{"x": x, "y": y, "z": 0} for x, y in coordinates]
                for path, payload in (
                    ("/groups/", {"name": "Invalid", "points": points}),
                    (f"/groups/{uuid4()}", {"name": "Invalid", "points": points}),
                    (f"/groups/{uuid4()}/update", {"points": points}),
                ):
                    with self.subTest(points=points, path=path):
                        response = client.post(path, json=payload)
                        self.assertEqual(response.status_code, 422, response.text)
                        self.assertIn("self-intersect", response.text)
            read.assert_not_awaited()
            write.assert_not_awaited()

    def test_valid_convex_concave_and_legacy_empty_points(self):
        domain = importlib.import_module(f"{PACKAGE}.domain.group")
        vector = importlib.import_module(f"{PACKAGE}.domain.home_object").Vector3Dto
        for coordinates in (
            [(0, 0), (10, 0), (10, 10), (0, 10)],
            [(0, 0), (10, 0), (5, 5), (10, 10), (0, 10)],
            [],
        ):
            points = [vector(x, y, 0) for x, y in coordinates]
            domain.GroupCreationDto("Valid", points)
            domain.GroupUpdateDto(points=points)
