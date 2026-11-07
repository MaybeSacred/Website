from typing import Literal
from datetime import datetime
from typing import Optional
from pydantic import Field
from uuid import UUID
from dataclasses import dataclass
from pandas import Timestamp

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
class HomeObjectCreationDto:
    name: str
    tags: list[str]
    user_data: dict[str, str]
    location: Vector3Dto
    orientation: QuaternionDto

@dataclass
class HomeObjectUpdateDto:
    name: Optional[str] = None
    tags: Optional[list[str]] = None
    user_data: Optional[dict[str, str]] = None
    location: Optional[Vector3Dto] = None
    orientation: Optional[QuaternionDto] = None

@dataclass
class HomeObject:
    id: UUID
    name: str
    creation_date: Timestamp
    tags: list[str]
    user_data: dict[str, str]
    location: Vector3Dto
    orientation: QuaternionDto