# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-05-14

### Added
- Minimal HL7 v2 parser (`parser.py`) — splits by segment terminator and field
  separator declared in MSH-1. Handles `\r`, `\n`, and `\r\n` line endings.
- HL7 v2.6 field labels (`labels.py`) for MSH, EVN, PID, PV1, OBR, OBX, NK1,
  AL1, DG1, IN1.
- Segment-by-segment, field-by-field diff (`differ.py`) with semantic labels.
- CLI `hl7diff` with `--format {text,json}` and `--color`/`--no-color` toggles.
- Static browser tool (`web/`) — vanilla JS port of the differ. No third-party
  deps. Runs entirely client-side; no data leaves the browser.
- 9 unit tests covering parser, labels, differ, and CLI.
- GitHub Actions test matrix (Python 3.8–3.12 × Ubuntu / macOS / Windows).
- MIT licence.
