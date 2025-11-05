from __future__ import annotations

import argparse
import tkinter as tk


def run_gui(subjects_path: str, locations_path: str) -> None:
    root = tk.Tk()
    root.title("Library Map")
    # TODO: build UI and connect to app_core
    root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subjects", required=True)
    parser.add_argument("--locations", required=True)
    args = parser.parse_args()
    run_gui(args.subjects, args.locations)


if __name__ == "__main__":
    main()
