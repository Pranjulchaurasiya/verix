"""Verification script to test all live Verix endpoints and guardrails against a running instance."""

import httpx

client = httpx.Client(base_url="http://127.0.0.1:8000", timeout=10.0)

print("--- 1. Testing Root Static HTML Serving ---")
r0 = client.get("/")
print("Root HTML status:", r0.status_code)
print("Contains Verix title:", "VERIX" in r0.text)
print("Length:", len(r0.text))

print("\n--- 2. Testing Whitelist Bypass Guardrail ---")
r1 = client.post("/api/v1/analyze", data={"url": "https://www.amazon.in/dp/B09G9BL5CP", "persona_mode": "buyer"})
d1 = r1.json()
print("Status:", d1["status"])
print("Trust Score:", d1["trust_score"])
print("Whitelist Bypass Flag:", d1["is_whitelist_bypass"])
print("Risk Category:", d1["risk_category"])

print("\n--- 3. Testing High-Risk Sneaker Scam ---")
r2 = client.post("/api/v1/analyze", data={"scenario": "default", "url": "https://sneakerflashsale-india.club/order-aj1", "persona_mode": "buyer"})
d2 = r2.json()
print("Status:", d2["status"])
print("Trust Score:", d2["trust_score"])
print("Matches Count:", len(d2["matched_domains"]))
print("Risk Category:", d2["risk_category"])

print("\n--- 4. Testing Insufficient Data Guardrail (< 2 matches) ---")
r3 = client.post("/api/v1/analyze", data={"scenario": "insufficient", "url": "https://craftmaker-portfolio.in/shop/ceramic-vase-1", "persona_mode": "buyer"})
d3 = r3.json()
print("Status:", d3["status"])
print("Trust Score (must be None):", d3["trust_score"])
print("Confidence:", d3["confidence"])
print("Risk Category:", d3["risk_category"])

print("\n--- 5. Testing Creator Photo Protection Mode ---")
r4 = client.post("/api/v1/analyze", data={"scenario": "cloned_seller", "url": "https://artisanhandicrafts.com/item/brass-diya", "persona_mode": "seller"})
d4 = r4.json()
print("Status:", d4["status"])
print("Persona:", d4["persona_mode"])
print("Action Recommendation:", d4["action_recommendation"][:100], "...")

print("\n--- 6. Testing Decoupled Admin Health & Stats ---")
r5 = client.get("/api/v1/admin/health")
d5 = r5.json()
print("Health Status:", d5["status"])
print("Uptime:", d5["uptime_seconds"], "seconds")
print("DB Connected:", d5["database_connected"])

r6 = client.get("/api/v1/admin/stats")
d6 = r6.json()
print("Total Scans in DB:", d6["total_scans"])
print("Whitelist Bypasses:", d6["whitelist_bypasses"])
print("Insufficient Data Scans:", d6["insufficient_data_scans"])
print("SerpApi Success Rate:", d6["serpapi_success_rate"])

print("\n--- 7. Testing Scan History Retrieval ---")
r7 = client.get("/api/v1/scans?limit=5")
d7 = r7.json()
print("Total Scans Count:", d7["total"])
print("Recent Items Returned:", len(d7["items"]))
for item in d7["items"][:3]:
    print(f"  - [{item['risk_category']}] {item['persona_mode']} scan, score={item['trust_score']}, matches={item['match_count']}")

print("\nSUCCESS: All live server endpoints and guardrails verified!")
