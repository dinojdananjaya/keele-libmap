# GenAI reviewer used for structure/QA; code authored by me.
# No generated code is used in this file.


from __future__ import annotations

import argparse
from typing import Iterable

from app_core.catalog import Catalog
from app_core.constants import ALLOWED_LOCATIONS
from app_core.errors import DataValidationError
from app_core.loader import load_locations, load_subjects


def print_rows(rows: Iterable[dict]) -> None:
    """Pretty-print: Classmark | Location | Subjects (comma-separated)."""
    rows = list(rows)
    if not rows:
        print("No matches found.\n")
        return
    w1 = max(9, max(len(r["classmark"]) for r in rows))
    w2 = max(8, max(len(r["location"]) for r in rows))
    print(f"{'Classmark':<{w1}} | {'Location':<{w2}} | Subjects")
    print(f"{'-'*w1}-+-{'-'*w2}-+-{'-'*40}")
    for r in rows:
        print(f"{r['classmark']:<{w1}} | {r['location']:<{w2}} | {', '.join(r['subjects'])}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Keele Library Map - console search")
    parser.add_argument("--subjects", required=True, help="Path to subjects↔classmarks CSV")
    parser.add_argument("--locations", required=True, help="Path to classmarks↔locations CSV")
    args = parser.parse_args()

    try:
        subj = load_subjects(args.subjects)
        locs = load_locations(args.locations)
    except DataValidationError as e:
        print(f"Data error: {e}")
        return

    catalog = Catalog(subj, locs)

    MENU = """
Search mode:
  [1] Subject / part-name  (e.g., "english" or "enviro")
  [2] Classmark            (e.g., PR)
  [3] Location             (one of the six)
  [Q] Quit
Choice: """
    while True:
        choice = input(MENU).strip().lower()
        if choice == "q":
            print("Goodbye.")
            break
        elif choice == "1":
            q = input("Enter subject (full or partial): ").strip()
            print_rows(catalog.search_by_subject(q))
        elif choice == "2":
            q = input("Enter classmark (1–2 letters, e.g., PR): ").strip()
            print_rows(catalog.search_by_classmark(q))
        elif choice == "3":
            print("Locations:")
            for loc in ALLOWED_LOCATIONS:
                print(f" - {loc}")
            q = input("Enter location exactly as shown: ").strip()
            print_rows(catalog.search_by_location(q))
        else:
            print("Please choose 1, 2, 3 or Q.\n")


if __name__ == "__main__":
    main()
