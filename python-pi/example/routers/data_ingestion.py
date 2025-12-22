import datetime
from uuid import UUID, uuid4
from dataclasses import dataclass
from fastapi import APIRouter
#from pydantic import BaseModel

router = APIRouter(
    prefix='/data-ingestion'
)

@dataclass
class SensorData:
    temperature: float
    humidity: float
    lux: float
    #temperatureRaw: int

@dataclass
class Envelope:
    data: SensorData
    date: datetime

memory_store: dict[UUID, Envelope] = {}

@router.get('/')
async def read_data():
    return memory_store

@router.post('/')
async def create_data(sensor_data: SensorData):
    global memory_store
    memory_store[uuid4()] = Envelope(sensor_data, datetime.datetime.now())
    if memory_store.__len__() > 50:
        #memory_store = [x for x in memory_store.items() if x]
        temp: dict[UUID, Envelope] = {}
        for k,v in memory_store.items():
            if v.date > datetime.datetime.now():
                temp[k] = v
        memory_store = temp