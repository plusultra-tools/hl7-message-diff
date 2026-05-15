"""Minimal HL7 v2 parser.

Assumes well-formed messages. Splits by segment terminator (\\r, \\n, or \\r\\n)
and by the field separator declared in MSH-1 (default '|').
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Segment:
    """A single HL7 v2 segment."""

    name: str
    fields: List[str]
    index: int  # position in the message (0-based)


def _split_segments(raw: str) -> List[str]:
    """Normalise line endings and split on segment terminator.

    HL7 v2 uses \\r officially; in the wild we see \\n and \\r\\n too.
    Empty lines are dropped.
    """
    normalised = raw.replace("\r\n", "\r").replace("\n", "\r")
    return [s for s in normalised.split("\r") if s.strip()]


def parse_message(raw: str) -> List[Segment]:
    """Parse a raw HL7 v2 message string into a list of Segment objects.

    The field separator is read from MSH-1 (4th character of the MSH segment)
    when present; otherwise '|' is assumed.

    Args:
        raw: The full HL7 message text.

    Returns:
        Ordered list of Segment objects.
    """
    raw_segments = _split_segments(raw)
    if not raw_segments:
        return []

    field_sep = "|"
    first = raw_segments[0]
    if first.startswith("MSH") and len(first) >= 4:
        field_sep = first[3]

    segments: List[Segment] = []
    for idx, raw_seg in enumerate(raw_segments):
        parts = raw_seg.split(field_sep)
        name = parts[0]
        # For MSH the field separator itself is "MSH-1" by convention;
        # the rest of the fields start from MSH-2.
        if name == "MSH":
            fields = [field_sep] + parts[1:]
        else:
            fields = parts[1:]
        segments.append(Segment(name=name, fields=fields, index=idx))
    return segments
