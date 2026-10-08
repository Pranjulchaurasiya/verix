# Security Policy

## Supported Versions

We actively maintain and provide security patches for the following versions of Verix:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0.0 | :x:                |

## Security Architecture & Defenses

Verix processes untrusted web inputs, third-party search indexes, and user-provided image assets. The system enforces strict defense-in-depth boundaries:

1. **Server-Side Request Forgery (SSRF) Firewall:**
   - All inbound URLs submitted for image extraction are validated via `_validate_public_url()`.
   - Protocol schemes are strictly limited to `http` and `https`.
   - Hostnames are resolved via DNS to inspect candidate IP addresses. Requests to private networks (`RFC 1918`), loopback (`127.0.0.0/8`, `::1`), link-local, multicast, or reserved ranges are actively rejected prior to socket connection.
   - Redirect chains are capped at 4 hops, with each hop independently audited against the SSRF firewall before traversal.

2. **Tamper-Evident Cryptographic Anchoring:**
   - Search evidence manifests are canonically serialized (`RFC 8785`) and signed using RFC 8032 **Ed25519** asymmetric cryptography.
   - Granular search evidence leaves are compiled into a binary **Merkle Tree**, providing verifiable inclusion proofs (`SHA-256`) that can be validated offline via `verify_evidence_cli.py`.
   - Retroactive modification of search snapshots or timestamps is cryptographically detectable.

3. **Prompt Injection & Non-Accusatory Sanitization:**
   - User inputs and remote page titles undergo control-character stripping and injection mitigation before optional LLM evaluation.
   - User-facing descriptions strictly adhere to an objective risk policy, prohibiting unsubstantiated or libelous claims (`scam`, `fraud`, `fake`, `criminal`).

4. **Webhook Security:**
   - Outbound webhooks are authenticated via HMAC-SHA256 signatures (`X-Verix-Signature: t={timestamp},v1={hash}`).
   - Payloads include a Unix timestamp with strict tolerance checks to mitigate replay attacks.

## Reporting a Vulnerability

If you discover a security vulnerability in Verix, please do **not** open a public issue. Instead, report it privately:

- **Email:** security@verix.ai (or submit via GitHub Private Security Advisory)
- **Response SLA:** Within 48 hours for acknowledgment and severity triage.
- **Remediation SLA:** Within 7 days for critical vulnerabilities (CVSS >= 9.0).

Please include:
- A description of the vulnerability and potential impact.
- Step-by-step reproduction instructions or a minimal Proof of Concept (PoC).
- Any proposed remediation patches.
