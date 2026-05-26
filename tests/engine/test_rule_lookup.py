"""Tests for RuleLookup."""
from datetime import date

import pytest
from gestnova_legal.engine.rule_lookup import NoRuleApplicable, RuleLookup


def test_supported_countries(lookup):
    countries = lookup.supported_countries()
    assert "ES" in countries
    assert "EU" in countries
    assert "MX" in countries


def test_get_es_compliance(lookup, today):
    rule = lookup.get("ES", "legal_compliance_requirements", today)
    assert rule.country == "ES"
    assert "rules" in rule.data


def test_get_es_laboral(lookup, today):
    rule = lookup.get("ES", "labor_vacaciones", today)
    assert rule.data["articulo"] == "38"


def test_get_eu_regulation(lookup, today):
    rule = lookup.get("EU", "eu_regulation_gdpr", today)
    assert rule.data["celex"] == "32016R0679"


def test_get_mx_laboral(lookup, today):
    rule = lookup.get("MX", "labor_vacaciones_mx", today)
    assert "LFT" in rule.data["abreviatura"]


def test_unknown_country_raises(lookup, today):
    with pytest.raises(NoRuleApplicable, match="not loaded"):
        lookup.get("FR", "anything", today)


def test_unknown_rule_raises(lookup, today):
    with pytest.raises(NoRuleApplicable, match="not defined"):
        lookup.get("ES", "nonexistent_rule", today)


def test_search_by_keyword(lookup, today):
    results = lookup.search_by_keyword("ES", "vacaciones", today)
    assert len(results) >= 1
    assert any("vacaciones" in r.rule for r in results)


def test_get_all_for_area(lookup, today):
    results = lookup.get_all_for_area("ES", "labor_", today)
    assert len(results) >= 2
