from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from uuid import UUID

import psycopg
from pandas import Timestamp
from psycopg.rows import dict_row
from psycopg import sql
from psycopg.types.json import Jsonb

from .domain.device import Device, ProvisionedDevice, UnprovisionedDevice
from .domain.group import Group
from .domain.home_object import HomeObject, QuaternionDto, Vector3Dto
from .domain.sensor_data import Envelope, EnvironmentSensorDataDto, HeartbeatDataDto


def _postgres_dsn() -> str:
    dsn = os.getenv("POSTGRES_DSN")
    if not dsn:
        raise RuntimeError("POSTGRES_DSN must be set to enable PostgreSQL storage")
    return dsn


async def _connect() -> psycopg.AsyncConnection[dict[str, Any]]:
    return await psycopg.AsyncConnection[dict[str, Any]].connect(
        _postgres_dsn(), row_factory=dict_row
    )


def _as_datetime(value: datetime | int | float) -> datetime:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=UTC)
    normalized = value.to_pydatetime() if isinstance(value, Timestamp) else value
    if not isinstance(normalized, datetime):
        raise ValueError("A valid datetime is required")
    return normalized.replace(tzinfo=UTC) if normalized.tzinfo is None else normalized


async def initialize_database() -> None:
    async with await _connect() as connection:
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS versions (
                version INTEGER PRIMARY KEY
            );
            """
        )
        await connection.execute("LOCK TABLE versions IN EXCLUSIVE MODE;")
        cursor = await connection.execute("SELECT version FROM versions;")
        applied_versions = {row["version"] for row in await cursor.fetchall()}
        for version, migration in enumerate((migration_version_0, migration_version_1)):
            if version not in applied_versions:
                await migration(connection)


async def migration_version_0(connection: psycopg.AsyncConnection[dict[str, Any]]) -> None:
    await connection.execute(
        """
        CREATE TABLE IF NOT EXISTS home_objects (
            id UUID PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            creation_date TIMESTAMPTZ NOT NULL,
            tags JSONB NOT NULL,
            user_data JSONB NOT NULL,
            location_x DOUBLE PRECISION NOT NULL,
            location_y DOUBLE PRECISION NOT NULL,
            location_z DOUBLE PRECISION NOT NULL,
            orientation_x DOUBLE PRECISION NOT NULL,
            orientation_y DOUBLE PRECISION NOT NULL,
            orientation_z DOUBLE PRECISION NOT NULL,
            orientation_w DOUBLE PRECISION NOT NULL
        );
        """
    )
    await connection.execute(
        """
        CREATE TABLE IF NOT EXISTS devices (
            id UUID PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            creation_date TIMESTAMPTZ NOT NULL,
            status TEXT NOT NULL,
            mac_address TEXT,
            home_object_id UUID REFERENCES home_objects(id),
            CHECK (
                (status = 'UNPROVISIONED'
                    AND mac_address IS NULL AND home_object_id IS NULL)
                OR (status = 'PROVISIONED'
                    AND mac_address IS NOT NULL AND home_object_id IS NOT NULL)
            )
        );
        """
    )
    await connection.execute(
        """
        CREATE TABLE IF NOT EXISTS groups (
            id UUID PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            creation_date TIMESTAMPTZ NOT NULL,
            points JSONB NOT NULL
        );
        """
    )
    await connection.execute(
        """
        CREATE TABLE IF NOT EXISTS envelopes (
            id UUID PRIMARY KEY,
            recorded_at TIMESTAMPTZ NOT NULL,
            event_type TEXT NOT NULL,
            mac_address TEXT NOT NULL,
            ip_address TEXT,
            source_date TIMESTAMPTZ NOT NULL,
            cpu_temperature DOUBLE PRECISION,
            temperature DOUBLE PRECISION,
            distance DOUBLE PRECISION,
            humidity DOUBLE PRECISION,
            lux DOUBLE PRECISION,
            pressure DOUBLE PRECISION,
            uv INTEGER,
            gas DOUBLE PRECISION,
            water_depth_raw INTEGER,
            moisture_percent DOUBLE PRECISION
        );
        """
    )
    await connection.execute(
        """
        CREATE INDEX IF NOT EXISTS envelopes_device_event_time_idx
        ON envelopes (mac_address, event_type, recorded_at);
        """
    )
    await connection.execute("INSERT INTO versions (version) VALUES (0);")


async def migration_version_1(connection: psycopg.AsyncConnection[dict[str, Any]]) -> None:
    await connection.execute(
        """
        CREATE TABLE libraries (
            id UUID PRIMARY KEY,
            name TEXT NOT NULL CHECK (length(btrim(name)) > 0),
            creation_date TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE TABLE documents (
            id UUID PRIMARY KEY,
            library_id UUID NOT NULL REFERENCES libraries(id) ON DELETE CASCADE,
            name TEXT NOT NULL CHECK (length(btrim(name)) > 0),
            creation_date TIMESTAMPTZ NOT NULL DEFAULT now(),
            description TEXT,
            ocr_text TEXT,
            image BYTEA,
            image_media_type TEXT,
            CHECK ((image IS NULL) = (image_media_type IS NULL))
        );
        CREATE INDEX documents_library_idx ON documents (library_id, creation_date, id);
        """
    )
    await connection.execute("INSERT INTO versions (version) VALUES (1);")


async def write_home_object(home_object: HomeObject) -> None:
    async with await _connect() as connection:
        await connection.execute(
            """
            INSERT INTO home_objects (
                id, name, creation_date, tags, user_data,
                location_x, location_y, location_z,
                orientation_x, orientation_y, orientation_z, orientation_w
            ) VALUES (
                %(id)s, %(name)s, %(creation_date)s, %(tags)s, %(user_data)s,
                %(location_x)s, %(location_y)s, %(location_z)s,
                %(orientation_x)s, %(orientation_y)s, %(orientation_z)s,
                %(orientation_w)s
            )
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                creation_date = EXCLUDED.creation_date,
                tags = EXCLUDED.tags,
                user_data = EXCLUDED.user_data,
                location_x = EXCLUDED.location_x,
                location_y = EXCLUDED.location_y,
                location_z = EXCLUDED.location_z,
                orientation_x = EXCLUDED.orientation_x,
                orientation_y = EXCLUDED.orientation_y,
                orientation_z = EXCLUDED.orientation_z,
                orientation_w = EXCLUDED.orientation_w;
            """,
            {
                "id": home_object.id,
                "name": home_object.name,
                "creation_date": _as_datetime(home_object.creation_date),
                "tags": Jsonb(home_object.tags),
                "user_data": Jsonb(home_object.user_data),
                "location_x": home_object.location.x,
                "location_y": home_object.location.y,
                "location_z": home_object.location.z,
                "orientation_x": home_object.orientation.x,
                "orientation_y": home_object.orientation.y,
                "orientation_z": home_object.orientation.z,
                "orientation_w": home_object.orientation.w,
            },
        )


def map_row_to_home_object(row: dict[str, Any]) -> HomeObject:
    creation_date = Timestamp(row["creation_date"])
    if not isinstance(creation_date, Timestamp):
        raise ValueError("A valid home object creation date is required")
    return HomeObject(
        id=row["id"],
        name=row["name"],
        creation_date=creation_date,
        tags=row["tags"],
        user_data=row["user_data"],
        location=Vector3Dto(
            row["location_x"], row["location_y"], row["location_z"]
        ),
        orientation=QuaternionDto(
            row["orientation_x"],
            row["orientation_y"],
            row["orientation_z"],
            row["orientation_w"],
        ),
    )


async def read_home_objects() -> list[HomeObject]:
    async with await _connect() as connection:
        cursor = await connection.execute(
            "SELECT * FROM home_objects ORDER BY creation_date, id;"
        )
        rows = await cursor.fetchall()
    return [map_row_to_home_object(row) for row in rows]


async def read_home_object(id: UUID) -> HomeObject | None:
    async with await _connect() as connection:
        cursor = await connection.execute(
            "SELECT * FROM home_objects WHERE id = %(id)s;",
            {"id": id},
        )
        row = await cursor.fetchone()
    return map_row_to_home_object(row) if row is not None else None


async def write_group(group: Group) -> None:
    async with await _connect() as connection:
        await connection.execute(
            """
            INSERT INTO groups (id, name, creation_date, points)
            VALUES (%(id)s, %(name)s, %(creation_date)s, %(points)s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                creation_date = EXCLUDED.creation_date,
                points = EXCLUDED.points;
            """,
            {
                "id": group.id,
                "name": group.name,
                "creation_date": _as_datetime(group.creation_date),
                "points": Jsonb([
                    {"x": point.x, "y": point.y, "z": point.z}
                    for point in group.points
                ]),
            },
        )


def map_row_to_group(row: dict[str, Any]) -> Group:
    creation_date = Timestamp(row["creation_date"])
    if not isinstance(creation_date, Timestamp):
        raise ValueError("A valid group creation date is required")
    return Group(
        id=row["id"],
        name=row["name"],
        creation_date=creation_date,
        points=[
            Vector3Dto(point["x"], point["y"], point["z"])
            for point in row["points"]
        ],
    )


async def read_groups() -> list[Group]:
    async with await _connect() as connection:
        cursor = await connection.execute(
            "SELECT * FROM groups ORDER BY creation_date, id;"
        )
        rows = await cursor.fetchall()
    return [map_row_to_group(row) for row in rows]


async def read_group(id: UUID) -> Group | None:
    async with await _connect() as connection:
        cursor = await connection.execute(
            "SELECT * FROM groups WHERE id = %(id)s;",
            {"id": id},
        )
        row = await cursor.fetchone()
    return map_row_to_group(row) if row is not None else None


async def delete_group(id: UUID) -> bool:
    async with await _connect() as connection:
        cursor = await connection.execute(
            "DELETE FROM groups WHERE id = %(id)s;",
            {"id": id},
        )
    return cursor.rowcount > 0


async def write_device(device: Device) -> None:
    status = device.device_status
    async with await _connect() as connection:
        await connection.execute(
            """
            INSERT INTO devices (
                id, name, creation_date, status, mac_address, home_object_id
            ) VALUES (
                %(id)s, %(name)s, %(creation_date)s, %(status)s,
                %(mac_address)s, %(home_object_id)s
            )
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                status = EXCLUDED.status,
                mac_address = EXCLUDED.mac_address,
                home_object_id = EXCLUDED.home_object_id;
            """,
            {
                "id": device.id,
                "name": device.name,
                "creation_date": _as_datetime(device.creation_date),
                "status": status.case,
                "mac_address": status.mac_address if isinstance(status, ProvisionedDevice) else None,
                "home_object_id": status.home_object_id if isinstance(status, ProvisionedDevice) else None,
            },
        )


def map_row_to_device(row: dict[str, Any]) -> Device:
    status: ProvisionedDevice | UnprovisionedDevice
    if row["status"] == "PROVISIONED":
        status = ProvisionedDevice(
            'PROVISIONED', row["mac_address"], row["home_object_id"]
        )
    elif row["status"] == "UNPROVISIONED":
        status = UnprovisionedDevice('UNPROVISIONED')
    else:
        raise ValueError(f"Unknown device status: {row['status']}")
    return Device(row["id"], row["name"], row["creation_date"], status)


async def read_devices() -> list[Device]:
    async with await _connect() as connection:
        cursor = await connection.execute(
            "SELECT * FROM devices ORDER BY creation_date, id;"
        )
        rows = await cursor.fetchall()
    return [map_row_to_device(row) for row in rows]


async def read_device(name: str) -> Device | None:
    async with await _connect() as connection:
        cursor = await connection.execute(
            "SELECT * FROM devices WHERE name = %s;", (name,)
        )
        row = await cursor.fetchone()
    return map_row_to_device(row) if row is not None else None


async def write_envelope(envelope: Envelope) -> None:
    data = envelope.data
    values: dict[str, Any] = {
        "id": envelope.id,
        "recorded_at": _as_datetime(envelope.date),
        "event_type": data.case,
        "mac_address": data.mac_address,
        "ip_address": getattr(data, "ip_address", None),
        "source_date": _as_datetime(data.source_date),
    }
    for field in (
        "cpu_temperature", "temperature", "distance", "humidity", "lux",
        "pressure", "uv", "gas", "water_depth_raw", "moisture_percent",
    ):
        values[field] = getattr(data, field, None)

    async with await _connect() as connection:
        await connection.execute(
            """
            INSERT INTO envelopes (
                id, recorded_at, event_type, mac_address, ip_address, source_date,
                cpu_temperature, temperature, distance, humidity, lux, pressure,
                uv, gas, water_depth_raw, moisture_percent
            ) VALUES (
                %(id)s, %(recorded_at)s, %(event_type)s, %(mac_address)s,
                %(ip_address)s, %(source_date)s, %(cpu_temperature)s,
                %(temperature)s, %(distance)s, %(humidity)s, %(lux)s,
                %(pressure)s, %(uv)s, %(gas)s, %(water_depth_raw)s,
                %(moisture_percent)s
            )
            ON CONFLICT (id) DO UPDATE SET
                recorded_at = EXCLUDED.recorded_at,
                event_type = EXCLUDED.event_type,
                mac_address = EXCLUDED.mac_address,
                ip_address = EXCLUDED.ip_address,
                source_date = EXCLUDED.source_date,
                cpu_temperature = EXCLUDED.cpu_temperature,
                temperature = EXCLUDED.temperature,
                distance = EXCLUDED.distance,
                humidity = EXCLUDED.humidity,
                lux = EXCLUDED.lux,
                pressure = EXCLUDED.pressure,
                uv = EXCLUDED.uv,
                gas = EXCLUDED.gas,
                water_depth_raw = EXCLUDED.water_depth_raw,
                moisture_percent = EXCLUDED.moisture_percent;
            """,
            values,
        )


async def read_envelopes(
    mac_address: str | None = None,
    *,
    min_hours_ago: int | None = None,
    max_hours_ago: int | None = None,
    event_type: Literal['ENVIRONMENT_SENSOR', 'HEARTBEAT'] | None = None,
) -> list[Envelope]:
    conditions: list[sql.SQL] = []
    parameters: dict[str, Any] = {}
    if mac_address is not None:
        conditions.append(sql.SQL("mac_address = %(mac_address)s"))
        parameters["mac_address"] = mac_address
    if event_type is not None:
        conditions.append(sql.SQL("event_type = %(event_type)s"))
        parameters["event_type"] = event_type
    if max_hours_ago is not None:
        conditions.append(sql.SQL("recorded_at >= now() - %(max_age)s"))
        parameters["max_age"] = timedelta(hours=max_hours_ago)
    if min_hours_ago is not None:
        conditions.append(sql.SQL("recorded_at <= now() - %(min_age)s"))
        parameters["min_age"] = timedelta(hours=min_hours_ago)
    where = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions) if conditions else sql.SQL("")
    async with await _connect() as connection:
        cursor = await connection.execute(
            sql.SQL("SELECT * FROM envelopes") + where + sql.SQL(" ORDER BY recorded_at, id;"),
            parameters,
        )
        rows = await cursor.fetchall()

    envelopes: list[Envelope] = []
    for row in rows:
        data: EnvironmentSensorDataDto | HeartbeatDataDto
        if row["event_type"] == "ENVIRONMENT_SENSOR":
            data = EnvironmentSensorDataDto(
                case="ENVIRONMENT_SENSOR",
                mac_address=row["mac_address"],
                source_date=row["source_date"],
                cpu_temperature=row["cpu_temperature"],
                temperature=row["temperature"],
                distance=row["distance"],
                humidity=row["humidity"],
                lux=row["lux"],
                pressure=row["pressure"],
                uv=row["uv"],
                gas=row["gas"],
                water_depth_raw=row["water_depth_raw"],
                moisture_percent=row["moisture_percent"],
            )
        elif row["event_type"] == "HEARTBEAT":
            data = HeartbeatDataDto(
                case="HEARTBEAT",
                mac_address=row["mac_address"],
                ip_address=row["ip_address"],
                source_date=row["source_date"],
            )
        else:
            raise ValueError(f"Unknown envelope event type: {row['event_type']}")
        envelopes.append(
            Envelope(id=row["id"], date=row["recorded_at"], data=data)
        )
    return envelopes


async def delete_envelopes_before(before: datetime) -> None:
    async with await _connect() as connection:
        await connection.execute(
            "DELETE FROM envelopes WHERE recorded_at < %s;",
            (_as_datetime(before),),
        )
