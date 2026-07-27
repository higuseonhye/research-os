# Public boundary — research-os

> **Audience:** anyone on the internet · employers · collaborators · reviewers  
> **Rule:** this repo is **self-contained**. No links to private GitHub repos.  
> **Governance (2026-07-28):** Independent personal research — public promotion = self sign-off after tier labeling and this checklist (no external PI gate).

---

## What belongs here (public)

| Category | Examples |
| --- | --- |
| **Locked research questions** | Paper 1 RQ v1.0 · public framing |
| **Reproducible code** | `scripts/` · `exp_surg_001` · `exp_surg_002` |
| **Tier B/C evidence** | Isaac aggregates · figures · `summary.json` with tier labels |
| **Methods / protocol** | Same-state CF · perturbation configs · benchmark schema |
| **Pre-reg / frozen design** | Phase C pre-reg · Study 2 Phase 1 design v0.1 |
| **Positioning (desk synthesis)** | Eval landscape v0.2 · lit positioning v1 |
| **Working paper PDF** | Labeled *not peer-reviewed* · tier-aligned narrative (e.g. `docs/paper1/paper001_recoverability_en.pdf`) |

---

## What does **not** belong here

| Category | Keep off public repo |
| --- | --- |
| API keys · tokens · `.env` | Never commit |
| PHI · patient data · clinical identifiers | Forbidden |
| L1 program narrative · Study 2 paper outline · internal exec logs | Working notes (local / private storage) |
| Internal PDF reading queues · kill matrix drafts | Working notes |
| Career · immigration · target lists | Working notes |
| Unreviewed manuscript drafts · internal meeting notes · collaborator-embargoed material | Working notes (private / vault) |
| **URLs to private repos** | Do not link from this repo |

---

## Claim tiers (required labeling)

| Tier | May say publicly |
| --- | --- |
| **A** | Protocol exists · pipeline runs · replay OK |
| **B** | Directional smoke · desk pilot · labeled “smoke” |
| **C** | Confirmatory · only after registered GPU run completes |

Never present Tier B as Tier C.

---

## Promotion flow

```text
working notes (private / vault) → self review (tier + claim boundary) → promote slice to research-os → tag tier · update status.md
```

Promote **design + results + repro** only. Do not copy internal logs or private URLs.
