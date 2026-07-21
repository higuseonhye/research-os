# EXP-SURG-002 — Dream curriculum sandbox (Stage 2 probe)

> **Status:** v0.1 desk mock · not Paper 1 evidence  
> **Parent:** EXP-SURG-001 perturbation taxonomy + mock reach  
> **Goal:** Compare **Gaussian vs diffusion** failure-scenario dreaming + **agentic curriculum** planning

## Quick start (no GPU)

```bash
python scripts/run_study2_dream_curriculum_mock.py --dreamer diffusion --agent rule --episodes 32
python scripts/run_study2_dream_curriculum_mock.py --compare --episodes 48
```

## Phase 1 (RunPod · publication track)

Pre-reg: [`docs/stage2/study2_prereg_v0.1.md`](../../../docs/stage2/study2_prereg_v0.1.md)

```bash
bash scripts/run_study2_dream_curriculum_runpod.sh
```

Outputs: `results/study2_dream_curriculum/mock/<run_id>/` · `results/study2_dream_curriculum/isaac/<run_id>/`

## Design

See [`docs/stage2/dream_curriculum_sandbox_v0.1.md`](../../../docs/stage2/dream_curriculum_sandbox_v0.1.md)

**Paper outline:** [`docs/stage2/study2_paper_outline_v0.1.md`](../../../docs/stage2/study2_paper_outline_v0.1.md)

## Boundary

- **Not** Paper 1 confirmatory · parallel RQ probe (discovery voice ①)
- **Not** full ReSYNC / IVNTR — perturbation-param dreaming only (v0.1)
- Isaac hook: reuse 001A injection points when mock metrics look good
