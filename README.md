# research-os

> Public Physical AI research portfolio — Paper 001 recoverability @ S (Tier C) · Paper 002 WM adequacy (EXP-SURG-003) · **Mismatch Lab** (public product spec)

**Public research portfolio** for a focused question in Physical AI: how embodied systems should respond when reality no longer matches their expectations.

This repository contains **promoted research evidence only**—research questions, reproducible experiments, protocols, figures, and clearly tiered claims. It is not a career diary, lab notebook, or private strategy workspace.

| | |
| --- | --- |
| **Paper 001 (EXP-SURG-001)** | After mismatch @ **S**, how do **intervention choice** and **timing** determine **successful resolution**? |
| **Paper 002 (EXP-SURG-003)** | After K failed L1 repairs, does **L3 structural expansion** beat parameter repair on novel drift — with **adequacy gate** validity (H4)? |
| **Mismatch Lab** | Public lab spec — **Robot Diff** · model adequacy layer · [hub](docs/mismatch_lab/README.md) |
| **Study 002 (EXP-SURG-002)** | Pilot: dream curriculum (Tier B · archived) |

**Latest (2026-07-30):** **Paper 001** complete. **Paper 002 model-order confirmatory passed**: 400/400 valid cells, C-B H=10 prediction error -10.806 mm, and C-B fixed-horizon final distance -13.304 mm. A venue-neutral manuscript and supplement v1.1, LaTeX sources, review PDFs, and reproducible figures are published. **Mismatch Lab** v0.1 spec published.

---

## Two public surfaces

```text
Research OS (this repo)     Evidence · protocols · Paper 001/002 · promoted results
Mismatch Lab (public spec)  Robot Diff · benchmark · SDK design · pilot invitation
```

Long-term vision (research program only): [docs/mismatch_lab/vision_narrative_v0.2.md](docs/mismatch_lab/vision_narrative_v0.2.md) — not a company or product roadmap in this repo.

---

## Research direction

**Long-term (L0):** When reality cannot be explained by the current **model class**, how should an embodied system revise the **architecture and composition** of its world-modeling system?

**Near-term program:** failure-driven representation reconstruction · **model adequacy decision** · latent as **observation** · recoverability as **measurement window** · Isaac/ORBIT embodied sim.

**Public product wedge (2026–28):** understand robot rollouts (**Diff · Replay · Explain**) → detect when differences imply **structural model inadequacy** — not auto-fix the robot on day one.

**Current scope:** controlled simulation studies. This repository does not claim clinical deployment, a complete theory of exception-aware intelligence, or a general recoverability estimator.

---

## Claim tier (honest)

| Tier | Label | Status |
| --- | --- | --- |
| A | Scaffold / protocol | Same-state CF pipeline · replay OK |
| B | Smoke / direction | 001A–D smoke atlas · Study2 desk mock |
| C | Confirmatory | **Paper 001 D0–D3 executed** (n=20) · **Paper 002 model-order confirmatory passed** (400 cells) |
| B+ | Pilot mechanism | **Paper 002 mock pilot v0.4** · G1 + H4 · not generalization |

We have **not** shown general world-model expansion, hardware transfer, a new recoverability **estimator**, or clinical deployment.

---

## Confirmatory highlights (Tier C)

| Track | Result | Summary |
| --- | --- | --- |
| **Paper 001 D0** | REPLAN **19/20** vs CONTINUE **0/20** @ 6 cm + occlusion | [`study1_proper/summary.json`](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper/summary.json) |
| **Paper 001 D1–D3** | B2 **0%** · B3 **85%** · D1 control descriptive | [`study1_proper_v2/summary.json`](experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper_v2/summary.json) |
| **Paper 001 figures** | Profile · baseline overlay · Isaac EE traces | [`docs/paper1/figures/`](docs/paper1/figures/) |
| **Study 002** | Pilot · mock–Isaac alignment (Tier B) | [`h3_mock_isaac_v0.4`](experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/h3_mock_isaac_v0.4/summary.json) |
| **Paper 002 pilot v0.4** | C vs B ΔPE · gate · H4 (preliminary) | [`pilot_v0.1/summary.json`](experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/pilot_v0.1/summary.json) |
| **Paper 002 Isaac drift anchor** | Moving target **10/10** vs frozen target **0/10** · 20.250 mm paired improvement | [`RESULTS.md`](experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_static_first_confirmatory_v0.2/RESULTS.md) |
| **Paper 002 model-order confirmatory** | C-B prediction **-10.806 mm** · final distance **-13.304 mm** · all gates pass | [`RESULTS.md`](experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_model_order_confirmatory_v1.0/RESULTS.md) |
| **Paper 002 submission package** | Manuscript + supplement v1.1 · LaTeX · Overleaf ZIP · review PDFs · five generated panels · CSV tables | [`manuscript`](docs/paper002/paper002_manuscript_model_order_v1.1.md) · [`LaTeX`](docs/paper002/paper002_manuscript_model_order_v1.1.tex) · [`Overleaf`](docs/paper002/paper002_overleaf_main_v1.1.zip) · [`PDF`](docs/paper002/paper002_manuscript_model_order_v1.1.pdf) · [`supplement`](docs/paper002/paper002_supplement_model_order_v1.1.tex) |

