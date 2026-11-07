from pandas import Timestamp
from ..postgres_data import write_home_object, read_home_object, read_home_objects
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException
from ..domain.home_object import HomeObjectCreationDto, HomeObject, Vector3Dto, QuaternionDto, HomeObjectUpdateDto

router = APIRouter(
    prefix='/home-objects'
)

async def get_home_object_by_id(id: UUID):
    return  await read_home_object(id)

@router.get('/', tags=['home-objects'])
async def read_objects():
    return await read_home_objects()

@router.get('/{id}', tags=['home-objects'], responses={404: {"description": "Home object not found"}})
async def get_object(id: str):
    val = await get_home_object_by_id(UUID(id))
    if val is None:
        raise HTTPException(status_code=404, detail=f"Home object not found: {id}")
    return val

@router.post('/', tags=['home-objects'], responses={400: {"description": "Home object already exists"}})
async def create_object(creation_dto: HomeObjectCreationDto):
    return await create_object_with_id(str(uuid4()), creation_dto)

@router.post('/{id}', tags=['home-objects'], responses={400: {"description": "Home object already exists"}})
async def create_object_with_id(id: str, creation_dto: HomeObjectCreationDto):
    existing = await get_home_object_by_id(UUID(id))
    if existing is not None:
        raise HTTPException(status_code=400, detail=f"Home object already exists: {id}")
    new_object = HomeObject(UUID(id), 
                            creation_dto.name,
                            Timestamp.now(),
                            tags=creation_dto.tags, 
                            user_data=creation_dto.user_data,
                            location=creation_dto.location,
                            orientation=creation_dto.orientation)
    await write_home_object(new_object)

@router.post('/{id}/update', tags=['home-objects'], responses={404: {"description": "Home object not found"}})
async def update_tags(id: str, data: HomeObjectUpdateDto):
    existing = await get_home_object_by_id(UUID(id))
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Home object not found: {id}")
    else:
        if data.name is not None:
            existing.name = data.name
        if data.user_data is not None:
            existing.user_data = data.user_data
        if data.tags is not None:
            existing.tags = data.tags
        if data.location is not None:
            existing.location = data.location
        if data.orientation is not None:
            existing.orientation = data.orientation
        await write_home_object(existing)
        