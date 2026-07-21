# EXP-SURG-002 — Dream curriculum sandbox (Stage 2 probe)

> **Status:** v0.1 desk mock · not Paper 1 evidence  
> **Design docs:** **private** — [builder-os-private stage2](https://github.com/higuseonhye/builder-os-private/tree/master/working/research/stage2)  
> **Parent:** EXP-SURG-001 perturbation taxonomy + mock reach

## Quick start (no GPU)

```bash
python scripts/run_study2_dream_curriculum_mock.py --dreamer diffusion --agent rule --episodes 32
python scripts/run_study2_dream_curriculum_mock.py --compare --episodes 48
```

## Phase 1 (RunPod)

Pre-reg (private): [study2_prereg_v0.1.md](https://github.com/higuseonhye/builder-os-private/blob/master/working/research/stage2/study2_prereg_v0.1.md)

```bash
bash scripts/run_study2_dream_curriculum_runpod.sh
```

## Boundary

- **Not** Paper 1 confirmatory · parallel L1 probe (discovery voice)
- **Not** full ReSYNC / IVNTR — perturbation-param dreaming only (v0.1)
- Narrative / RQ / paper outline: **private until PI sign-off**
