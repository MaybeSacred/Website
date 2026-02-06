from typing import Literal
from datetime import datetime, timedelta
from influxdb_client_3 import Point
from pydantic import Field
from uuid import UUID, uuid4
from dataclasses import dataclass
from fastapi import APIRouter
from ..influx_data import POINT_DATA_TABLE, write_points, query

#from pydantic import BaseModel

router = APIRouter(
    prefix='/data-ingestion'
)

@dataclass
class HeartbeatDataDto:
    case: Literal['HEARTBEAT']
    mac_address: str
    ip_address: str
    source_date: datetime | int

@dataclass
class EnvironmentSensorDataDto:
    case: Literal['ENVIRONMENT_SENSOR']
    mac_address: str
    source_date: datetime | int
    cpu_temperature: float | None = None
    temperature: float | None = None
    distance: float | None = None
    humidity: float | None = None
    lux: float | None = None
    pressure: float | None = None
    uv: int | None = None
    gas: float | None = None
    water_depth_raw: int | None = None
    #temperatureRaw: int

@dataclass
class Envelope:
    id: UUID
    date: datetime
    data: EnvironmentSensorDataDto | HeartbeatDataDto = Field(discriminator='case')

def to_point(envelope: Envelope) -> list[Point]:
    return [Point(POINT_DATA_TABLE)
            .tag("mac_address", envelope.data.mac_address)
            .field("uuid", str(envelope.id))
            .field("case", envelope.data.case)
            .field("temperature", envelope.data.temperature if isinstance(envelope.data, EnvironmentSensorDataDto) else None)
            .field("cpu_temperature", envelope.data.cpu_temperature if isinstance(envelope.data, EnvironmentSensorDataDto) else None)
            .field("distance", envelope.data.distance if isinstance(envelope.data, EnvironmentSensorDataDto) else None)
            .field("humidity", envelope.data.humidity if isinstance(envelope.data, EnvironmentSensorDataDto) else None)
            .field("lux", envelope.data.lux if isinstance(envelope.data, EnvironmentSensorDataDto) else None)
            .field("pressure", envelope.data.pressure if isinstance(envelope.data, EnvironmentSensorDataDto) else None)
            .field("uv", envelope.data.uv if isinstance(envelope.data, EnvironmentSensorDataDto) else None)
            .field("gas", envelope.data.gas if isinstance(envelope.data, EnvironmentSensorDataDto) else None)
            .field("water_depth_raw", envelope.data.water_depth_raw if isinstance(envelope.data, EnvironmentSensorDataDto) else None)
            .field("source_date", envelope.data.source_date if isinstance(envelope.data.source_date, int) else envelope.data.source_date.timestamp())
            .field("ip_address", envelope.data.ip_address if isinstance(envelope.data, HeartbeatDataDto) else None)
        ]

def from_points(points) -> list[Envelope]:
    return [Envelope(i['uuid'], i['time'], 
                EnvironmentSensorDataDto('ENVIRONMENT_SENSOR', 
                                         i['mac_address'], 
                                         datetime.fromtimestamp(i['source_date']), 
                                         i.get('cpu_temperature', None), 
                                         i.get('temperature', None), 
                                         i.get('distance', None), 
                                         i.get('humidity', None), 
                                         i.get('lux', None), 
                                         i.get('pressure', None), 
                                         i.get('uv', None), 
                                         i.get('gas', None), 
                                         i.get('water_depth_raw', None))) 
            if i['case'] == 'ENVIRONMENT_SENSOR' 
            else 
                Envelope(i['uuid'], i['time'], 
                    HeartbeatDataDto('HEARTBEAT', 
                                     i['mac_address'], 
                                     i['ip_address'], 
                                     datetime.fromtimestamp(i['source_date']))) 
            for i in points.to_pylist()]
    
@router.get('/', tags=['data-ingestion'])
async def read_data():
    val = await query(f"select * from \"{POINT_DATA_TABLE}\";")
    return from_points(val)

@router.get('/{mac_address}', tags=['data-ingestion'])
async def read_data_for_device(mac_address: str):
    val = await query(f"select * from \"{POINT_DATA_TABLE}\" where mac_address = $mac_address;", mac_address=mac_address)
    return from_points(val)

@router.post('/environment-sensor', tags=['data-ingestion'])
async def create_data(sensor_data: EnvironmentSensorDataDto):
    envelope = Envelope(uuid4(), datetime.now(), sensor_data)
    write_points(to_point(envelope))

@router.post('/heartbeat', tags=['data-ingestion'])
async def create_heartbeat(heartbeat_data: HeartbeatDataDto):
    envelope = Envelope(uuid4(), datetime.now(), heartbeat_data)
    write_points(to_point(envelope))

@router.delete('/', tags=['data-ingestion'])
async def delete_data():
    await query('delete from \"point-data\" WHERE time < \'2027-01-01T00:00:00Z\';')