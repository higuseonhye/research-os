# Paper 001 — figures & tables

> **Generated:** `python scripts/plot_paper1_figures.py`  
> **Isaac captures:** `bash scripts/capture_study1_viewport.sh` (GPU) → `plot_paper1_from_ee_traces.py`

---

## Main text

| Fig | File | Tier | Description |
| --- | --- | --- | --- |
| **1** | [`fig1_architecture_overview.png`](fig1_architecture_overview.png) | A | System stack + same-state CF evaluation pipeline |
| **2** | [`fig2_same_state_fork.png`](fig2_same_state_fork.png) | C | Branching at mismatch onset **S** |
| **3** | [`fig3_profile_d0.png`](fig3_profile_d0.png) | C | D0 five-mode recoverability profile (n=20) |
| **4** | [`fig4_baseline_overlay.png`](fig4_baseline_overlay.png) | C | Menu vs B2 vs B3 @ fixed **S** |
| **5** | [`fig5_occlusion_contrast.png`](fig5_occlusion_contrast.png) | C | D0 occluded vs D1 no-occlusion (RQ-P) |

## Tables

| Table | File | CSV |
| --- | --- | --- |
| **1** D0 profiles | [`table1_d0_results.png`](table1_d0_results.png) | [`tables/table1_d0.csv`](tables/table1_d0.csv) |
| **2** Program summary | [`table2_proper_program.png`](table2_proper_program.png) | [`tables/table2_program.csv`](tables/table2_program.csv) |

## Simulation panels

| Panel | File | Source |
| --- | --- | --- |
| CONTINUE vs REPLAN schematic | [`sim_panel_continue_replan.png`](sim_panel_continue_replan.png) | CPU schematic (protocol geometry) |
| Multi-mode menu | [`sim_panel_multimode.png`](sim_panel_multimode.png) | CPU schematic |
| Isaac EE traces | [`sim_panel_isaac_traces.png`](sim_panel_isaac_traces.png) | GPU capture → [`isaac_captures/`](isaac_captures/) |

Captions: [`../fig_captions.md`](../fig_captions.md)
