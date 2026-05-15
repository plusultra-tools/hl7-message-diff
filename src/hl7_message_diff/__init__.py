"""hl7-message-diff — semantic diff for HL7 v2 messages."""

from hl7_message_diff.differ import diff_messages, Difference
from hl7_message_diff.parser import parse_message, Segment

__version__ = "0.1.0"
__all__ = ["diff_messages", "Difference", "parse_message", "Segment"]