Full status: Paper 001 [`docs/paper1/status.md`](docs/paper1/status.md) · Paper 002 [`docs/paper002/status.md`](docs/paper002/status.md)

---

## Start here

| | Link |
| --- | --- |
| Portfolio landing | **[higuseonhye.github.io/research-os](https://higuseonhye.github.io/research-os/)** · [`docs/index.md`](docs/index.md) |
| **Mismatch Lab** | [`docs/mismatch_lab/README.md`](docs/mismatch_lab/README.md) · [Diff demo](docs/mismatch_lab/diff_explorer_v0.1.html) · [public scope](docs/mismatch_lab/PUBLIC_SCOPE.md) |
| Paper 001 hub | [`docs/paper1/README.md`](docs/paper1/README.md) |
| Paper 002 hub | [`docs/paper002/README.md`](docs/paper002/README.md) |
| EXP-SURG-003 | [`experiments/.../exp_surg_003_wm_expansion/README.md`](experiments/surgical_intelligence/exp_surg_003_wm_expansion/README.md) |
| Study 002 hub | [`docs/stage2/README.md`](docs/stage2/README.md) |
| Research question v1.0 | [`docs/paper1/research_question.md`](docs/paper1/research_question.md) |
| Experiment loop | [`docs/EXPERIMENT_LOOP.md`](docs/EXPERIMENT_LOOP.md) |
| Repro scripts | [`scripts/README.md`](scripts/README.md) |
| Public boundary | [`docs/PUBLIC_BOUNDARY.md`](docs/PUBLIC_BOUNDARY.md) · [`docs/mismatch_lab/PUBLIC_SCOPE.md`](docs/mismatch_lab/PUBLIC_SCOPE.md) |

---

## Quick repro

```bash
# Paper 002 confirmatory figures and tables (CPU only)
python scripts/plot_paper002_model_order.py
python scripts/build_paper002_submission_tex.py
python scripts/build_paper002_overleaf_zip.py

# Historical Paper 002 mock smoke (CPU)
python scripts/run_exp_surg_003_pilot.py --smoke

# Paper 001
python scripts/run_study1a.py --mock
export STUDY1D_FULL=1
export STUDY1D_SEEDS=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19
bash scripts/run_study1d_runpod.sh
```

VESSL: [`docs/paper002/vessl_runbook_v0.1.md`](docs/paper002/vessl_runbook_v0.1.md)

---

## Repository layout

| Path | Contents |
| --- | --- |
| `docs/mismatch_lab/` | Public lab spec · API schema · benchmark · homepage copy |
| `docs/paper1/` | Paper 001 RQ · status · working paper |
| `docs/paper002/` | Paper 002 manuscript · figures · frozen preregistration |
| `experiments/surgical_intelligence/exp_surg_003_*` | Paper 002 pilot, confirmatory records, and Isaac trajectories |
| `experiments/surgical_intelligence/exp_surg_001_*` | Paper 1 configs · Tier B/C results |
| `scripts/wm_expansion/` | Mock env · WM · gate · protocol |
| `scripts/` | Mock + RunPod + VESSL entry points |

---

## Security

Do **not** commit API keys, credentials, PHI, or collaborator-embargoed material without consent. See [`.gitignore`](.gitignore) and [`docs/PUBLIC_BOUNDARY.md`](docs/PUBLIC_BOUNDARY.md).

**Private by design:** internal reading queues, career and relocation planning, people notes, internal meeting notes, and unpublished strategy are excluded from this repository.
