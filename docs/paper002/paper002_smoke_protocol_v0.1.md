# Paper 002 — Seed-43 smoke protocol v0.1

> **Purpose:** engineering pipeline validation only · **not** confirmatory  
> **When:** after v0.3 commit · **before** mock seeds 42–46 consensus export  
> **Pre-reg:** [paper002_prereg_v0.3.md](paper002_prereg_v0.3.md) §9

---

## Allowed uses

- Verify mock runner + `cf_margin` on local CPU  
- Verify Isaac study1d runner + zero_agent on VESSL  
- Verify promote/copy scripts end-to-end on **1–2 specs**  
- Confirm occlusion transfer smoke (one spec with occlusion_gain > 0)

---

## Forbidden uses

| Forbidden | Why |
| --- | --- |
| Include seed-43 mock in **consensus export** (Leg 4) | Confirmatory ranking must use seeds 42–46 median only |
| Adjust thresholds, weights, mapping from smoke | Pre-reg drift |
| Add/remove export candidates based on smoke Isaac outcomes | Manifest must be frozen pre-confirmatory |
| Label smoke results as Tier A / confirmatory | Engineering only |

---

## Procedure

### CPU mock smoke (local)

```bash
python scripts/run_study2_dream_curriculum_mock.py \
  --config experiments/.../config/sandbox_v0.4.yaml \
  --compare --episodes 16 --seed 43 --agent rule \
  --promote-label smoke_seed43_mock_v0.1
```

**Do not** merge `smoke_seed43_*` into `mock_confirmatory_v0.1`.

### Isaac smoke (VESSL · optional · 1–2 specs)

- Export 1 top spec from smoke mock **separate manifest**: `artifacts/isaac_specs_smoke_seed43.json`  
- Run Isaac · promote to `results/smoke_seed43_isaac_v0.1/`  
- Record RUN_ID · git SHA · zero_agent pass/fail

---

## Required artifacts

| Artifact | Label prefix |
| --- | --- |
| Mock records | `smoke_seed43_mock_v0.1/` |
| Export manifest | `isaac_specs_smoke_seed43.json` |
| Isaac aggregate | `smoke_seed43_isaac_v0.1/` |
| Run log | `smoke_seed43_run_log.json` |

Run log must state: `"tier": "engineering_smoke"`, `"excluded_from_confirmatory": true`.

---

## Relation to confirmatory export

```text
smoke seed 43  ──► engineering only · separate manifest
confirmatory   ──► seeds 42–46 median · frozen checksum manifest
```

No shared spec_ids between smoke and confirmatory manifests.
