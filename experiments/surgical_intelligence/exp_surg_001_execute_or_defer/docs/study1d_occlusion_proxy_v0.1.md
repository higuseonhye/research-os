# EXP-SURG-001D — Occlusion proxy contract v0.1

> **Status:** active for D0 smoke · **Date:** 2026-07-22  
> **Config:** [`../config/study1d_occlusion_multimode.yaml`](../config/study1d_occlusion_multimode.yaml)

---

## Purpose

Define a **minimal, reproducible** P3 occlusion proxy before scene geometry (occluder mesh) is wired in ORBIT Reach.  
Every run must label the proxy in `run_manifest.json` and per-branch JSON.

---

## v0.1 proxy: `gain_scale_flag`

| Field | Value |
| --- | --- |
| `proxy_type` | `gain_scale_flag` |
| `proxy_version` | `v0.1` |
| Onset | step **20** (same as target shift) |
| Co-occurring | **6 cm** target shift (Y+) |

**Mechanism (Isaac + mock):**

1. At onset, set `visibility_recoverable=False` and `visibility_fraction` from level table.
2. While occlusion active and **not cleared**, scale scripted proposer gain by `visibility_fraction`.
3. **REOBSERVE:** hold `reobserve_hold_steps` (default 10) with zero delta action → set `visibility_cleared=True` → REPLAN@0 chase shifted target at full gain.
4. **RESHAPE (D1):** for `reshape_steps`, apply visibility clear + optional camera-root nudge proxy → REPLAN@0.
5. **HANDOVER (D1):** zero action until terminal · category `handover_proxy`.

**Not modeled in v0.1:** RGB dropout · actual FOV block · learned detector.

---

## Occlusion levels

| Level | `visibility_fraction` | Label |
| ---: | ---: | --- |
| 1 | 0.35 | `mild_occlusion_gain_scale` |
| 2 | 0.20 | `moderate_occlusion_gain_scale` |

---

## Artifact fields (required)

Per branch record:

```json
{
  "perturbation_id": "P3",
  "occlusion_proxy": "gain_scale_flag_v0.1",
  "occlusion_level": 1,
  "visibility_fraction": 0.35,
  "visibility_cleared": false,
  "response_class": "policy"
}
```

Run manifest:

```json
{
  "occlusion_proxy_version": "v0.1",
  "blockers_waived": ["occlusion_proxy"],
  "blockers_deferred": ["reshape_skill", "handover_proxy"]
}
```

---

## Upgrade path (v0.2+)

| Version | Change |
| --- | --- |
| v0.2 | Scene occluder prim spawn @ onset · keep gain_scale as fallback |
| v0.3 | RGB obs dropout aligned with `s_odd_needle_reaching.yaml` `rgb_target_in_fov_fraction` |

---

## Mode semantics (001D v0.1)

| Mode | Branch behavior after onset @ S |
| --- | --- |
| CONTINUE | Frozen target · occluded gain until end |
| REPLAN @ d=20 | Frozen + occluded gain until switch · full gain to shifted |
| REOBSERVE | Hold 10 steps · clear visibility · replan shifted @ full gain |
| RESHAPE | D1 · clear visibility after reshape_steps · replan |
| HANDOVER | D1 · freeze · early terminal |

Judge unchanged: distance to **shifted** target · tol 0.02 m · forbidden AABB.
