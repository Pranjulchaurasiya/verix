"""Image storage, perceptual hashing, and URL management."""

import os
import io
import uuid
import hashlib
import hmac
import secrets
import time
from urllib.parse import urlparse, urlunparse, urlencode, parse_qsl
from typing import Tuple, Optional
from PIL import Image
import imagehash
from backend.app.config import settings

_development_media_key = secrets.token_bytes(32)


def _media_key() -> bytes:
    if settings.MEDIA_SIGNING_KEY:
        return settings.MEDIA_SIGNING_KEY.encode("utf-8")
    if settings.ENVIRONMENT.lower() == "production":
        raise RuntimeError("MEDIA_SIGNING_KEY must be configured in production.")
    return _development_media_key


def signed_image_url(image_url: str, scan_id: str) -> str:
    """Return a short-lived bearer link for a locally stored scan image."""
    parsed = urlparse(image_url)
    if not parsed.path.startswith("/uploads/"):
        return image_url
    name = parsed.path.removeprefix("/uploads/")
    if not name or "/" in name or "\\" in name:
        return image_url
    expires = int(time.time()) + min(settings.UPLOAD_RETENTION_DAYS, 7) * 86400
    message = f"{scan_id}:{name}:{expires}".encode("utf-8")
    signature = hmac.new(_media_key(), message, hashlib.sha256).hexdigest()
    query = urlencode([*parse_qsl(parsed.query), ("scan", scan_id), ("expires", expires), ("signature", signature)])
    return urlunparse(parsed._replace(query=query))


def verify_image_signature(scan_id: str, name: str, expires: int, signature: str) -> bool:
    if expires < int(time.time()) or expires > int(time.time()) + 8 * 86400:
        return False
    message = f"{scan_id}:{name}:{expires}".encode("utf-8")
    expected = hmac.new(_media_key(), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

def validate_image_bytes(file_bytes: bytes) -> Tuple[int, int, str]:
    """Validate that bytes are a safe, decodable raster image before storing them."""
    if not file_bytes:
        raise ValueError("The uploaded file is empty.")
    if len(file_bytes) > settings.MAX_IMAGE_SIZE_BYTES:
        raise ValueError("The uploaded image exceeds the maximum size limit.")

    try:
        with Image.open(io.BytesIO(file_bytes)) as image:
            width, height = image.size
            if width < 1 or height < 1 or width * height > settings.MAX_IMAGE_PIXELS:
                raise ValueError("The uploaded image dimensions are not supported.")
            image.verify()
            image_format = (image.format or "").upper()
    except Image.DecompressionBombError as exc:
        raise ValueError("The uploaded image is too large to process safely.") from exc
    except (Image.UnidentifiedImageError, OSError) as exc:
        raise ValueError("The uploaded file is not a valid supported image.") from exc

    if image_format not in {"JPEG", "PNG", "WEBP", "GIF"}:
        raise ValueError("Only JPEG, PNG, WebP, and GIF images are supported.")
    return width, height, image_format

def compute_image_hashes(image_bytes: bytes) -> Tuple[str, str]:
    """
    Computes both exact SHA256 and perceptual average hash (aHash).
    Returns (sha256_hash, perceptual_hash_str).
    """
    sha256_hash = hashlib.sha256(image_bytes).hexdigest()
    
    try:
        pil_image = Image.open(io.BytesIO(image_bytes))
        # Convert to RGB if needed (handling RGBA / CMYK)
        if pil_image.mode not in ("RGB", "L"):
            pil_image = pil_image.convert("RGB")
        perceptual = str(imagehash.average_hash(pil_image))
    except Exception:
        # Fallback if image cannot be decoded by PIL
        perceptual = sha256_hash[:16]
        
    return sha256_hash, perceptual

def save_uploaded_image(file_bytes: bytes, original_filename: Optional[str] = None) -> Tuple[str, str, str]:
    """
    Saves image bytes to the uploads directory.
    Returns (saved_filepath, public_image_url, sha256_hash).
    """
    validate_image_bytes(file_bytes)
    sha256_hash, _ = compute_image_hashes(file_bytes)
    
    # Extract extension or default to .jpg
    ext = ".jpg"
    if original_filename and "." in original_filename:
        ext = os.path.splitext(original_filename)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
            ext = ".jpg"
            
    unique_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(settings.UPLOAD_DIR, unique_name)
    
    with open(dest_path, "wb") as f:
        f.write(file_bytes)
        
    # Build public or relative URL
    base_url = settings.PUBLIC_BASE_URL or os.environ.get("RENDER_EXTERNAL_URL", "")
    if base_url:
        base_url = base_url.rstrip("/")
        image_url = f"{base_url}/uploads/{unique_name}"
    else:
        image_url = f"/uploads/{unique_name}"
        
    return dest_path, image_url, sha256_hash
