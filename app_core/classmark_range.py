# I acknowledge using ChatGPT (GPT-5 Thinking) as a reviewer for structure/QA.
# Code is my own; no generated content is used in this file.

"""
Classmark range utilities.

Rules:
- Classmarks are 1–2 uppercase letters A–Z only.
- Example range "G" to "GF" expands to: G, GA, GB, GC, GD, GE, GF.
"""

from __future__ import annotations

import re
from typing import List

_VALID_RE = re.compile(r"^[A-Z]{1,2}$")


def is_valid_classmark(mark: str) -> bool:
    """Return True iff mark is 1–2 uppercase letters A–Z."""
    if mark is None:
        return False
    return _VALID_RE.fullmatch(mark) is not None


def classmark_to_int(mark: str) -> int:
    """Map A→0 … Z→25, AA→26 … AZ→51 … ZZ→(26*26+25). Assumes valid mark."""
    if not is_valid_classmark(mark):
        raise ValueError(f"Invalid classmark: {mark!r}")
    if len(mark) == 1:
        return ord(mark[0]) - ord("A")
    # len == 2
    base = 26
    first = ord(mark[0]) - ord("A")
    second = ord(mark[1]) - ord("A")
    return base + 26 * first + second


def int_to_classmark(n: int) -> str:
    """Inverse of classmark_to_int for 0..(26*26+25)."""
    if n < 0 or n > (26 * 26 + 25):
        raise ValueError(f"Out of bounds integer for classmark: {n}")
    if n <= 25:
        return chr(n + ord("A"))
    n -= 26
    first = n // 26
    second = n % 26
    return chr(first + ord("A")) + chr(second + ord("A"))


def expand_range(start: str, end: str) -> List[str]:
    """Inclusive expansion from start to end, after validation & normalization."""
    s = start.strip().upper()
    e = end.strip().upper()
    if not is_valid_classmark(s) or not is_valid_classmark(e):
        raise ValueError(f"Invalid range endpoints: {start!r}..{end!r}")
    si = classmark_to_int(s)
    ei = classmark_to_int(e)
    if si > ei:
        raise ValueError(f"Range start exceeds end: {start!r}>{end!r}")
    return [int_to_classmark(i) for i in range(si, ei + 1)]
