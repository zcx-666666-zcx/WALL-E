import base64
import struct
import time
import zlib

FALLBACK_JPEG_BASE64 = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAP//////////////////////////////////////////////////////////"
    "////////////////////////////wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAX/xAAUEA"
    "EAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIQAxAAAAGf/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABBQJ//8"
    "QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAgBAwEBPwF//8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAgBAgEBPwF//8"
    "QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQAGPwJ//8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPyF//9"
    "oADAMBAAIAAwAAABCf/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAgBAwEBPxB//8QAFBEBAAAAAAAAAAAAAAAAAA"
    "AAAP/aAAgBAgEBPxB//8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxB//9k="
)


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + chunk_type
        + data
        + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
    )


def _make_png_bytes(width: int, height: int, sequence: int = 0) -> bytes:
    rows = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            r = (x * 255 // max(width - 1, 1) + sequence * 7) % 256
            g = (y * 255 // max(height - 1, 1) + sequence * 3) % 256
            b = (80 + sequence * 11 + x // 6 + y // 5) % 256
            row.extend((r, g, b))
        rows.append(bytes(row))

    raw = b"".join(rows)
    header = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return header + _png_chunk(b"IHDR", ihdr) + _png_chunk(b"IDAT", zlib.compress(raw, 6)) + _png_chunk(b"IEND", b"")


def make_demo_jpeg_bytes(text: str, width: int = 640, height: int = 360, sequence: int = 0) -> bytes:
    try:
        from PIL import Image, ImageDraw, ImageFont

        image = Image.new("RGB", (width, height), (18, 26, 34))
        draw = ImageDraw.Draw(image)
        for y in range(height):
            color = (18 + y * 28 // max(height, 1), 38 + y * 40 // max(height, 1), 58 + y * 35 // max(height, 1))
            draw.line([(0, y), (width, y)], fill=color)

        accent = (255, 132, 72)
        draw.rectangle((20, 20, width - 20, height - 20), outline=accent, width=3)
        draw.ellipse((width - 95, 28, width - 35, 88), outline=(96, 220, 150), width=4)
        draw.line((45, height - 70, width - 45, height - 70), fill=(96, 220, 150), width=4)

        try:
            font = ImageFont.truetype("Arial.ttf", max(20, width // 18))
            small_font = ImageFont.truetype("Arial.ttf", max(13, width // 32))
        except Exception:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        draw.text((42, 48), text, fill=(255, 255, 255), font=font)
        draw.text((42, 105), f"hardware-demo frame #{sequence}", fill=(230, 238, 242), font=small_font)
        draw.text((42, 135), time.strftime("%Y-%m-%d %H:%M:%S"), fill=(230, 238, 242), font=small_font)

        from io import BytesIO

        output = BytesIO()
        image.save(output, format="JPEG", quality=78)
        return output.getvalue()
    except Exception:
        return base64.b64decode(FALLBACK_JPEG_BASE64)


def build_camera_frame_payload(device_name: str, image_bytes: bytes, now_ms: int | None = None):
    return {
        "deviceName": device_name,
        "timestamp": now_ms if now_ms is not None else int(time.time() * 1000),
        "format": "jpg",
        "encoding": "base64",
        "image": base64.b64encode(image_bytes).decode("ascii"),
    }
