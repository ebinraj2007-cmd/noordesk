"""Command-line interface: python -m noordesk.cli run"""
from __future__ import annotations

import argparse
import json
import os

from . import SUPPORTED_LANGUAGES, profile as profiles
from .ingest import load_from_folder
from .pipeline import process_inbox
from .escalation import DEFAULT_THRESHOLD

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE = os.path.join(HERE, "sample_data", "inbox")


def run(args) -> None:
    folder = args.inbox or SAMPLE
    messages = load_from_folder(folder)
    records = process_inbox(messages, profile=profiles.load(),
                            threshold=args.threshold, use_llm=not args.no_llm)
    records.sort(key=lambda r: (r["needs_review"], r["priority"]), reverse=True)

    print(f"\nNoorDesk — processed {len(records)} messages from {folder}\n")
    print(f"{'PRI':<4}{'LANG':<6}{'INTENT':<14}{'REVIEW':<8}SENDER")
    print("-" * 70)
    for r in records:
        flag = "REVIEW" if r["needs_review"] else ""
        lang = SUPPORTED_LANGUAGES.get(r["detected_language"], r["detected_language"])
        print(f"{r['priority']:<4}{lang:<6}{r['intent']:<14}{flag:<8}{r['sender']}")
        print(f"     translation: {r['translation']}")
        if r["suggested_reply"]:
            print(f"     reply ({lang}): {r['suggested_reply'][:80]}...")
        print()


def main() -> None:
    p = argparse.ArgumentParser(prog="noordesk", description="NoorDesk CLI")
    sub = p.add_subparsers(dest="command", required=True)
    r = sub.add_parser("run", help="process an inbox folder")
    r.add_argument("--inbox", help="folder of message .json files")
    r.add_argument("--no-llm", action="store_true", help="force the rule engine")
    r.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                   help="escalation confidence threshold (0..1)")
    r.set_defaults(func=run)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
