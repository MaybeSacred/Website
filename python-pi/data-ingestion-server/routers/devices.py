from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from ..domain.device import (
    Device,
    ProvisionedDevice,
    ProvisioningDataDto,
    UnprovisionedDevice,
)
from ..postgres_data import read_device as get_device, read_devices, write_device
from .home_objects import get_home_object_by_id

router = APIRouter(
    prefix='/devices'
)


@router.get('/', tags=['devices'])
async def read_data():
    return await read_devices()


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
    new_device = Device(
        uuid4(), name, datetime.now(UTC),
        device_status=UnprovisionedDevice(case='UNPROVISIONED'),
    )
    await write_device(new_device)


@router.post('/{name}/provision', tags=['devices'])
async def provision_device(name: str, provisioning_data: ProvisioningDataDto):
    device = await get_device(name)
    if device is None:
        raise HTTPException(status_code=404, detail=f"Device not found: {name}")
    home_object = await get_home_object_by_id(provisioning_data.home_object_id)
    if home_object is None:
        raise HTTPException(status_code=422, detail=f"Home object not found: {provisioning_data.home_object_id}")
    device.device_status = ProvisionedDevice(
        case='PROVISIONED',
        mac_address=provisioning_data.mac_address,
        home_object_id=provisioning_data.home_object_id,
    )
    await write_device(device)
