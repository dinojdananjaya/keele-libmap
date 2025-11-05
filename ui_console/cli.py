from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--subjects",
        required=True,
        help="Path to subjects↔classmarks CSV",
    )
    parser.add_argument(
        "--locations",
        required=True,
        help="Path to classmarks↔locations CSV",
    )
    parser.parse_args()
    # TODO: load data via app_core.loader
    # TODO: interactive loop


if __name__ == "__main__":
    main()
