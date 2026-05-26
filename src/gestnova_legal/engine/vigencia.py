"""TTL and staleness helpers for legal knowledge."""
from datetime import date, timedelta

DEFAULT_NORM_TTL_DAYS = 30
DEFAULT_JURISPRUDENCE_TTL_DAYS = 90


def is_stale(verified_date: date, ttl_days: int | None = None, today: date | None = None) -> bool:
    today = today or date.today()
    ttl = ttl_days or DEFAULT_NORM_TTL_DAYS
    return (today - verified_date).days > ttl


def days_until_stale(verified_date: date, ttl_days: int | None = None, today: date | None = None) -> int:
    today = today or date.today()
    ttl = ttl_days or DEFAULT_NORM_TTL_DAYS
    return ttl - (today - verified_date).days


def ttl_for_type(content_type: str) -> int:
    if content_type == "jurisprudencia":
        return DEFAULT_JURISPRUDENCE_TTL_DAYS
    return DEFAULT_NORM_TTL_DAYS
