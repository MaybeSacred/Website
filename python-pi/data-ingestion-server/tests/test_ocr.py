import importlib
from io import BytesIO
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
import pytesseract

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
ocr = importlib.import_module("python-pi.data-ingestion-server.ocr")


class OcrTests(unittest.TestCase):
    def test_pillow_image_and_options_are_forwarded_without_altering_text(self):
        with Image.new("RGB", (20, 20), "white") as image:
            with patch.object(
                ocr.pytesseract, "image_to_string", return_value="Hello\n\n"
            ) as recognize:
                self.assertEqual(
                    ocr.extract_text(image, lang="fra", config="--psm 6", timeout=2),
                    "Hello\n\n",
                )
                recognize.assert_called_once_with(
                    image, lang="fra", config="--psm 6", timeout=2
                )
            self.assertEqual(image.getpixel((0, 0)), (255, 255, 255))

    def test_encoded_images_are_decoded_in_memory(self):
        for format, mode in (("PNG", "RGBA"), ("JPEG", "RGB"), ("TIFF", "L")):
            with self.subTest(format=format):
                with BytesIO() as stream, Image.new(mode, (20, 10), "white") as image:
                    image.save(stream, format=format)
                    payload = stream.getvalue()

                def recognize(decoded, **options):
                    self.assertIsInstance(decoded, Image.Image)
                    self.assertEqual(decoded.size, (20, 10))
                    self.assertEqual(decoded.mode, mode)
                    decoded.load()
                    self.assertEqual(options, {
                        "lang": "eng", "config": "", "timeout": 30,
                    })
                    return "Example\n"

                with patch.object(
                    ocr.pytesseract, "image_to_string", side_effect=recognize
                ):
                    self.assertEqual(ocr.extract_text_from_bytes(payload), "Example\n")

    def test_bytes_helper_forwards_custom_options_and_closes_decoded_image(self):
        with BytesIO() as stream, Image.new("RGB", (20, 20)) as image:
            image.save(stream, format="PNG")
            payload = stream.getvalue()
        with patch.object(ocr, "extract_text", return_value="Bonjour") as recognize:
            self.assertEqual(
                ocr.extract_text_from_bytes(
                    payload, lang="fra", config="--psm 7", timeout=5
                ),
                "Bonjour",
            )
            recognize.assert_called_once()
            self.assertEqual(recognize.call_args.kwargs, {
                "lang": "fra", "config": "--psm 7", "timeout": 5,
            })
            decoded = recognize.call_args.args[0]
        with self.assertRaises(ValueError):
            decoded.load()

    def test_invalid_images_raise_without_calling_tesseract(self):
        for payload in (b"", b"not an image", b"\x89PNG\r\n\x1a\n"):
            with self.subTest(payload=payload):
                with patch.object(ocr.pytesseract, "image_to_string") as recognize:
                    with self.assertRaises(UnidentifiedImageError):
                        ocr.extract_text_from_bytes(payload)
                    recognize.assert_not_called()

    def test_blank_image_text_is_not_replaced(self):
        with Image.new("RGB", (20, 20)) as image:
            with patch.object(ocr.pytesseract, "image_to_string", return_value=""):
                self.assertEqual(ocr.extract_text(image), "")

    def test_ocr_errors_propagate_and_owned_image_is_closed(self):
        with BytesIO() as stream, Image.new("RGB", (20, 20)) as image:
            image.save(stream, format="PNG")
            payload = stream.getvalue()
        for error in (
            pytesseract.TesseractNotFoundError(),
            pytesseract.TesseractError(1, "Missing language data"),
            RuntimeError("Tesseract process timeout"),
        ):
            with self.subTest(error=type(error).__name__):
                with patch.object(
                    ocr.pytesseract, "image_to_string", side_effect=error
                ) as recognize:
                    with self.assertRaises(type(error)) as raised:
                        ocr.extract_text_from_bytes(payload)
                    self.assertIs(raised.exception, error)
                    decoded = recognize.call_args.args[0]
                with self.assertRaises(ValueError):
                    decoded.load()


@unittest.skipUnless(shutil.which("tesseract"), "Tesseract executable is not installed")
class TesseractIntegrationTests(unittest.TestCase):
    def test_generated_image_and_encoded_bytes_return_actual_text(self):
        with Image.new("RGB", (500, 100), "white") as image:
            ImageDraw.Draw(image).text(
                (20, 20), "HELLO OCR 123",
                font=ImageFont.load_default(size=40), fill="black",
            )
            self.assertEqual(
                ocr.extract_text(image, config="--psm 7").strip(), "HELLO OCR 123"
            )
            with BytesIO() as stream:
                image.save(stream, format="PNG")
                self.assertEqual(
                    ocr.extract_text_from_bytes(
                        stream.getvalue(), config="--psm 7"
                    ).strip(),
                    "HELLO OCR 123",
                )


if __name__ == "__main__":
    unittest.main()
