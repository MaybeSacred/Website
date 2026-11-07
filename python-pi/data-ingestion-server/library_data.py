from typing import Any
from uuid import UUID, uuid4

from psycopg import sql

from .domain.library import (
    Document, DocumentCreationDto, DocumentUpdateDto,
    Library, LibraryCreationDto, LibraryUpdateDto,
)
from .postgres_data import _connect

DOCUMENT_COLUMNS = sql.SQL(
    "id, library_id, name, creation_date, description, ocr_text, "
    "(image IS NOT NULL) AS has_image"
)


async def read_libraries() -> list[Library]:
    async with await _connect() as connection:
        cursor = await connection.execute(
            "SELECT id, name, creation_date FROM libraries ORDER BY creation_date, id"
        )
        return [Library.model_validate(row) for row in await cursor.fetchall()]


async def read_library(id: UUID) -> Library | None:
    async with await _connect() as connection:
        cursor = await connection.execute(
            "SELECT id, name, creation_date FROM libraries WHERE id = %s", (id,)
        )
        row = await cursor.fetchone()
        return Library.model_validate(row) if row is not None else None


async def create_library(data: LibraryCreationDto) -> Library:
    async with await _connect() as connection:
        cursor = await connection.execute(
            "INSERT INTO libraries (id, name) VALUES (%s, %s) RETURNING id, name, creation_date",
            (uuid4(), data.name),
        )
        return Library.model_validate(await cursor.fetchone())


async def update_library(id: UUID, data: LibraryUpdateDto) -> Library | None:
    if not data.model_fields_set:
        return await read_library(id)
    async with await _connect() as connection:
        cursor = await connection.execute(
            "UPDATE libraries SET name = %s WHERE id = %s RETURNING id, name, creation_date",
            (data.name, id),
        )
        row = await cursor.fetchone()
        return Library.model_validate(row) if row is not None else None


async def delete_library(id: UUID) -> bool:
    async with await _connect() as connection:
        cursor = await connection.execute("DELETE FROM libraries WHERE id = %s", (id,))
        return cursor.rowcount > 0


async def read_documents(library_id: UUID) -> list[Document]:
    async with await _connect() as connection:
        cursor = await connection.execute(
            sql.SQL("SELECT {} FROM documents WHERE library_id = %s ORDER BY creation_date, id")
            .format(DOCUMENT_COLUMNS), (library_id,),
        )
        return [Document.model_validate(row) for row in await cursor.fetchall()]


async def read_document(library_id: UUID, id: UUID) -> Document | None:
    async with await _connect() as connection:
        cursor = await connection.execute(
            sql.SQL("SELECT {} FROM documents WHERE library_id = %s AND id = %s")
            .format(DOCUMENT_COLUMNS), (library_id, id),
        )
        row = await cursor.fetchone()
        return Document.model_validate(row) if row is not None else None


async def create_document(library_id: UUID, data: DocumentCreationDto) -> Document | None:
    async with await _connect() as connection:
        cursor = await connection.execute(
            sql.SQL(
                "INSERT INTO documents (id, library_id, name, description, ocr_text) "
                "SELECT %s, id, %s, %s, %s FROM libraries WHERE id = %s RETURNING {}"
            ).format(DOCUMENT_COLUMNS),
            (uuid4(), data.name, data.description, data.ocr_text, library_id),
        )
        row = await cursor.fetchone()
        return Document.model_validate(row) if row is not None else None


async def update_document(
    library_id: UUID, id: UUID, data: DocumentUpdateDto,
) -> Document | None:
    changes: dict[str, Any] = data.model_dump(exclude_unset=True)
    if not changes:
        return await read_document(library_id, id)
    async with await _connect() as connection:
        cursor = await connection.execute(
            sql.SQL("UPDATE documents SET {} WHERE library_id = %s AND id = %s RETURNING {}")
            .format(
                sql.SQL(", ").join(
                    sql.SQL("{} = %s").format(sql.Identifier(key)) for key in changes
                ),
                DOCUMENT_COLUMNS,
            ),
            (*changes.values(), library_id, id),
        )
        row = await cursor.fetchone()
        return Document.model_validate(row) if row is not None else None


async def delete_document(library_id: UUID, id: UUID) -> bool:
    async with await _connect() as connection:
        cursor = await connection.execute(
            "DELETE FROM documents WHERE library_id = %s AND id = %s", (library_id, id)
        )
        return cursor.rowcount > 0


async def write_document_image(
    library_id: UUID, id: UUID, image: bytes | None, media_type: str | None,
) -> Document | None:
    async with await _connect() as connection:
        cursor = await connection.execute(
            sql.SQL(
                "UPDATE documents SET image = %s, image_media_type = %s "
                "WHERE library_id = %s AND id = %s RETURNING {}"
            ).format(DOCUMENT_COLUMNS), (image, media_type, library_id, id),
        )
        row = await cursor.fetchone()
        return Document.model_validate(row) if row is not None else None


async def read_document_image(library_id: UUID, id: UUID) -> tuple[bytes, str] | None:
    async with await _connect() as connection:
        cursor = await connection.execute(
            "SELECT image, image_media_type FROM documents "
            "WHERE library_id = %s AND id = %s AND image IS NOT NULL", (library_id, id),
        )
        row = await cursor.fetchone()
        return (bytes(row["image"]), row["image_media_type"]) if row is not None else None
