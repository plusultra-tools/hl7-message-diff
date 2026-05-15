"""Command-line interface for hl7-message-diff."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, TextIO

from hl7_message_diff.differ import diff_messages, Difference


# ANSI colour codes — kept inline to stay stdlib-only.
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _format_text(diffs: List[Difference], use_color: bool) -> str:
    if not diffs:
        return "No differences.\n"

    def c(code: str, text: str) -> str:
        return f"{code}{text}{RESET}" if use_color else text

    lines: List[str] = []
    for d in diffs:
        if d.kind == "segment-mismatch":
            lines.append(c(YELLOW + BOLD, d.field_name))
        elif d.kind == "segment-only-in-a":
            lines.append(c(RED + BOLD, d.field_name))
        elif d.kind == "segment-only-in-b":
            lines.append(c(GREEN + BOLD, d.field_name))
        else:
            lines.append(c(CYAN + BOLD, d.field_name))
            if d.before is not None:
                lines.append(c(RED, f"  - {d.before}"))
            if d.after is not None:
                lines.append(c(GREEN, f"  + {d.after}"))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _format_json(diffs: List[Difference]) -> str:
    payload = {"differences": [d.to_dict() for d in diffs]}
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def _read_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hl7diff",
        description=(
            "Semantic diff for HL7 v2 pipe-delimited messages. "
            "Shows which field changed with HL7 v2.6 field names."
        ),
    )
    parser.add_argument("file_a", help="Path to first HL7 message file.")
    parser.add_argument("file_b", help="Path to second HL7 message file.")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format. 'text' (default) is human-readable; 'json' is for CI.",
    )
    color_group = parser.add_mutually_exclusive_group()
    color_group.add_argument(
        "--color", action="store_true", help="Force ANSI colour output."
    )
    color_group.add_argument(
        "--no-color", action="store_true", help="Disable ANSI colour output."
    )
    return parser


def main(argv: List[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    out = stdout if stdout is not None else sys.stdout

    try:
        raw_a = _read_file(args.file_a)
        raw_b = _read_file(args.file_b)
    except OSError as exc:
        print(f"hl7diff: error reading input: {exc}", file=sys.stderr)
        return 2

    diffs = diff_messages(raw_a, raw_b)

    if args.format == "json":
        out.write(_format_json(diffs))
    else:
        if args.no_color:
            use_color = False
        elif args.color:
            use_color = True
        else:
            use_color = out.isatty() if hasattr(out, "isatty") else False
        out.write(_format_text(diffs, use_color))

    return 0 if not diffs else 1


if __name__ == "__main__":
    sys.exit(main())
