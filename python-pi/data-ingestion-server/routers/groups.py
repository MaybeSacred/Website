from pandas import Timestamp
from ..postgres_data import write_group, read_group, read_groups, delete_group
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException
from ..domain.group import Group, GroupCreationDto, GroupUpdateDto

router = APIRouter(
    prefix='/groups'
)

async def get_group_by_id(id: UUID):
    return await read_group(id)

@router.get('/', tags=['groups'])
async def read_all_groups():
    return await read_groups()

@router.get('/{id}', tags=['groups'], responses={404: {"description": "Group not found"}})
async def get_group(id: UUID):
    val = await get_group_by_id(id)
    if val is None:
        raise HTTPException(status_code=404, detail=f"Group not found: {id}")
    return val

@router.post('/', tags=['groups'], responses={400: {"description": "Group already exists"}})
async def create_group(creation_dto: GroupCreationDto):
    return await create_group_with_id(uuid4(), creation_dto)

@router.post('/{id}', tags=['groups'], responses={400: {"description": "Group already exists"}})
async def create_group_with_id(id: UUID, creation_dto: GroupCreationDto):
    existing = await get_group_by_id(id)
    if existing is not None:
        raise HTTPException(status_code=400, detail=f"Group already exists: {id}")
    await write_group(Group(id, creation_dto.name, Timestamp.now(), creation_dto.points))

@router.post('/{id}/update', tags=['groups'], responses={404: {"description": "Group not found"}})
async def update_group(id: UUID, data: GroupUpdateDto):
    existing = await get_group_by_id(id)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Group not found: {id}")
    if data.name is not None:
        existing.name = data.name
    if data.points is not None:
        existing.points = data.points
    await write_group(existing)

@router.delete('/{id}', tags=['groups'], responses={404: {"description": "Group not found"}})
async def remove_group(id: UUID):
    if not await delete_group(id):
        raise HTTPException(status_code=404, detail=f"Group not found: {id}")
