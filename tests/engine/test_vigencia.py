"""Tests for vigencia helpers."""
from datetime import date

from gestnova_legal.engine.vigencia import (
    DEFAULT_NORM_TTL_DAYS,
    days_until_stale,
    is_stale,
    ttl_for_type,
)


def test_fresh_is_not_stale():
    assert not is_stale(date(2026, 5, 1), today=date(2026, 5, 15))


def test_old_is_stale():
    assert is_stale(date(2026, 3, 1), today=date(2026, 5, 15))


def test_custom_ttl():
    assert not is_stale(date(2026, 3, 1), ttl_days=90, today=date(2026, 5, 15))


def test_days_until_stale():
    days = days_until_stale(date(2026, 5, 1), today=date(2026, 5, 15))
    assert days == DEFAULT_NORM_TTL_DAYS - 14


def test_ttl_for_jurisprudencia():
    assert ttl_for_type("jurisprudencia") == 90


def test_ttl_for_norma():
    assert ttl_for_type("norma") == 30
