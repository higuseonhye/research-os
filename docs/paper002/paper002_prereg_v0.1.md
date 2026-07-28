# Paper 002 — Pre-registration v0.1 (superseded)

> **Superseded by [paper002_prereg_v0.2.md](paper002_prereg_v0.2.md)** · not executed  
> **Experiment:** EXP-SURG-003 · confirmatory generative curriculum  
> **Config:** [`sandbox_v0.3.yaml`](../../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/config/sandbox_v0.3.yaml)  
> **Pilot (not confirmatory):** Study 002 Phase 1–2 · [`../stage2/`](../stage2/)  
> **Date frozen:** 2026-07-28

---

## Design summary

| Parameter | Study 002 Phase 2 (pilot) | **Paper 002 confirmatory** |
| --- | --- | --- |
| Mock episodes / dreamer | 48 | **128** |
| Mock seeds | 3 (42–44) | **5 (42–46)** |
| Export strategy | top-5 + bottom-5 | **top-10 + bottom-10** |
| Specs / dreamer | 10 | **20** |
| **Total Isaac specs** | 20 | **40** |
| Isaac seeds / spec | 5 (0–4) | **8 (0–7)** |
| Agents @ mock | rule only | **rule + llm-json** |
| Isaac runner | study1d | **study1d** (unchanged) |
| Occlusion map | gain_scale_flag v0.1 | **unchanged** |

**Primary export seed:** 43 (Study 002 convention). Seeds 42, 44 = sensitivity only (Tier B).

---

## Primary hypotheses (confirmatory)

### H1 — Mock–Isaac rank correlation (rule agent)

> On the **40-spec top+bottom pack** exported from `mock_confirmatory_v0.1/records_seed43.json` (rule agent), **Spearman ρ** between mock per-spec informative (0/1) and Isaac informative ≥ **0.5** (pooled across dreamers).

**Pass:** ρ ≥ 0.5 · `reason: ok` · n ≥ 40  
**Pilot anchor:** Study 002 H3′ ρ=0.899 @ n=20

### H2 — Tier separation (rule agent)

> On Isaac @ rule agent: `bottom.informative_rate` ≤ **0.5** AND `top.informative_rate − bottom.informative_rate` ≥ **0.4**.

**Pass:** both conditions on pooled tiers across dreamers  
**Pilot anchor:** H4′ top 1.0 · bottom 0.3 @ n=20

### H3 — LLM agent Isaac validation

> LLM JSON curriculum (frozen prompt v0.1 · [`llm_curriculum_protocol_v0.1.md`](llm_curriculum_protocol_v0.1.md)) yields mock→Isaac **Spearman ρ ≥ 0.5** on its 40-spec pack, **OR** LLM **tier gap** ≥ rule tier gap with bottom IR ≤ 0.5.

**Pass:** either criterion  
**Kill:** LLM ρ < 0.3 **and** tier gap < rule → **no LLM claim** in paper body

---

## Secondary / exploratory (Tier B · not registry failure)

| ID | Hypothesis |
| --- | --- |
| **H4** | Gaussian per-dreamer ρ ≥ diffusion per-dreamer ρ (coverage vs diversity) |
| **H5** | Export seed sensitivity: ρ(42), ρ(44) within **0.15** of ρ(43) |
| **H6** | Hybrid dreamer (50/50 gaussian+diffusion proposals) ↑ tier gap vs single dreamer |
| **H7** | LLM mock informative yield ≥ rule (mock-only · descriptive) |

---

## Agents (frozen)

| Agent | Mode | Source |
| --- | --- | --- |
| **Rule baseline** | `rule` | Taxonomy cycle · Study 002 default |
| **LLM curriculum** | `json-file` | One JSON per mock seed · prompt v0.1 · see LLM protocol |

**LLM model:** record exact model ID in run log at execution time (not changed mid-study).

---

## Metrics (unchanged from Study 002)

| Metric | Definition |
| --- | --- |
| **informative @ spec** | CONTINUE fail ∧ REPLAN ok @ **S** |
| **informative_rate** | #informative / #specs in tier or pool |
| **mock–isaac ρ** | Spearman on per-spec 0/1 flags |
| **param_diversity** | mean std(shift, onset, occlusion) across mock records |
| **tier gap** | top IR − bottom IR |

---

## Execution order (gates)

| Leg | Work | Gate |
| ---: | --- | --- |
| 0 | This file committed · config v0.3 committed | — |
| 1 | LLM curricula generated (5 seeds × prompt v0.1) | JSON validates schema |
| 2 | Mock rule · 5 seeds · `--compare` · promote `mock_confirmatory_v0.1` | CPU · records committed |
| 3 | Mock llm-json · 5 seeds · promote `mock_confirmatory_llm_v0.1` | CPU |
| 4 | Export specs (seed 43 primary) → `artifacts/isaac_specs_v0.3.json` | 40 specs |
| 5 | Isaac rule ablation · study1d · 40 specs × 8 seeds | GPU · zero_agent smoke |
| 6 | Isaac llm ablation · same specs structure from llm mock | GPU |
| 7 | H1–H3 compute · promote `selection_ablation_v0.3/` · `h3_mock_isaac_v0.3/` | CPU |

**Do not run Leg 5–6 before Leg 0–4 complete.**

---

## Pass / fail / stop

| Outcome | Action |
| --- | --- |
| H1 + H2 PASS · H3 PASS | Tier A draft · full story |
| H1 + H2 PASS · H3 FAIL | Tier B · CF curriculum · no LLM claim |
| H1 PASS · H2 FAIL | Stop · publish mock-rank limitation · no Isaac retry on same cell |
| H1 FAIL | Stop GPU for llm leg · negative result doc |

**One Isaac ablation per frozen design.** No third ablation on same cell without new pre-reg.

---

## Version

| Version | Date | Note |
| --- | --- | --- |
| v0.1 | 2026-07-28 | Initial freeze · Study 002 → Paper 002 elevation |
