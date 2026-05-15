# Landing copy — hl7-message-diff (Carrd / static)

## Hero

**Stop eye-balling pipe-delimited HL7 messages.**

Diff two HL7 v2 messages field-by-field, with semantic labels from the v2.6 standard. See exactly which field changed — not just which byte.

`pip install hl7-message-diff`  ·  [Try in browser →](./web/index.html)  ·  [GitHub →](https://github.com/example/hl7-message-diff)

---

## Three modes

**CLI** — `hl7diff before.hl7 after.hl7`
Coloured output. Field names. Before / after. Drop into your terminal.

**Browser** — open `index.html`
Paste two messages. Get a diff. **No upload. No server. No PHI ever leaves your browser.** Safe for production traffic.

**JSON for CI** — `hl7diff a.hl7 b.hl7 --format json`
Plug into pytest / Jest / Go test. Assert "this mapping preserves PID-3 and PID-5." Catch regressions in your integration mappings before they hit prod.

---

## Built for hospital integration engineers

You wrote a new Mirth channel. You map HL7 ADT^A04 to an internal API. You change one transformation rule. Two test messages diverge. `diff -u` tells you "bytes differ at column 47." Useless.

`hl7diff` tells you: **PID-7 Date/Time of Birth** changed from `19800101` to `19800102`. Now you know.

---

## Free. Open source. MIT.

The CLI, the library, the browser tool — all free, all MIT-licensed.

**Coming soon — Pro tier (€5-9/mo):**
- Batch mode: diff a folder of 10,000 messages against a baseline in CI.
- GitHub Actions integration.
- Per-test-run summary reports.

[Notify me when Pro launches →](mailto:hl7diff@example.com?subject=Notify%20me%20when%20Pro%20launches)

---

## FAQ

**Does it support HL7 FHIR?**
No — FHIR is JSON/XML and already has good diff tools (`json-diff`, `xmldiff`). This is strictly for HL7 v2 pipe-delimited.

**Does it parse / validate HL7?**
No — it assumes well-formed messages. For parsing/validation use `hl7apy` or `python-hl7` first.

**Is the browser version actually private?**
Yes. Open DevTools, watch the Network tab, paste a message, click Diff — zero outbound requests. The whole differ runs in JS in your browser tab.

**Which segments are labelled?**
MSH, EVN, PID, PV1, OBR, OBX, NK1, AL1, DG1, IN1. Unknown segments fall back to positional labels (`XYZ-3` instead of `XYZ-3 SomeName`). PRs welcome to extend coverage.

---

## Built by integration engineers, for integration engineers

Open an [issue](https://github.com/example/hl7-message-diff/issues) with a message you couldn't diff. PRs welcome.
