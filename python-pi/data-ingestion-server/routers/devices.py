from enum import Enum
from typing import Literal
from datetime import datetime, timedelta
from influxdb_client_3 import Point
from pandas import Timestamp
from ..influx_data import DEVICE_TABLE, write_points, query
from pydantic import Field
from uuid import UUID, uuid4
from dataclasses import dataclass
from fastapi import APIRouter, HTTPException
from .home_objects import get_home_object_by_id

#from pydantic import BaseModel

router = APIRouter(
    prefix='/devices'
)

@dataclass
class ProvisioningDataDto:
    mac_address: str
    home_object_id: UUID

@dataclass
class UnprovisionedDevice:
    case: Literal['UNPROVISIONED']

@dataclass
class ProvisionedDevice:
    case: Literal['PROVISIONED']
    mac_address: str
    home_object_id: UUID

@dataclass
class Device:
    id: UUID
    name: str
    creation_date: Timestamp
    device_status: UnprovisionedDevice | ProvisionedDevice = Field(discriminator='case')
    
def to_point(envelope: Device, overwrite: bool = False) -> list[Point]:
    v = (Point(DEVICE_TABLE)
        .tag("name", envelope.name)
        .field("uuid", str(envelope.id))
        .field("case", envelope.device_status.case)
        .field("home_object_id", str(envelope.device_status.home_object_id) if isinstance(envelope.device_status, ProvisionedDevice) else None)
        .field("mac_address", envelope.device_status.mac_address if isinstance(envelope.device_status, ProvisionedDevice) else None))
    v = v.time(envelope.creation_date.value) if overwrite else v
    return [v]

def from_points(points) -> list[Device]:
    return [Device(UUID(i['uuid']), i['name'], i['time'],
                ProvisionedDevice('PROVISIONED', i['mac_address'], UUID(i['home_object_id']))) 
            if i['case'] == 'PROVISIONED' 
            else 
                Device(UUID(i['uuid']), i['name'], i['time'], 
                    UnprovisionedDevice('UNPROVISIONED')) 
            for i in points.to_pylist()]

async def get_device(name: str):
    val = await query(f"select * from \"{DEVICE_TABLE}\" where name = $name;", name=name)
    if val is not None and len(val) > 0:
        return from_points(val)[0]

@router.get('/', tags=['devices'])
async def read_data():
    val = await query(f"select * from \"{DEVICE_TABLE}\";")
    return from_points(val)

@router.get('/{name}', tags=['devices'])
async def read_device(name: str):
    device = await get_device(name)
    if device is None:
        raise HTTPException(status_code=404, detail=f"Device not found: {name}")
    return device

@router.post('/{name}', tags=['devices'])
async def create_device_endpoint(name: str):
    existing = await get_device(name)
    if existing is not None:
        raise HTTPException(status_code=400, detail=f"Device already exists: {name}")
    new_device = Device(uuid4(), name, Timestamp(datetime.now()), device_status = UnprovisionedDevice(case='UNPROVISIONED'))
    write_points(to_point(new_device))

@router.post('/{name}/provision', tags=['devices'])
async def provision_device(name: str, provisioning_data: ProvisioningDataDto):
    device = await get_device(name)
    if device is None:
        raise HTTPException(status_code=404, detail=f"Device not found: {name}")
    home_object = await get_home_object_by_id(provisioning_data.home_object_id)
    if home_object is None:
        raise HTTPException(status_code=422, detail=f"Home object not found: {provisioning_data.home_object_id}")
    device.device_status = ProvisionedDevice(case='PROVISIONED', mac_address=provisioning_data.mac_address, home_object_id=provisioning_data.home_object_id)
    write_points(to_point(device, True))