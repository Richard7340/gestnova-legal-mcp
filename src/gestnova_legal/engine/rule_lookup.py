"""Load YAML packs and resolve rules by (country, key, date)."""
from datetime import date
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel
from ruamel.yaml import YAML


class Rule(BaseModel):
    rule: str
    country: str
    effective_from: date
    effective_until: Optional[date] = None
    source: str
    data: Any
    region: Optional[str] = None


class NoRuleApplicable(Exception):
    def __init__(self, country: str, key: str, on_date: date, hint: str = ""):
        self.country = country
        self.key = key
        self.on_date = on_date
        self.hint = hint
        super().__init__(f"No rule '{key}' for {country} on {on_date}. {hint}")


class RuleLookup:
    def __init__(self, packs_root: Path):
        self._packs_root = Path(packs_root)
        self._rules: dict[tuple[str, str], list[Rule]] = {}
        self._countries: set[str] = set()
        self._load()

    def _load(self) -> None:
        yaml = YAML(typ="safe")
        if not self._packs_root.exists():
            return
        for country_dir in self._packs_root.iterdir():
            if not country_dir.is_dir():
                continue
            country = country_dir.name.upper()
            self._countries.add(country)
            for yaml_path in country_dir.rglob("*.yaml"):
                parts = yaml_path.relative_to(country_dir).parts
                inferred_region = None
                if len(parts) >= 2 and parts[0] == "regions":
                    inferred_region = parts[1]
                raw = yaml.load(yaml_path.read_text(encoding="utf-8"))
                if not raw:
                    continue
                for entry in raw:
                    if "region" not in entry and inferred_region:
                        entry["region"] = inferred_region
                    rule = Rule(**entry)
                    key = (rule.country, rule.rule)
                    self._rules.setdefault(key, []).append(rule)
        for k in self._rules:
            self._rules[k].sort(key=lambda r: r.effective_from, reverse=True)

    def supported_countries(self) -> list[str]:
        return sorted(self._countries)

    def get(self, country: str, key: str, on_date: date, region: Optional[str] = None) -> Rule:
        candidates = self._rules.get((country, key), [])
        if not candidates:
            if country not in self._countries:
                raise NoRuleApplicable(country, key, on_date, hint=f"Country '{country}' not loaded.")
            raise NoRuleApplicable(country, key, on_date, hint=f"Rule '{key}' not defined for {country}.")
        if region:
            for rule in candidates:
                if (
                    rule.region == region
                    and rule.effective_from <= on_date
                    and (rule.effective_until is None or on_date <= rule.effective_until)
                ):
                    return rule
        for rule in candidates:
            if (
                rule.region is None
                and rule.effective_from <= on_date
                and (rule.effective_until is None or on_date <= rule.effective_until)
            ):
                return rule
        raise NoRuleApplicable(
            country, key, on_date,
            hint=f"No vigencia covers {on_date.isoformat()}. Most recent: {candidates[0].effective_from.isoformat()}.",
        )

    def get_all_for_area(self, country: str, key_prefix: str, on_date: date) -> list[Rule]:
        result = []
        for (c, k), _rules in self._rules.items():
            if c == country and k.startswith(key_prefix):
                try:
                    result.append(self.get(c, k, on_date))
                except NoRuleApplicable:
                    continue
        return result

    def search_by_keyword(self, country: str, keyword: str, on_date: date) -> list[Rule]:
        kw = keyword.lower()
        result = []
        for (c, k), _rules in self._rules.items():
            if c != country:
                continue
            if kw in k.lower():
                try:
                    result.append(self.get(c, k, on_date))
                except NoRuleApplicable:
                    continue
                continue
            for rule in _rules:
                if (
                    rule.effective_from <= on_date
                    and (rule.effective_until is None or on_date <= rule.effective_until)
                    and kw in str(rule.data).lower()
                ):
                    result.append(rule)
                    break
        return result


_lookup: RuleLookup | None = None


def get_lookup() -> RuleLookup:
    global _lookup
    if _lookup is None:
        packs = Path(__file__).resolve().parent.parent.parent.parent / "packs"
        _lookup = RuleLookup(packs)
    return _lookup


def reset_lookup() -> None:
    global _lookup
    _lookup = None


def init_lookup(packs_root: Path) -> RuleLookup:
    global _lookup
    _lookup = RuleLookup(packs_root)
    return _lookup
