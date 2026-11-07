from io import BytesIO
from uuid import UUID

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import Response
from PIL import Image, UnidentifiedImageError
from starlette.concurrency import run_in_threadpool

from .. import library_data as storage
from ..domain.library import (
    Document, DocumentCreationDto, DocumentUpdateDto,
    Library, LibraryCreationDto, LibraryDetail, LibraryUpdateDto,
)

router = APIRouter(prefix="/libraries", tags=["libraries"])
MAX_IMAGE_BYTES = 10 * 1024 * 1024


def require_found[T](value: T | None, kind: str) -> T:
    if value is None:
        raise HTTPException(status_code=404, detail=f"{kind} not found")
    return value


@router.get("/")
async def read_libraries() -> list[Library]:
    return await storage.read_libraries()


@router.post("/", status_code=201)
async def create_library(data: LibraryCreationDto) -> Library:
    return await storage.create_library(data)


@router.get("/{library_id}")
async def read_library(library_id: UUID) -> LibraryDetail:
    library = require_found(await storage.read_library(library_id), "Library")
    return LibraryDetail(
        **library.model_dump(), documents=await storage.read_documents(library_id)
    )


@router.patch("/{library_id}")
async def update_library(library_id: UUID, data: LibraryUpdateDto) -> Library:
    return require_found(await storage.update_library(library_id, data), "Library")


@router.delete("/{library_id}", status_code=204)
async def delete_library(library_id: UUID) -> Response:
    if not await storage.delete_library(library_id):
        raise HTTPException(status_code=404, detail="Library not found")
    return Response(status_code=204)


@router.get("/{library_id}/documents/")
async def read_documents(library_id: UUID) -> list[Document]:
    require_found(await storage.read_library(library_id), "Library")
    return await storage.read_documents(library_id)


@router.post("/{library_id}/documents/", status_code=201)
async def create_document(library_id: UUID, data: DocumentCreationDto) -> Document:
    return require_found(await storage.create_document(library_id, data), "Library")


@router.get("/{library_id}/documents/{document_id}")
async def read_document(library_id: UUID, document_id: UUID) -> Document:
    return require_found(await storage.read_document(library_id, document_id), "Document")


@router.patch("/{library_id}/documents/{document_id}")
async def update_document(
    library_id: UUID, document_id: UUID, data: DocumentUpdateDto,
) -> Document:
    return require_found(
        await storage.update_document(library_id, document_id, data), "Document"
    )


@router.delete("/{library_id}/documents/{document_id}", status_code=204)
async def delete_document(library_id: UUID, document_id: UUID) -> Response:
    if not await storage.delete_document(library_id, document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return Response(status_code=204)


def image_media_type(data: bytes) -> str:
    try:
        with BytesIO(data) as stream, Image.open(stream) as image:
            media_type = Image.MIME.get(image.format) if image.format else None
            image.verify()
        with BytesIO(data) as stream, Image.open(stream) as image:
            image.load()
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError) as error:
        raise HTTPException(status_code=422, detail="Invalid image upload") from error
    if media_type is None:
        raise HTTPException(status_code=422, detail="Unsupported image format")
    return media_type


@router.put("/{library_id}/documents/{document_id}/image")
async def upload_image(
    library_id: UUID, document_id: UUID, image: UploadFile,
) -> Document:
    require_found(await storage.read_document(library_id, document_id), "Document")
    try:
        data = await image.read(MAX_IMAGE_BYTES + 1)
    finally:
        await image.close()
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image exceeds 10 MiB")
    media_type = await run_in_threadpool(image_media_type, data)
    return require_found(
        await storage.write_document_image(library_id, document_id, data, media_type),
        "Document",
    )


@router.get("/{library_id}/documents/{document_id}/image")
async def download_image(library_id: UUID, document_id: UUID) -> Response:
    data, media_type = require_found(
        await storage.read_document_image(library_id, document_id), "Document image"
    )
    return Response(
        content=data, media_type=media_type,
        headers={"X-Content-Type-Options": "nosniff"},
    )


@router.delete("/{library_id}/documents/{document_id}/image", status_code=204)
async def delete_image(library_id: UUID, document_id: UUID) -> Response:
    require_found(
        await storage.write_document_image(library_id, document_id, None, None),
        "Document",
    )
    return Response(status_code=204)
