"""Synthetic AI Generation & Provenance Metadata Analyzer.

Inspects image headers, EXIF tags, PNG chunks, and C2PA markers to detect
AI generator signatures (Midjourney, DALL-E, Stable Diffusion, ComfyUI, Flux, etc.)
and distinguish genuine retail items from zero-match 'Ghost synthetic listings'.
"""

from typing import Dict, Any, List, Optional
import io
import re
import logging
from PIL import Image, ExifTags

logger = logging.getLogger("verix.provenance")

KNOWN_GENERATORS = {
    "midjourney": "Midjourney",
    "dall-e": "OpenAI DALL-E",
    "dalle": "OpenAI DALL-E",
    "stable diffusion": "Stable Diffusion",
    "sd-webui": "Stable Diffusion (AUTOMATIC1111)",
    "automatic1111": "Stable Diffusion (AUTOMATIC1111)",
    "comfyui": "ComfyUI",
    "novelai": "NovelAI",
    "civitai": "Civitai Model Pipeline",
    "invokeai": "InvokeAI",
    "adobe firefly": "Adobe Firefly",
    "generative ai": "Generative AI Pipeline",
    "flux.1": "Black Forest Labs FLUX.1",
    "leonardo.ai": "Leonardo AI",
    "synthid": "Google DeepMind SynthID Marker",
}

def analyze_image_provenance(image_bytes: Optional[bytes]) -> Dict[str, Any]:
    """
    Extracts provenance and synthetic generator signals from image bytes.
    Safe-fails with neutral provenance if bytes are missing or corrupted.
    """
    if not image_bytes or len(image_bytes) < 32:
        return {
            "has_provenance_data": False,
            "is_synthetic": False,
            "detected_generators": [],
            "c2pa_present": False,
            "provenance_score": 0.0,
            "summary": "No image metadata available for provenance inspection."
        }

    detected_generators = set()
    raw_snippets = []
    c2pa_found = False
    software_tag = None
    has_exif = False

    # 1. Raw Byte Scanning for embedded signatures and C2PA markers
    try:
        lower_sample = image_bytes[: min(len(image_bytes), 1024 * 512)].lower()
        if b"c2pa" in lower_sample or b"content credentials" in lower_sample or b"urn:c2pa" in lower_sample:
            c2pa_found = True

        for key, label in KNOWN_GENERATORS.items():
            pattern = key.encode("utf-8")
            if pattern in lower_sample:
                detected_generators.add(label)
    except Exception as exc:
        logger.debug("Raw byte scan error: %s", exc)

    # 2. Structured Metadata via Pillow
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Check PNG text info (tEXt / iTXt)
        if hasattr(img, "info") and isinstance(img.info, dict):
            for info_k, info_v in img.info.items():
                if not isinstance(info_v, str):
                    continue
                v_lower = info_v.lower()
                
                # Stable Diffusion parameter dump check
                if info_k in ("parameters", "sd-metadata", "prompt", "workflow"):
                    detected_generators.add("Stable Diffusion / Prompt Pipeline")
                    raw_snippets.append(f"{info_k}: {info_v[:100]}...")

                for gen_key, gen_label in KNOWN_GENERATORS.items():
                    if gen_key in v_lower:
                        detected_generators.add(gen_label)
                        if gen_key in ("software", "comment", "description"):
                            software_tag = info_v[:80]

        # Check EXIF
        exif_data = img.getexif()
        if exif_data:
            has_exif = True
            for tag_id, val in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                val_str = str(val)
                val_lower = val_str.lower()
                
                if tag_name == "Software":
                    software_tag = val_str[:80]
                
                for gen_key, gen_label in KNOWN_GENERATORS.items():
                    if gen_key in val_lower:
                        detected_generators.add(gen_label)
                        raw_snippets.append(f"EXIF {tag_name}: {val_str[:80]}")

    except Exception as exc:
        logger.debug("Pillow metadata extraction error: %s", exc)

    # 3. Compute Composite Provenance Risk Score
    generators_list = sorted(detected_generators)
    is_synthetic = len(generators_list) > 0
    score = 0.0

    if is_synthetic:
        score = min(1.0, 0.65 + (0.15 * len(generators_list)))

    summary_parts = []
    if is_synthetic:
        summary_parts.append(f"Synthetic generation signature detected ({', '.join(generators_list)}).")
    elif c2pa_found:
        summary_parts.append("Digital provenance assertion (C2PA/Content Credentials) present.")
    elif software_tag:
        summary_parts.append(f"Standard editor/camera metadata present ({software_tag}).")
    elif has_exif:
        summary_parts.append("Standard camera EXIF metadata present.")
    else:
        summary_parts.append("Standard digital image without synthetic AI generation markers.")

    return {
        "has_provenance_data": bool(has_exif or software_tag or c2pa_found or is_synthetic),
        "is_synthetic": is_synthetic,
        "detected_generators": generators_list,
        "c2pa_present": c2pa_found,
        "software_tag": software_tag,
        "provenance_score": round(score, 2),
        "summary": " ".join(summary_parts),
        "metadata_snippets": raw_snippets[:3]
    }
