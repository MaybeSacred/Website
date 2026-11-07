from datetime import UTC, datetime, timedelta
from uuid import UUID

from api_support import ApiTestCase, storage


def sensor_payload(mac_address: str = "mac") -> dict:
    return {
        "case": "ENVIRONMENT_SENSOR", "mac_address": mac_address,
        "source_date": 1700000000,
        "cpu_temperature": 40, "temperature": 21, "distance": 12,
        "humidity": 50, "lux": 100, "pressure": 1013, "uv": 2,
        "gas": 3, "water_depth_raw": 4, "moisture_percent": 60,
    }


class IngestionApiTests(ApiTestCase):
    async def test_sensor_and_heartbeat_payloads_round_trip(self):
        self.assertEqual((await self.client.get("/data-ingestion/")).json(), [])
        sensor = sensor_payload()
        heartbeat = {
            "case": "HEARTBEAT", "mac_address": "mac",
            "source_date": "2026-01-01T05:00:00+05:00", "ip_address": "127.0.0.1",
        }
        for path, payload in (("environment-sensor", sensor), ("heartbeat", heartbeat)):
            response = await self.client.post(f"/data-ingestion/{path}", json=payload)
            self.assertEqual(response.status_code, 200)
            self.assertIsNone(response.json())
        response = await self.client.get("/data-ingestion/")
        self.assertEqual(response.status_code, 200)
        envelopes = response.json()
        self.assertEqual(len(envelopes), 2)
        self.assertNotEqual(envelopes[0]["id"], envelopes[1]["id"])
        for envelope, payload in zip(envelopes, (sensor, heartbeat), strict=True):
            self.assertEqual(str(UUID(envelope["id"])), envelope["id"])
            self.assertIsNotNone(datetime.fromisoformat(envelope["date"]).tzinfo)
            for field, value in payload.items():
                if field != "source_date":
                    self.assertEqual(envelope["data"][field], value)
        self.assertEqual(
            datetime.fromisoformat(envelopes[0]["data"]["source_date"]),
            datetime.fromtimestamp(sensor["source_date"], tz=UTC),
        )
        self.assertEqual(
            datetime.fromisoformat(envelopes[1]["data"]["source_date"]),
            datetime(2026, 1, 1, tzinfo=UTC),
        )
        self.assertEqual(
            (await self.client.get("/data-ingestion/mac")).json(), [envelopes[0]]
        )

    async def test_optional_sensor_fields_are_null_and_zero_values_survive(self):
        for payload in (
            {"case": "ENVIRONMENT_SENSOR", "mac_address": "mac", "source_date": 0},
            {**sensor_payload(), **{key: 0 for key in sensor_payload() if key not in (
                "case", "mac_address", "source_date",
            )}},
        ):
            response = await self.client.post("/data-ingestion/environment-sensor", json=payload)
            self.assertEqual(response.status_code, 200)
        rows = (await self.client.get("/data-ingestion/")).json()
        self.assertEqual(len(rows), 2)
        for field in sensor_payload().keys() - {"case", "mac_address", "source_date"}:
            self.assertIsNone(rows[0]["data"][field])
            self.assertEqual(rows[1]["data"][field], 0)
        self.assertEqual(
            datetime.fromisoformat(rows[0]["data"]["source_date"]),
            datetime(1970, 1, 1, tzinfo=UTC),
        )

    async def test_recording_time_mac_and_event_filters(self):
        for mac in ("mac", "other", "mac' OR true --"):
            response = await self.client.post(
                "/data-ingestion/environment-sensor", json=sensor_payload(mac)
            )
            self.assertEqual(response.status_code, 200)
        response = await self.client.post("/data-ingestion/heartbeat", json={
            "case": "HEARTBEAT", "mac_address": "mac",
            "source_date": 1700000000, "ip_address": "127.0.0.1",
        })
        self.assertEqual(response.status_code, 200)
        rows = (await self.client.get("/data-ingestion/")).json()
        # Age fixture records without changing their source timestamps.
        async with await storage._connect() as connection:
            for row, age in zip(rows, (2, 1, 1, 1), strict=True):
                await connection.execute(
                    "UPDATE envelopes SET recorded_at = now() - %s WHERE id = %s",
                    (timedelta(hours=age), UUID(row["id"])),
                )
        response = await self.client.get("/data-ingestion/mac", params={
            "min_hours_ago": 1, "max_hours_ago": 3,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["id"] for row in response.json()], [rows[0]["id"]])
        self.assertEqual(
            (await self.client.get("/data-ingestion/mac", params={
                "min_hours_ago": 3, "max_hours_ago": 75,
            })).json(), [],
        )
        self.assertEqual((await self.client.get("/data-ingestion/missing")).json(), [])
        response = await self.client.get("/data-ingestion/mac' OR true --")
        self.assertEqual([row["id"] for row in response.json()], [rows[2]["id"]])
        all_rows = (await self.client.get("/data-ingestion/")).json()
        self.assertEqual(len(all_rows), 4)
        self.assertEqual(all_rows[0]["id"], rows[0]["id"])

    async def test_invalid_time_windows_do_not_modify_data(self):
        self.assertEqual((await self.client.post(
            "/data-ingestion/environment-sensor", json=sensor_payload()
        )).status_code, 200)
        original = (await self.client.get("/data-ingestion/")).json()
        for minimum, maximum, status in (
            (-1, 1, 400), (0, -1, 400), (5, 4, 400), (0, 73, 400),
            ("invalid", 72, 422), (0, "invalid", 422),
        ):
            with self.subTest(minimum=minimum, maximum=maximum):
                response = await self.client.get("/data-ingestion/mac", params={
                    "min_hours_ago": minimum, "max_hours_ago": maximum,
                })
                self.assertEqual(response.status_code, status)
                if status == 400:
                    self.assertEqual(response.json(), {
                        "detail": f"Invalid time range: {minimum} - {maximum}",
                    })
        self.assertEqual((await self.client.get("/data-ingestion/")).json(), original)

    async def test_invalid_ingestion_bodies_do_not_write(self):
        for path, payload in (
            ("environment-sensor", {}),
            ("environment-sensor", {**sensor_payload(), "case": "HEARTBEAT"}),
            ("environment-sensor", {**sensor_payload(), "source_date": "bad-date"}),
            ("environment-sensor", {**sensor_payload(), "temperature": "hot"}),
            ("heartbeat", {"case": "HEARTBEAT", "mac_address": "mac", "source_date": 0}),
            ("heartbeat", {
                "case": "ENVIRONMENT_SENSOR", "mac_address": "mac",
                "source_date": 0, "ip_address": "127.0.0.1",
            }),
        ):
            with self.subTest(path=path, payload=payload):
                response = await self.client.post(f"/data-ingestion/{path}", json=payload)
                self.assertEqual(response.status_code, 422)
                self.assertIn("detail", response.json())
        self.assertEqual((await self.client.get("/data-ingestion/")).json(), [])

    async def test_delete_strict_cutoff_preserves_devices_and_home_objects(self):
        home_id = await self.create_home_object()
        self.assertEqual((await self.client.post("/devices/sensor")).status_code, 200)
        for index in range(3):
            response = await self.client.post(
                "/data-ingestion/environment-sensor", json=sensor_payload(f"mac-{index}")
            )
            self.assertEqual(response.status_code, 200)
        rows = (await self.client.get("/data-ingestion/")).json()
        cutoff = datetime(2027, 1, 1, tzinfo=UTC)
        async with await storage._connect() as connection:
            for row, date in zip(rows, (
                cutoff - timedelta(microseconds=1), cutoff, cutoff + timedelta(microseconds=1),
            ), strict=True):
                await connection.execute(
                    "UPDATE envelopes SET recorded_at = %s WHERE id = %s",
                    (date, UUID(row["id"])),
                )
        for _ in range(2):
            response = await self.client.delete("/data-ingestion/")
            self.assertEqual(response.status_code, 200)
            self.assertIsNone(response.json())
            self.assertEqual(
                [row["id"] for row in (await self.client.get("/data-ingestion/")).json()],
                [row["id"] for row in rows[1:]],
            )
        self.assertEqual((await self.client.get(f"/home-objects/{home_id}")).status_code, 200)
        self.assertEqual((await self.client.get("/devices/sensor")).status_code, 200)
