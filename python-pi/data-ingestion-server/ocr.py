from io import BytesIO

from PIL import Image
import pytesseract


def extract_text(
    image: Image.Image,
    *,
    lang: str = "eng",
    config: str = "",
    timeout: int = 30,
) -> str:
    """Return OCR text without modifying or closing the caller's Pillow image."""
    return pytesseract.image_to_string(
        image, lang=lang, config=config, timeout=timeout
    )


def extract_text_from_bytes(
    image_bytes: bytes,
    *,
    lang: str = "eng",
    config: str = "",
    timeout: int = 30,
) -> str:
    """Decode an encoded image in memory and return its first frame's OCR text."""
    with BytesIO(image_bytes) as stream:
        image = Image.open(stream)
        try:
            return extract_text(image, lang=lang, config=config, timeout=timeout)
        finally:
            image.close()
