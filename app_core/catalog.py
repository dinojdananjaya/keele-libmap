# GenAI reviewer used for structure/QA; code authored by me.
# No generated code is used in this file.

"""Shared search API for console and GUI."""

from __future__ import annotations

from typing import Dict, List, Set

from .constants import ALLOWED_LOCATIONS


class Catalog:
    def __init__(self, subjects_map: Dict[str, Set[str]], locations_map: Dict[str, str]) -> None:
        # Build by_classmark
        self._by_classmark: Dict[str, tuple[str, Set[str]]] = {}
        for cm, loc in locations_map.items():
            self._by_classmark[cm] = (loc, set())
        # Attach subjects (classmark may exist only in subjects_map too)
        for cm, subs in subjects_map.items():
            if cm in self._by_classmark:
                self._by_classmark[cm] = (self._by_classmark[cm][0], set(subs))
            else:
                # Classmark with subjects but no location → still track with empty location?
                # Better: omit from results unless a location is later provided.
                self._by_classmark[cm] = ("", set(subs))

        # Subject index
        self._by_subject_lower: Dict[str, Set[str]] = {}
        for cm, (_, subs) in self._by_classmark.items():
            for s in subs:
                self._by_subject_lower.setdefault(s.lower(), set()).add(cm)

        # Location index
        self._by_location: Dict[str, Set[str]] = {}
        for cm, (loc, _) in self._by_classmark.items():
            if loc:
                self._by_location.setdefault(loc, set()).add(cm)

    def _row(self, classmark: str) -> dict:
        loc, subjects = self._by_classmark[classmark]
        return {
            "classmark": classmark,
            "location": loc,
            "subjects": sorted(subjects),
        }

    def search_by_subject(self, q: str) -> List[dict]:
        term = (q or "").strip().lower()
        if not term:
            return []
        # gather subjects that contain the term
        cmatches: Set[str] = set()
        for subj_lower, cms in self._by_subject_lower.items():
            if term in subj_lower:
                cmatches.update(cms)
        rows = [self._row(cm) for cm in cmatches if self._by_classmark[cm][0]]
        return sorted(rows, key=lambda r: r["classmark"])

    def search_by_classmark(self, mark: str) -> List[dict]:
        cm = (mark or "").strip().upper()
        if not cm:
            return []
        if cm not in self._by_classmark or not self._by_classmark[cm][0]:
            return []
        return [self._row(cm)]

    def search_by_location(self, loc: str) -> List[dict]:
        loc_norm = (loc or "").strip()
        if loc_norm not in ALLOWED_LOCATIONS:
            return []
        cms = self._by_location.get(loc_norm, set())
        rows = [self._row(cm) for cm in cms]
        return sorted(rows, key=lambda r: r["classmark"])
