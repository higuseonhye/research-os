# EXP-SURG-003 — Paper 002 WM expansion confirmatory

> **Paper:** [docs/paper002/](../../../docs/paper002/) · [confirmatory spec](../../../docs/paper002/paper002_confirmatory_spec_v0.1.md)  
> **Status:** scaffold · **not started** · pre-reg not frozen  
> **Parent:** EXP-SURG-001 ORBIT reach pipeline

---

## What this experiment tests

```text
Train static-only WM (W0)
→ Ep1 persistent drift failure
→ K × L1 repair fails
→ Arms: A none · B repair F0 · C add F1+G
→ Ep2 novel drift
→ Primary: prediction error (H=10) · task success · static retention · gate H4
```

**First milestone:** find drift regime where **L1 fails but L3 succeeds** (pilot only).

---

## Config

| File | Role |
| --- | --- |
| [`config/confirmatory_v0.1.yaml`](config/confirmatory_v0.1.yaml) | Phase · arms · drift · gate · outcomes skeleton |

---

## Implementation status

| Step | Status |
| --- | --- |
| Target drift env params in ORBIT reach | ⏳ |
| GRU/RSSM-lite W0 pretrain | ⏳ |
| MPC ← WM rollouts | ⏳ |
| Arms A/B pilot | ⏳ |
| F1 + G (L3) | ⏳ |
| Gate negative controls N1/N2 | ⏳ |
| Confirmatory run | ⏳ after pre-reg freeze |

---

## Quick start (future)

```bash
# Engineering pilot (not confirmatory)
python scripts/run_exp_surg_003_pilot.py --config experiments/surgical_intelligence/exp_surg_003_wm_expansion/config/confirmatory_v0.1.yaml --tier pilot

# Confirmatory (after freeze + fresh seeds)
python scripts/run_exp_surg_003_confirmatory.py --config ... --tier confirmatory
```

Scripts **not yet implemented** — config and spec define the contract.

---

## Results

```text
results/
  pilot_v0.1/       # excluded from confirmatory analysis
  confirmatory_v0.1/  # post freeze
```

Empty until first pilot run.

---

## Boundary

- Not Paper 001 confirmatory  
- Not mock→physics (archived)  
- Oracle arm D = diagnostic only · excluded from primary contrasts  
- Public: frozen design + tier-labeled results per [`PUBLIC_BOUNDARY.md`](../../../docs/PUBLIC_BOUNDARY.md)

---

## Docs

- [Confirmatory spec](../../../docs/paper002/paper002_confirmatory_spec_v0.1.md)
- [Pre-reg draft](../../../docs/paper002/paper002_prereg_wm_expansion_v0.1.md)
- [Analysis plan v0.3](../../../docs/paper002/paper002_analysis_plan_v0.3.md)
