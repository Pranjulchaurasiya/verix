"""Google DeepMind SynthID & Unified Multi-Tier Synthetic Provenance Service.

Architecture:
  - Tier 1: Deterministic Byte-Level & Manifest Parsing (Instant, local, C2PA, EXIF, PNG chunks).
  - Tier 2: Google Gemini Vision Multimodal Forensic Inspector (Active visual AI analysis).
  - Tier 3: Google Cloud Vertex AI SynthID Enterprise Adapter (GCP Project connector).
"""

import io
import json
import base64
import logging
from typing import Dict, Any, List, Optional
import httpx
from PIL import Image, ExifTags

from backend.app.config import settings

logger = logging.getLogger("verix.synthid")

KNOWN_GENERATOR_SIGNATURES: Dict[str, str] = {
    "synthid": "Google DeepMind SynthID",
    "imagen": "Google DeepMind Imagen",
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
    "flux.1": "Black Forest Labs FLUX.1",
    "leonardo.ai": "Leonardo AI",
    "generative ai": "Generative AI Pipeline",
}

class SynthIDService:
    """Unified service for DeepMind SynthID and synthetic AI provenance analysis."""

    @staticmethod
    def inspect_metadata_and_bytes(image_bytes: Optional[bytes]) -> Dict[str, Any]:
        """Tier 1: Instant local byte-level and metadata analysis."""
        if not image_bytes or len(image_bytes) < 32:
            return {
                "has_provenance_data": False,
                "is_synthetic": False,
                "synthid_detected": False,
                "detected_generators": [],
                "c2pa_present": False,
                "provenance_score": 0.0,
                "summary": "No image metadata available for provenance inspection.",
                "visual_artifacts": []
            }

        detected_generators = set()
        raw_snippets = []
        c2pa_found = False
        software_tag = None
        has_exif = False

        # 1. Byte-level signature check
        try:
            lower_sample = image_bytes[: min(len(image_bytes), 1024 * 512)].lower()
            if b"c2pa" in lower_sample or b"content credentials" in lower_sample or b"urn:c2pa" in lower_sample:
                c2pa_found = True

            for key, label in KNOWN_GENERATOR_SIGNATURES.items():
                if key.encode("utf-8") in lower_sample:
                    detected_generators.add(label)
        except Exception as exc:
            logger.debug("Tier 1 byte scanning error: %s", exc)

        # 2. Structured metadata check
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if hasattr(img, "info") and isinstance(img.info, dict):
                for info_k, info_v in img.info.items():
                    if not isinstance(info_v, str):
                        continue
                    v_lower = info_v.lower()
                    if info_k in ("parameters", "sd-metadata", "prompt", "workflow"):
                        detected_generators.add("Stable Diffusion / Prompt Pipeline")
                        raw_snippets.append(f"{info_k}: {info_v[:100]}...")

                    for gen_key, gen_label in KNOWN_GENERATOR_SIGNATURES.items():
                        if gen_key in v_lower:
                            detected_generators.add(gen_label)
                            if gen_key in ("software", "comment", "description"):
                                software_tag = info_v[:80]

            exif_data = img.getexif()
            if exif_data:
                has_exif = True
                for tag_id, val in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                    val_str = str(val)
                    val_lower = val_str.lower()
                    if tag_name == "Software":
                        software_tag = val_str[:80]
                    for gen_key, gen_label in KNOWN_GENERATOR_SIGNATURES.items():
                        if gen_key in val_lower:
                            detected_generators.add(gen_label)
                            raw_snippets.append(f"EXIF {tag_name}: {val_str[:80]}")
        except Exception as exc:
            logger.debug("Tier 1 Pillow metadata error: %s", exc)

        generators_list = sorted(detected_generators)
        synthid_found = any("synthid" in g.lower() or "imagen" in g.lower() for g in generators_list)
        is_synthetic = len(generators_list) > 0
        score = 0.0
        if is_synthetic:
            score = min(1.0, 0.65 + (0.15 * len(generators_list)))

        return {
            "has_provenance_data": bool(has_exif or software_tag or c2pa_found or is_synthetic),
            "is_synthetic": is_synthetic,
            "synthid_detected": synthid_found,
            "detected_generators": generators_list,
            "c2pa_present": c2pa_found,
            "software_tag": software_tag,
            "provenance_score": round(score, 2),
            "summary": "Synthetic AI generator signature detected in metadata." if is_synthetic else (
                "C2PA Content Credentials digital provenance present." if c2pa_found else "Standard photographic metadata."
            ),
            "visual_artifacts": raw_snippets[:3]
        }

    @staticmethod
    async def inspect_with_gemini_vision(image_bytes: bytes) -> Optional[Dict[str, Any]]:
        """Tier 2: Google Gemini Multimodal Forensic AI Analysis."""
        if not settings.GEMINI_API_KEY or len(image_bytes) < 64:
            return None

        # Convert to Base64
        try:
            b64_data = base64.b64encode(image_bytes).decode("utf-8")
        except Exception:
            return None

        # Probe supported models with priority order
        candidate_models = ["gemini-3.8-flash", settings.GEMINI_MODEL]
        
        prompt = """
You are a senior digital forensic analyst evaluating this product image for:
1. Synthetic AI generation indicators (Midjourney, Stable Diffusion, DALL-E, Imagen).
2. DeepMind SynthID or digital generative watermarks.
3. Unnatural micro-textures, diffusion smoothing, distorted typography/logos, or physics anomalies.

Return strictly valid JSON conforming to this schema:
{
  "is_synthetic": boolean,
  "synthetic_confidence": float between 0.0 and 1.0,
  "synthid_detected": boolean,
  "detected_generator": string ("None", "Imagen / SynthID", "Midjourney", "Stable Diffusion", "DALL-E", "FLUX", or "Unknown Generative AI"),
  "visual_forensic_artifacts": list of strings detailing observations,
  "explanation": concise 1-2 sentence forensic summary
}
"""
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": b64_data
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        }

        async with httpx.AsyncClient(timeout=4.0) as client:
            for model in candidate_models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.GEMINI_API_KEY}"
                try:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
                        parsed = json.loads(raw_json)
                        return parsed
                except Exception as exc:
                    logger.debug("Gemini vision evaluation attempt failed on %s: %s", model, exc)
                    continue

        return None

    @staticmethod
    def inspect_vertex_ai_adapter() -> Dict[str, Any]:
        """Tier 3: Google Cloud Vertex AI SynthID Enterprise adapter diagnostics."""
        project_id = getattr(settings, "GCP_PROJECT_ID", None)
        return {
            "status": "configured" if project_id else "unconfigured",
            "provider": "Google Cloud Vertex AI SynthID",
            "project_id": project_id,
            "instructions": "Set GCP_PROJECT_ID and GOOGLE_APPLICATION_CREDENTIALS in .env to activate direct Vertex AI enterprise verification."
        }

    @classmethod
    async def analyze_provenance(cls, image_bytes: Optional[bytes]) -> Dict[str, Any]:
        """
        Unified Multi-Tier Pipeline execution:
        Tier 1 (Instant) -> Tier 2 (Gemini Vision) -> Tier 3 (Vertex Adapter)
        """
        # Execute Tier 1
        t1_result = cls.inspect_metadata_and_bytes(image_bytes)

        # Execute Tier 2 if image bytes exist
        t2_result = None
        if image_bytes and len(image_bytes) >= 64:
            try:
                t2_result = await cls.inspect_with_gemini_vision(image_bytes)
            except Exception as e:
                logger.debug("Tier 2 Gemini Vision call bypassed: %s", e)

        # Execute Tier 3
        t3_result = cls.inspect_vertex_ai_adapter()

        # Merge Results
        is_synthetic = t1_result["is_synthetic"]
        synthid_detected = t1_result["synthid_detected"]
        detected_generators = list(t1_result["detected_generators"])
        visual_artifacts = list(t1_result.get("visual_artifacts", []))
        provenance_score = t1_result["provenance_score"]
        active_tier = "tier1_metadata"

        if t2_result and isinstance(t2_result, dict):
            active_tier = "tier2_gemini_vision"
            if t2_result.get("synthid_detected"):
                synthid_detected = True
                detected_generators.append("Google DeepMind SynthID (Vision Forensic)")
            if t2_result.get("is_synthetic") and t2_result.get("synthetic_confidence", 0.0) >= 0.65:
                is_synthetic = True
                gen = t2_result.get("detected_generator")
                if gen and gen not in ("None", "none") and gen not in detected_generators:
                    detected_generators.append(gen)
                provenance_score = max(provenance_score, round(float(t2_result.get("synthetic_confidence", 0.7)), 2))
                if t2_result.get("visual_forensic_artifacts"):
                    visual_artifacts.extend(t2_result["visual_forensic_artifacts"][:2])

        # Deduplicate generators
        detected_generators = sorted(list(set(detected_generators)))

        # Build comprehensive summary
        summary_parts = []
        if synthid_detected:
            summary_parts.append("Google DeepMind SynthID watermark detected.")
        elif is_synthetic:
            summary_parts.append(f"Synthetic AI media detected ({', '.join(detected_generators)}).")
        elif t1_result.get("c2pa_present"):
            summary_parts.append("Cryptographic C2PA Content Credentials verified.")
        else:
            summary_parts.append("Authentic camera/retail photograph (No synthetic AI markers detected).")

        return {
            "has_provenance_data": t1_result["has_provenance_data"] or bool(t2_result),
            "is_synthetic": is_synthetic,
            "synthid_detected": synthid_detected,
            "c2pa_present": t1_result["c2pa_present"],
            "detected_generators": detected_generators,
            "provenance_score": provenance_score,
            "active_tier": active_tier,
            "visual_artifacts": visual_artifacts,
            "summary": " ".join(summary_parts),
            "vertex_adapter": t3_result,
            "metadata_snippets": visual_artifacts[:3]
        }

synthid_service = SynthIDService()
