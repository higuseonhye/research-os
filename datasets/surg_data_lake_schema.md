# Surg-Data Lake Schema v0.1

> Draft metadata contract for surgical intelligence datasets · July 2026

## Purpose

Define how external datasets (LEMON, ORBIT logs, dVRK demos, tool detection outputs) register in one **metadata layer** without storing blobs in Git.

## Asset Record (JSON / YAML per asset)

```yaml
asset_id: string          # unique, e.g. lemon:video:000123
source: enum              # lemon | orbit_rollout | dvrk | synthetic | tool_detect | twelvelabs_index
provenance:
  uri: string             # HF path, S3, or local path (not in git)
  license: string
  access_date: date
modality:
  - video | proprio | language | action | reward
robotic_context:
  is_robotic_assisted: bool
  platform: string        # da_vinci | star | shadow_hand | unknown
procedure_tags: [string]
task_contract:            # optional link to SIB
  sib_task_id: string     # e.g. sib.reach.dual_star.v0
  observation_space: string
  action_space: string
quality:
  fps: number
  resolution: [w, h]
  duration_s: number
experiment_links:
  - experiment_id: string
  - commit_sha: string
rq_mapping: [RQ1 | RQ2 | RQ3 | RQ4]
search_index:             # optional — Twelve Labs / future providers
  provider: string         # twelvelabs
  index_id: string
  indexed_asset_id: string
  model: string            # marengo3.0
  indexed_at: date
segments:                  # NL search hits (timestamps only)
  - query_id: string
    query_text: string
    rank: int
    start_s: float
    end_s: float
```

## Collection Manifest (repo-safe)

Store under `datasets/manifests/` (git):

```yaml
collection: surg_data_lake_v0.1
assets:
  - asset_id: orbit:rollout:reach_zero_20260708
    source: orbit_rollout
    sib_task_id: sib.reach.dual_star.v0
    experiment_links:
      - experiment_id: EXP-SRFM-002
```

## Phase 2 Population Plan

| Source | Phase 2 action |
| --- | --- |
| LEMON | HF access → first 10-asset manifest |
| Twelve Labs index | 1-clip search smoke → `twelvelabs_lemon_v0.yaml` |
| ORBIT rollouts | already in `benchmark/leaderboard/reach_v0.md` |
| DexBench | crosswalk metadata only |
| Tool detection | add after EXP-SI-PER-002 |

## Next

- [x] Create `datasets/manifests/orbit_reach_v0.yaml` from existing artifacts
- [x] Add LEMON assets after HF approval (`lemon_v0.yaml`, 10-asset subset)
