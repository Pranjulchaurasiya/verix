"""Product availability guidance kept separate from authenticity scoring."""


def append_availability_guidance(recommendation: str, availability: str | None) -> str:
    if availability == "discontinued":
        note = "Availability signal: the retailer marks this product as discontinued. This does not prove inauthenticity; verify current stock, warranty, and seller claims before purchasing."
    elif availability == "out_of_stock":
        note = "Availability signal: the retailer marks this product as unavailable. Confirm current stock and seller claims before purchasing."
    else:
        return recommendation

    if note in recommendation:
        return recommendation
    return f"{recommendation.rstrip()} {note}"
