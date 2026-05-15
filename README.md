# hl7-message-diff

A semantic diff tool for HL7 v2 pipe-delimited messages — see exactly which field changed, by name, not by position.

## Why this exists

HL7 v2 messages are pipe-delimited, positional, and field-order matters. When `PID|1|||12345^^^MR||DOE^JOHN||19800101|M|||123 MAIN ST^^BOSTON^MA^02101` becomes
`PID|1|||12345^^^MR||DOE^JOHN||19800102|M|||123 MAIN ST^^BOSTON^MA^02101`,
spotting that **PID-7 (Date of Birth)** flipped from `19800101` to `19800102` is a chore. Multiply by 20 segments, hundreds of fields, and a stack of integration test failures — and you have a real problem.

Every hospital integration engineer who has touched Mirth, Iguana, Rhapsody, Cloverleaf, Corepoint, or a custom-rolled HL7 listener has hit this. Stack Overflow has dozens of "how do I diff HL7 messages" threads. The standard answer is `vimdiff` or `diff -u` — which tells you *that* bytes differ at column 47, not that the **patient's DOB** changed.

This tool fixes that. Field-by-field, with semantic labels from the HL7 v2.6 standard.

## What it does

**1. CLI:**
```bash
hl7diff message_a.hl7 message_b.hl7
```
→ colored output. Shows segment, field number, field name (e.g. `PID-7 Date/Time of Birth`), before-value, after-value.

**2. Static web (browser-only, no PHI leaves the browser):**
Open `web/index.html`. Paste two messages, get colored diff. No server, no upload, no tracking. Safe for production HL7 traffic.

**3. JSON output for CI:**
```bash
hl7diff a.hl7 b.hl7 --format json
```
→ structured diff. Drop it into pytest, Jest, or any test harness to assert "this integration mapping preserves PID-3 (patient ID) and PID-5 (name)."

## What it does NOT do

- **Not a HL7 v2 parser/validator.** Assumes messages are well-formed. If your `MSH` segment is malformed, fix that first with `hl7apy` or `python-hl7`.
- **No FHIR / HL7 v3 / CDA support.** Those are JSON/XML and have proper diff tools already (`json-diff`, `xmldiff`).
- **No transformation suggestions.** Pure diff, not a mapping engine.
- **No segment reordering tolerance.** Segments are matched by index; if your `PID` is at position 1 in one message and position 2 in another, that's reported as a structural diff.

## Semantic-label coverage

Embedded HL7 v2.6 field definitions for the segments that cover ~95% of real-world ADT and ORU traffic:

| Segment | Coverage | Notes |
|---------|----------|-------|
| MSH | 1-21 | Message Header |
| PID | 1-30 | Patient Identification |
| PV1 | 1-52 | Patient Visit |
| OBR | 1-49 | Observation Request |
| OBX | 1-18 | Observation/Result |
| EVN | 1-7 | Event Type |
| NK1 | 1-39 | Next of Kin |
| AL1 | 1-6 | Patient Allergy Information |
| DG1 | 1-22 | Diagnosis |
| IN1 | 1-53 | Insurance |

Unknown segments fall back to positional labels (`XYZ-3` instead of `XYZ-3 SomeName`).

## Install

```bash
pip install hl7-message-diff
```

Or from source:
```bash
git clone https://github.com/<user>/hl7-message-diff
cd hl7-message-diff
pip install -e .
```

Stdlib only. No dependencies.

## Examples

**Identical messages → empty diff, exit 0:**
```bash
$ hl7diff sample.hl7 sample.hl7
No differences.
$ echo $?
0
```

**1-field change:**
```bash
$ hl7diff before.hl7 after.hl7
PID-7 Date/Time of Birth
  - 19800101
  + 19800102
```

**JSON output:**
```bash
$ hl7diff before.hl7 after.hl7 --format json
{
  "differences": [
    {
      "segment": "PID",
      "segment_index": 0,
      "field": 7,
      "field_name": "Date/Time of Birth",
      "before": "19800101",
      "after": "19800102"
    }
  ]
}
```

## Pricing

- **OSS**: MIT-licensed. The CLI, the web page, the library — all free.
- **Future Pro tier (€5-9/mo)**: batch mode (diff a folder of 10,000 messages against a baseline in CI), GitHub Actions integration, summary reports per integration test run. Email `hl7diff@example.com` to be notified.

## Contributing

Issues with real-world HL7 messages (PHI redacted) are gold. Open one with:
- The two messages you're comparing.
- What you expected.
- What you got.

## License

MIT. See `LICENSE`.
