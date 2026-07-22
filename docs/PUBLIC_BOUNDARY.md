# Public boundary — research-os

> **Audience:** anyone on the internet · employers · collaborators · reviewers  
> **Master asset rule:** update evidence here first · derive resume / deck / emails elsewhere

---

## What belongs in this repo (public)

| Category | Examples |
| --- | --- |
| **Locked research questions** | Paper 1 RQ v1.0 · public framing |
| **Reproducible code** | `scripts/` · `exp_surg_001` · `exp_surg_002` |
| **Tier B smoke evidence** | Isaac aggregates · figures · `summary.json` with tier labels |
| **Methods / protocol** | Same-state CF · perturbation configs · benchmark schema |
| **Pre-reg summaries** | Phase C **frozen design** (confirmatory not run) |
| **Positioning (desk synthesis)** | Eval landscape v0.2 · lit positioning v1 |

---

## What does **not** belong here

| Category | Where |
| --- | --- |
| API keys · tokens · `.env` | Never commit · see `.gitignore` |
| PHI · patient data · clinical identifiers | Forbidden |
| Stage 2 L1 RQ · Study2 paper outline · full Study2 pre-reg narrative | **builder-os-private** · stub in `docs/stage2/` |
| Internal PDF reading queues · day plans | **builder-os-private** / Obsidian vault |
| Career · immigration · target lists · 9-week program | **builder-os-private/working/career/** |
| Lab meeting feedback · PI drafts · kill matrix edits | **builder-os-private** |
| Embargoed co-author material | Private until release |

---

## Claim tiers (required labeling)

| Tier | May say publicly |
| --- | --- |
| **A** | Protocol exists · pipeline runs · replay OK |
| **B** | Directional smoke · n=5 or desk pilot · labeled “smoke” |
| **C** | Confirmatory · only after registered GPU run completes |

Never present Tier B as Tier C.

---

## Links to private repos

Some paths reference `builder-os-private` on GitHub. Those URLs require repo access. Public readers should use this repo + [`docs/stage2/README.md`](stage2/README.md) stubs only.

---

## Promotion flow

```text
working (private) → review → promote slice to research-os → tag tier · update status.md
```

Do not copy wholesale from private to public.
