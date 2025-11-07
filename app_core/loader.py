# I acknowledge using ChatGPT (GPT-5 Thinking) as a reviewer for structure/QA.
# Code is my own; no generated content is used in this file.

"""
CSV loaders for:
1) subjects↔classmarks    : subject,classmark
2) classmarks↔locations   : either
   - classmark,location
   - start_classmark,end_classmark,location

Normalization:
- Trim whitespace.
- Uppercase classmarks.
- Validate classmark format (1–2 letters) and location against allowed set.
- Expand ranges once at load time.

Outputs:
- load_subjects -> dict[classmark] = set(subjects)
- load_locations -> dict[classmark] = location
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, Set

from .classmark_range import expand_range, is_valid_classmark
from .constants import ALLOWED_LOCATIONS
from .errors import DataValidationError


def _read_csv(path: str | Path) -> Iterable[dict]:
    p = Path(path)
    if not p.exists():
        raise DataValidationError(f"CSV file not found: {p}")
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise DataValidationError(f"No header row in {p}")
        for i, row in enumerate(reader, start=2):  # header at line 1
            yield i, row  # include 1-based line number


def load_subjects(path: str | Path) -> Dict[str, Set[str]]:
    """Load 'subject,classmark' CSV into mapping: classmark -> set(subjects)."""
    rows = list(_read_csv(path))
    if not rows:
        raise DataValidationError(
            f"{path}: CSV must include header 'subject,classmark' and at least one data row."
        )
    header = {k.strip().lower() for k in rows[0][1].keys()}
    if header != {"subject", "classmark"}:
        raise DataValidationError(
            f"{path}: Expected headers exactly 'subject,classmark', " f"found: {sorted(header)}"
        )

    result: Dict[str, Set[str]] = {}
    for line_no, row in rows:
        subject = (row.get("subject") or "").strip()
        classmark = (row.get("classmark") or "").strip().upper()
        if not subject:
            raise DataValidationError(f"{path}:{line_no}: subject is empty")
        if not is_valid_classmark(classmark):
            raise DataValidationError(
                f"{path}:{line_no}: invalid classmark {classmark!r} " "(must be 1–2 letters A–Z)"
            )
        result.setdefault(classmark, set()).add(subject)
    return result


def load_locations(path: str | Path) -> Dict[str, str]:
    """Load locations CSV (per-classmark OR ranged) into mapping: classmark -> location."""
    rows = list(_read_csv(path))
    if not rows:
        raise DataValidationError(f"{path}: CSV must include a header and at least one data row.")

    header = [h.strip().lower() for h in rows[0][1].keys()]
    header_set = set(header)

    per_row = header_set == {"classmark", "location"}
    ranged = header_set == {"start_classmark", "end_classmark", "location"}

    if not (per_row or ranged):
        raise DataValidationError(
            f"{path}: Unexpected headers {sorted(header_set)}. "
            "Expected either ['classmark','location'] or "
            "['start_classmark','end_classmark','location']."
        )

    mapping: Dict[str, str] = {}

    if per_row:
        for line_no, row in rows:
            mark = (row.get("classmark") or "").strip().upper()
            loc = (row.get("location") or "").strip()
            if not is_valid_classmark(mark):
                raise DataValidationError(f"{path}:{line_no}: invalid classmark {mark!r}")
            if loc not in ALLOWED_LOCATIONS:
                raise DataValidationError(
                    f"{path}:{line_no}: invalid location {loc!r} "
                    f"(must be one of {ALLOWED_LOCATIONS})"
                )
            if mark in mapping and mapping[mark] != loc:
                raise DataValidationError(
                    f"{path}:{line_no}: conflicting location for {mark!r}: "
                    f"{mapping[mark]!r} vs {loc!r}"
                )
            mapping[mark] = loc
        return mapping

    # ranged schema
    for line_no, row in rows:
        s = (row.get("start_classmark") or "").strip().upper()
        e = (row.get("end_classmark") or "").strip().upper()
        loc = (row.get("location") or "").strip()
        if loc not in ALLOWED_LOCATIONS:
            raise DataValidationError(
                f"{path}:{line_no}: invalid location {loc!r} "
                f"(must be one of {ALLOWED_LOCATIONS})"
            )
        try:
            expanded = expand_range(s, e)
        except Exception as ex:
            raise DataValidationError(f"{path}:{line_no}: invalid range {s!r}..{e!r}: {ex}") from ex
        for mark in expanded:
            if mark in mapping and mapping[mark] != loc:
                raise DataValidationError(
                    f"{path}:{line_no}: conflicting location for {mark!r}: "
                    f"{mapping[mark]!r} vs {loc!r}"
                )
            mapping[mark] = loc
    return mapping
