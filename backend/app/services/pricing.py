"""Multi-Retailer Pricing Anomaly & Outlier Distribution Engine.

Performs robust statistical dispersion analysis (IQR, Median, MAD, Modified Z-score)
and currency normalization across SerpApi Google Lens and Shopping matches to detect
bait-and-switch counterfeit pricing and predatory price gouging.
"""

from typing import List, Dict, Any, Optional
import statistics
import re

# Standard FX rates to USD (updated benchmark reference)
FX_RATES_TO_USD: Dict[str, float] = {
    "USD": 1.0,
    "$": 1.0,
    "EUR": 1.08,
    "€": 1.08,
    "GBP": 1.28,
    "£": 1.28,
    "INR": 0.012,
    "₹": 0.012,
    "CAD": 0.74,
    "AUD": 0.65,
    "JPY": 0.0066,
    "CNY": 0.14
}

def parse_price_and_currency(raw_price: Any, currency_hint: Optional[str] = None) -> Optional[tuple[float, str]]:
    """Extracts numeric float and standardized currency symbol."""
    if raw_price is None:
        return None
    
    if isinstance(raw_price, (int, float)):
        curr = currency_hint or "USD"
        return (float(raw_price), curr)

    s = str(raw_price).strip()
    if not s:
        return None

    # Detect currency symbol
    detected_curr = "USD"
    for symbol in ["₹", "INR", "€", "EUR", "£", "GBP", "$", "USD", "CAD", "AUD", "JPY", "CNY"]:
        if symbol in s:
            detected_curr = symbol
            break
    if currency_hint and currency_hint in FX_RATES_TO_USD:
        detected_curr = currency_hint

    # Clean numeric string
    # Remove currency symbols and non-numeric chars except digits and dot/comma
    clean = re.sub(r"[^\d.,]", "", s)
    if not clean:
        return None

    # Handle commas vs periods in international pricing
    if "," in clean and "." in clean:
        clean = clean.replace(",", "")
    elif "," in clean:
        # If single comma followed by 2 digits, it's a decimal (e.g. 19,99)
        parts = clean.split(",")
        if len(parts) == 2 and len(parts[1]) in [1, 2]:
            clean = f"{parts[0]}.{parts[1]}"
        else:
            clean = clean.replace(",", "")

    try:
        val = float(clean)
        return (val, detected_curr)
    except ValueError:
        return None


def normalize_to_usd(amount: float, currency: str) -> float:
    """Converts price to USD using benchmark FX table."""
    rate = FX_RATES_TO_USD.get(currency.upper(), FX_RATES_TO_USD.get(currency, 1.0))
    return round(amount * rate, 2)


def analyze_price_distribution(matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes interquartile range (IQR), median, and modified Z-scores across all priced matches.
    Flags statistical outliers (severe low pricing = counterfeit risk; extreme high = gouging).
    """
    priced_items = []

    for m in matches:
        raw_price = m.get("extracted_price") if m.get("extracted_price") is not None else m.get("price")
        parsed = parse_price_and_currency(raw_price, m.get("currency"))
        if parsed and parsed[0] > 0:
            val, curr = parsed
            usd_val = normalize_to_usd(val, curr)
            if usd_val > 0.05:  # Filter out trivial noise/zero values
                priced_items.append({
                    "domain": m.get("domain", "unknown"),
                    "title": m.get("title", "Listing"),
                    "link": m.get("link") or m.get("url"),
                    "original_price": round(val, 2),
                    "original_currency": curr,
                    "usd_price": usd_val,
                    "is_whitelisted": m.get("is_whitelisted", False)
                })

    if len(priced_items) < 3:
        return {
            "has_pricing_data": len(priced_items) > 0,
            "sample_size": len(priced_items),
            "median_usd": priced_items[0]["usd_price"] if priced_items else None,
            "mean_usd": priced_items[0]["usd_price"] if priced_items else None,
            "iqr_usd": None,
            "lower_bound_usd": None,
            "upper_bound_usd": None,
            "has_pricing_anomaly": False,
            "anomaly_summary": "Insufficient multi-retailer pricing samples to compute dispersion bounds.",
            "priced_listings": priced_items
        }

    usd_prices = sorted([it["usd_price"] for it in priced_items])
    n = len(usd_prices)

    # Median and Quartiles
    median_val = statistics.median(usd_prices)
    mean_val = statistics.mean(usd_prices)

    # Q1 and Q3 via quantiles
    q1 = statistics.quantiles(usd_prices, n=4)[0] if n >= 4 else usd_prices[0]
    q3 = statistics.quantiles(usd_prices, n=4)[2] if n >= 4 else usd_prices[-1]
    iqr = max(0.01, q3 - q1)

    lower_fence = max(0.0, q1 - (1.5 * iqr))
    upper_fence = q3 + (1.5 * iqr)

    # Median Absolute Deviation (MAD) for robust modified Z-scores
    deviations = [abs(x - median_val) for x in usd_prices]
    mad = statistics.median(deviations) or (iqr / 1.349) or 1.0

    flagged_outliers = []
    enriched_listings = []
    severe_discount_detected = False

    for it in priced_items:
        p = it["usd_price"]
        mod_z = round(0.6745 * (p - median_val) / mad, 2)
        it["modified_z_score"] = mod_z

        is_low_outlier = p < lower_fence or (median_val > 0 and (p / median_val) < 0.40)
        is_high_outlier = p > upper_fence

        it["is_outlier"] = is_low_outlier or is_high_outlier
        if is_low_outlier:
            it["anomaly_type"] = "severe_discount_counterfeit_risk"
            flagged_outliers.append(it)
            severe_discount_detected = True
        elif is_high_outlier:
            it["anomaly_type"] = "price_gouging_anomaly"
            flagged_outliers.append(it)
        else:
            it["anomaly_type"] = "within_normal_distribution"

        enriched_listings.append(it)

    summary_parts = []
    if severe_discount_detected:
        summary_parts.append(
            f"Detected statistical pricing outlier(s) priced >60% below the retail market median ($${median_val:.2f} USD). "
            f"Severe price collapse often signals counterfeit reproduction or bait-and-switch merchandise."
        )
    elif len(flagged_outliers) > 0:
        summary_parts.append(
            f"Pricing dispersion identified {len(flagged_outliers)} outlier listing(s) deviating from market median ($${median_val:.2f} USD)."
        )
    else:
        summary_parts.append(
            f"Retailer prices fall within normal market distribution (Median: $${median_val:.2f} USD, IQR: $${iqr:.2f})."
        )

    return {
        "has_pricing_data": True,
        "sample_size": n,
        "median_usd": round(median_val, 2),
        "mean_usd": round(mean_val, 2),
        "iqr_usd": round(iqr, 2),
        "q1_usd": round(q1, 2),
        "q3_usd": round(q3, 2),
        "lower_bound_usd": round(lower_fence, 2),
        "upper_bound_usd": round(upper_fence, 2),
        "has_pricing_anomaly": len(flagged_outliers) > 0,
        "severe_discount_detected": severe_discount_detected,
        "outlier_count": len(flagged_outliers),
        "anomaly_summary": " ".join(summary_parts),
        "priced_listings": enriched_listings
    }
