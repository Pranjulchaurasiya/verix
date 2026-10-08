"""Seller Asset Protection & Evidentiary Takedown Notice Generator.

Empowers original catalog creators, brands, and sellers to defend proprietary product photography
by turning SerpApi reverse-image matches into legally structured, cryptographically anchored
DMCA / VeRO infringement notices.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import hashlib
from backend.app.services.audit_merkle import MerkleTree, sign_audit_manifest, get_public_key_hex

def generate_takedown_package(
    scan_id: str,
    image_hash: str,
    matched_domains: List[Dict[str, Any]],
    claimant_name: Optional[str] = None,
    product_title: Optional[str] = None,
    original_work_url: Optional[str] = None,
    base_verification_url: str = "https://verix.dev"
) -> Dict[str, Any]:
    """
    Constructs a complete, legally formatted, cryptographically signed takedown notice.
    """
    c_name = claimant_name or "Authorized Catalog Owner / Brand Rights Holder"
    p_title = product_title or "Original Proprietary Product Photography"
    
    # Extract unauthorized / non-whitelisted commercial URLs
    infringing_items = []
    for m in matched_domains:
        link = m.get("link") or m.get("url") or ""
        domain = m.get("domain") or "unspecified"
        is_wl = m.get("is_whitelisted", False)
        if link and not is_wl:
            infringing_items.append({
                "domain": domain,
                "url": link,
                "title": m.get("title") or "Commercial listing",
                "price": m.get("price") or m.get("extracted_price")
            })

    # Prepare Merkle tree over the evidence set
    leaves = [
        {"claimant": c_name, "image_hash": image_hash},
        {"original_work": p_title, "original_url": original_work_url or "proprietary_catalog"},
        {"infringing_count": len(infringing_items), "evidence_provider": "SerpApi Google Lens"},
        {"infringing_urls": [it["url"] for it in infringing_items[:10]]}
    ]
    tree = MerkleTree(leaves)

    now_iso = datetime.now(timezone.utc).isoformat()
    manifest = {
        "scan_id": scan_id,
        "merkle_root": tree.root,
        "type": "DMCA_TAKEDOWN_EVIDENCE_V1",
        "timestamp": now_iso
    }
    sig_info = sign_audit_manifest(manifest)

    # Compile the formal statutory notice text
    infringing_url_list_txt = "\n".join([f"  * {it['domain']}: {it['url']}" for it in infringing_items]) or "  * [No unauthorized external links detected]"

    notice_text = f"""NOTICE OF COPYRIGHT INFRINGEMENT AND DEMAND FOR EXPEDITIOUS REMOVAL
Pursuant to 17 U.S.C. § 512(c) (DMCA) / Platform VeRO / Brand Protection Guidelines

Date: {datetime.now(timezone.utc).strftime('%B %d, %Y')}
Case Evidence ID: VERIX-{scan_id[:8].upper()}

To the Designated Abuse Desk / Marketplace Rights Enforcement Team:

I am contacting you on behalf of {c_name}, the owner of exclusive copyrights in the original commercial product photography and catalog media described below.

1. IDENTIFICATION OF COPYRIGHTED WORK:
Description: {p_title}
Original Catalog Reference: {original_work_url or 'Proprietary merchant photo studio asset'}
Digital Perceptual Image Fingerprint (SHA-256): {image_hash}

2. IDENTIFICATION OF INFRINGING MATERIAL:
The following listings display, distribute, or reproduce the copyrighted product photography without license, permission, or authorization:
{infringing_url_list_txt}

3. INDEPENDENT SEARCH & REVERSE-IMAGE EVIDENCE:
This material was detected and corroborated via SerpApi reverse-image indexing across public web search engines.
Cryptographic Merkle Root: {tree.root}
Ed25519 Evidence Signature: {sig_info['signature_hex']}
Public Key ID: {sig_info['key_id']}
Independent Verification URL: {base_verification_url}/api/v1/audit/dossier/{scan_id}

4. STATUTORY DECLARATIONS:
- I have a good-faith belief that the use of the material in the manner complained of is not authorized by the copyright owner, its agent, or the law.
- The information in this notification is accurate, and under penalty of perjury, I declare that I am authorized to act on behalf of the owner of an exclusive right that is allegedly infringed.

Sincerely,
{c_name}
Authenticity & Evidence Hash: {sig_info['payload_digest']}
Automated Evidence Engine: Verix Authenticity Intelligence (SerpApi Hackathon 2026)
"""

    return {
        "case_id": f"VERIX-{scan_id[:8].upper()}",
        "scan_id": scan_id,
        "created_at": now_iso,
        "claimant_name": c_name,
        "infringing_count": len(infringing_items),
        "infringing_items": infringing_items,
        "merkle_root": tree.root,
        "signature": sig_info,
        "notice_text": notice_text.strip(),
        "platform_channels": {
            "amazon": "https://brandregistry.amazon.com/brand-protection",
            "ebay": "https://www.ebay.com/help/policies/member-behavior-policies/report-intellectual-property-infringements-vero?id=4349",
            "google_dmca": "https://www.google.com/webmasters/tools/dmca-notice",
            "shopify": "https://www.shopify.com/legal/dmca"
        }
    }
