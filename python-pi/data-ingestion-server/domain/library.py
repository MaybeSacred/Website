from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class LibraryCreationDto(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Name


class LibraryUpdateDto(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Name | None = None

    @field_validator("name")
    @classmethod
    def reject_null_name(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("name cannot be null")
        return value


class DocumentCreationDto(LibraryCreationDto):
    description: str | None = None
    ocr_text: str | None = None


class DocumentUpdateDto(LibraryUpdateDto):
    description: str | None = None
    ocr_text: str | None = None


class Library(BaseModel):
    id: UUID
    name: str
    creation_date: datetime


class Document(BaseModel):
    id: UUID
    library_id: UUID
    name: str
    creation_date: datetime
    description: str | None
    ocr_text: str | None
    has_image: bool


class LibraryDetail(Library):
    documents: list[Document]
