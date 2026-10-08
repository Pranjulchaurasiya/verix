import pytest
from backend.app.services.pricing import (
    parse_price_and_currency, normalize_to_usd, analyze_price_distribution
)

def test_parse_price_and_currency():
    assert parse_price_and_currency("$129.99") == (129.99, "$")
    assert parse_price_and_currency("₹4,999") == (4999.0, "₹")
    assert parse_price_and_currency("€89,50") == (89.5, "€")
    assert parse_price_and_currency("£45.00") == (45.0, "£")
    assert parse_price_and_currency(None) is None
    assert parse_price_and_currency("Free") is None

def test_normalize_to_usd():
    assert normalize_to_usd(100.0, "USD") == 100.0
    assert normalize_to_usd(100.0, "EUR") == 108.0
    assert normalize_to_usd(1000.0, "INR") == 12.0

def test_analyze_price_distribution_few_samples():
    matches = [
        {"domain": "shop1.com", "price": "$100"},
        {"domain": "shop2.com", "price": "$110"}
    ]
    res = analyze_price_distribution(matches)
    assert res["has_pricing_data"] is True
    assert res["sample_size"] == 2
    assert res["iqr_usd"] is None
    assert res["has_pricing_anomaly"] is False

def test_analyze_price_distribution_with_counterfeit_outlier():
    # Regular market price around $150, but one suspicious listing at $15 (90% discount)
    matches = [
        {"domain": "official-store.com", "price": "$150", "is_whitelisted": True},
        {"domain": "retailer-b.com", "price": "$155", "is_whitelisted": False},
        {"domain": "retailer-c.com", "price": "$145", "is_whitelisted": False},
        {"domain": "retailer-d.com", "price": "$160", "is_whitelisted": False},
        {"domain": "sketchy-outlet.xyz", "price": "$15", "is_whitelisted": False}
    ]
    res = analyze_price_distribution(matches)
    assert res["has_pricing_data"] is True
    assert res["sample_size"] == 5
    assert res["median_usd"] == 150.0
    assert res["has_pricing_anomaly"] is True
    assert res["severe_discount_detected"] is True

    # Check sketchy outlet listing was flagged as severe_discount_counterfeit_risk
    sketchy = next(it for it in res["priced_listings"] if it["domain"] == "sketchy-outlet.xyz")
    assert sketchy["is_outlier"] is True
    assert sketchy["anomaly_type"] == "severe_discount_counterfeit_risk"
    assert sketchy["modified_z_score"] < -2.0
