from enum import Enum
from typing import Literal
from datetime import datetime, timedelta
from influxdb_client_3 import Point
from pandas import Timestamp
from ..influx_data import HOME_OBJECTS_TABLE, write_points, query
from pydantic import Field
from uuid import UUID, uuid4
from dataclasses import dataclass
from fastapi import APIRouter, HTTPException
import json

router = APIRouter(
    prefix='/home-objects'
)

@dataclass
class Vector3Dto:
    x: float
    y: float
    z: float

@dataclass
class QuaternionDto:
    x: float
    y: float
    z: float
    w: float
@dataclass
class HomeObjectCreationUpdateDto:
    tags: list[str]
    user_data: dict[str, str]
    location: Vector3Dto
    orientation: QuaternionDto

@dataclass
class HomeObject:
    id: UUID
    name: str
    creation_date: Timestamp
    tags: list[str]
    user_data: dict[str, str]
    location: Vector3Dto
    orientation: QuaternionDto
    
def to_point(envelope: HomeObject, overwrite: bool = False) -> list[Point]:
    v = (Point(HOME_OBJECTS_TABLE)
        .tag("name", envelope.name)
        .field("uuid", str(envelope.id))
        .field("tags", json.dumps(envelope.tags))
        .field("user_data", json.dumps(envelope.user_data))
        .field("location_x", envelope.location.x)
        .field("location_y", envelope.location.y)
        .field("location_z", envelope.location.z)
        .field("orientation_x", envelope.orientation.x)
        .field("orientation_y", envelope.orientation.y)
        .field("orientation_z", envelope.orientation.z)
        .field("orientation_w", envelope.orientation.w)
    )
    v = v.time(envelope.creation_date.value) if overwrite else v
    return [v]

def from_points(points) -> list[HomeObject]:
    return [HomeObject(UUID(i['uuid']), 
                       i['name'], 
                       i['time'], 
                       json.loads(i['tags']), 
                       json.loads(i['user_data']),
                       Vector3Dto(i['location_x'], i['location_y'], i['location_z']),
                       QuaternionDto(i['orientation_x'], i['orientation_y'], i['orientation_z'], i['orientation_w'])
                      ) 
            for i in points.to_pylist()]

async def get_home_object(name: str):
    val = await query(f"select * from \"{HOME_OBJECTS_TABLE}\" where name = $name;", name=name)
    if val is not None and len(val) > 0:
        return from_points(val)[0]
    
async def get_home_object_by_id(id: UUID):
    val = await query(f"select * from \"{HOME_OBJECTS_TABLE}\" where uuid = $id;", id=str(id))
    if val is not None and len(val) > 0:
        return from_points(val)[0]

@router.get('/', tags=['home-objects'])
async def read_data():
    val = await query(f"select * from \"{HOME_OBJECTS_TABLE}\";")
    return from_points(val)

@router.get('/{name}', tags=['home-objects'])
async def get_device(name: str):
    val = await get_home_object(name)
    if val is None:
        raise HTTPException(status_code=404, detail=f"Home object not found: {name}")
    return val

@router.post('/{name}', tags=['home-objects'])
async def create_device(name: str, creation_dto: HomeObjectCreationUpdateDto):
    existing = await get_home_object(name)
    if existing is not None:
        raise HTTPException(status_code=400, detail=f"Home object already exists: {name}")
    new_device = HomeObject(uuid4(), 
                            name, 
                            Timestamp(datetime.now()), 
                            tags=creation_dto.tags, 
                            user_data=creation_dto.user_data,
                            location=creation_dto.location,
                            orientation=creation_dto.orientation)
    write_points(to_point(new_device))

@router.post('/{name}/tags', tags=['home-objects'])
async def provision_device(name: str, data: HomeObjectCreationUpdateDto):
    existing = await get_home_object(name)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Home object not found: {name}")
    else:
        existing.user_data = data.user_data
        existing.tags = data.tags
        existing.location = data.location
        existing.orientation = data.orientation
        write_points(to_point(existing, True))