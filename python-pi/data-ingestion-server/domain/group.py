from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from pandas import Timestamp

from .home_object import Vector3Dto
from .polygon import validate_polygon


@dataclass
class GroupCreationDto:
    name: str
    points: list[Vector3Dto]

    def __post_init__(self):
        validate_polygon(self.points)


@dataclass
class GroupUpdateDto:
    name: Optional[str] = None
    points: Optional[list[Vector3Dto]] = None

    def __post_init__(self):
        if self.points is not None:
            validate_polygon(self.points)


@dataclass
class Group:
    id: UUID
    name: str
    creation_date: Timestamp
    points: list[Vector3Dto]
