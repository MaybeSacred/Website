from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from ..domain.sensor_data import Envelope, EnvironmentSensorDataDto, HeartbeatDataDto
from ..postgres_data import delete_envelopes_before, read_envelopes, write_envelope

router = APIRouter(
    prefix='/data-ingestion'
)


@router.get('/', tags=['data-ingestion'])
async def read_data():
    return await read_envelopes()


@router.get(
    '/{mac_address}',
    tags=['data-ingestion'],
    responses={400: {"description": "Invalid time range"}},
)
async def read_data_for_device(mac_address: str, min_hours_ago: int = 0, max_hours_ago: int = 72):
    if min_hours_ago < 0 or max_hours_ago < 0 or min_hours_ago > max_hours_ago or max_hours_ago - min_hours_ago > 72:
        raise HTTPException(status_code=400, detail=f"Invalid time range: {min_hours_ago} - {max_hours_ago}")
    return await read_envelopes(
        mac_address,
        min_hours_ago=min_hours_ago,
        max_hours_ago=max_hours_ago,
        event_type='ENVIRONMENT_SENSOR',
    )


@router.post('/environment-sensor', tags=['data-ingestion'])
async def create_data(sensor_data: EnvironmentSensorDataDto):
    envelope = Envelope(uuid4(), datetime.now(UTC), sensor_data)
    await write_envelope(envelope)


@router.post('/heartbeat', tags=['data-ingestion'])
async def create_heartbeat(heartbeat_data: HeartbeatDataDto):
    envelope = Envelope(uuid4(), datetime.now(UTC), heartbeat_data)
    await write_envelope(envelope)


@router.delete('/', tags=['data-ingestion'])
async def delete_data():
    await delete_envelopes_before(datetime(2027, 1, 1, tzinfo=UTC))
