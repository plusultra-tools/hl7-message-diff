# Kill gate — hl7-message-diff

**Decision date:** 2026-06-13 (d+30 from launch, target launch 2026-05-14).

## Survive criteria (any one suffices)

- **≥ 100 GitHub stars** on the public repo, OR
- **≥ 30 `pip install` per `last_week`** (pypistats.org/packages/hl7-message-diff) at the decision date, OR
- **≥ 3 issues / PRs from contributors with verifiable healthcare affiliations** (hospital, EHR vendor, integration consultancy — check GitHub bios / employer emails), OR
- **≥ 1 Stripe-paying customer** on the future Pro tier (batch + CI mode).

## Kill criteria (auto-kill if true)

- All four metrics below thresholds AND no organic inbound signal (zero unsolicited mentions, no Reddit / Hacker News thread, no third-party blog post).
- 30-day install trend flat or declining at d+30.
- No reply from any of the 5 cold outreach attempts to integration engineers (LinkedIn / r/healthIT moderators).

## Distribution checkpoints (pre-decision)

By d+14:
- Published on PyPI under name `hl7-message-diff`.
- README answers at least 2 Stack Overflow questions on HL7 diffing (linked back to the repo).
- Posted on r/healthIT, r/healthinformatics, r/python, dev.to.
- Static web page live on GitHub Pages or Vercel with custom domain.

By d+21:
- ProductHunt submission scheduled.
- Reached out to 10 integration engineers on LinkedIn (after principal calibration on voice/tone — see CLAUDE.md §3).

## Post-mortem path (if killed)

Move repository to public-archive state (do not delete — SEO value persists). Move workspace to `archive/hl7-message-diff/` with `post-mortem.md` capturing:
- Final star/install/issue counts.
- Hypothesis on why it failed (no audience, wrong distribution channel, feature insufficient, etc.).
- Salvageable assets (the v2.6 label map alone is reusable for the next HL7-related venture).
