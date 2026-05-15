"""Segment-by-segment, field-by-field HL7 v2 diff."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, List, Optional

from hl7_message_diff.parser import parse_message, Segment
from hl7_message_diff.labels import label_for


@dataclass(frozen=True)
class Difference:
    """One field-level difference between two messages."""

    segment: str
    segment_index: int
    field: int
    field_name: str
    before: Optional[str]
    after: Optional[str]
    kind: str  # "changed" | "added" | "removed" | "segment-mismatch" | "segment-only-in-a" | "segment-only-in-b"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _diff_segment_pair(a: Segment, b: Segment) -> List[Difference]:
    """Diff two segments of the same type at the same index."""
    diffs: List[Difference] = []
    max_len = max(len(a.fields), len(b.fields))
    for i in range(max_len):
        a_val = a.fields[i] if i < len(a.fields) else None
        b_val = b.fields[i] if i < len(b.fields) else None
        if a_val == b_val:
            continue
        position = i + 1  # 1-based HL7 field number
        label = label_for(a.name, position)
        if a_val is None:
            kind = "added"
        elif b_val is None:
            kind = "removed"
        else:
            kind = "changed"
        diffs.append(
            Difference(
                segment=a.name,
                segment_index=a.index,
                field=position,
                field_name=label,
                before=a_val,
                after=b_val,
                kind=kind,
            )
        )
    return diffs


def diff_messages(raw_a: str, raw_b: str) -> List[Difference]:
    """Return ordered list of field-level differences between two HL7 messages.

    An empty list means the messages are semantically identical (same segments,
    same field values in the same positions).
    """
    a_segs = parse_message(raw_a)
    b_segs = parse_message(raw_b)
    diffs: List[Difference] = []

    max_segs = max(len(a_segs), len(b_segs))
    for i in range(max_segs):
        a = a_segs[i] if i < len(a_segs) else None
        b = b_segs[i] if i < len(b_segs) else None

        if a is None and b is not None:
            diffs.append(
                Difference(
                    segment=b.name,
                    segment_index=i,
                    field=0,
                    field_name=f"{b.name} (segment present only in second message)",
                    before=None,
                    after=b.name,
                    kind="segment-only-in-b",
                )
            )
            continue
        if b is None and a is not None:
            diffs.append(
                Difference(
                    segment=a.name,
                    segment_index=i,
                    field=0,
                    field_name=f"{a.name} (segment present only in first message)",
                    before=a.name,
                    after=None,
                    kind="segment-only-in-a",
                )
            )
            continue

        assert a is not None and b is not None  # for type checkers
        if a.name != b.name:
            diffs.append(
                Difference(
                    segment=f"{a.name}/{b.name}",
                    segment_index=i,
                    field=0,
                    field_name=f"Segment type mismatch at index {i}: {a.name} vs {b.name}",
                    before=a.name,
                    after=b.name,
                    kind="segment-mismatch",
                )
            )
            continue

        diffs.extend(_diff_segment_pair(a, b))

    return diffs
