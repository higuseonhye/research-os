# Paper 1 — Figure captions (v0.2 · Tier C)

> **Evidence:** EXP-SURG-001 proper program D0–D3 · Isaac Sim 4.1 · ORBIT IK-Rel  
> **Regenerate:** `python scripts/plot_paper1_figures.py`  
> **Isaac capture:** `bash scripts/capture_study1_viewport.sh` (GPU)

---

## Fig 1 — Architecture overview

> **Figure 1.** Paper 001 evaluation architecture. A frozen scripted proposer executes nominal reach until mismatch onset **S** (6 cm target shift + occlusion proxy L1 in D0). Recorded actions are replayed from the same seed so all branches share identical state through **S**; only the post-onset response differs. Terminal outcomes are judged by distance to the shifted target (≤ 2 cm), forbidden-zone violations, and step budget. The upper row situates the measurement within a broader surgical agent stack (Stage 2+); Paper 001 claims profile separation, not a learned selector.

PNG: [`fig1_architecture_overview.png`](figures/fig1_architecture_overview.png)

---

## Fig 2 — Same-state counterfactual fork

> **Figure 2.** Same-state counterfactual fork at mismatch onset **S** (step 20). All branches replay identical pre-onset actions, apply the same target shift, then diverge by response mode. D0 confirmatory rates (n=20): REPLAN_d20 19/20, REOBSERVE 17/20, RESHAPE 18/20, CONTINUE 0/20, HANDOVER stub 0/20.

PNG: [`fig2_same_state_fork.png`](figures/fig2_same_state_fork.png)

---

## Fig 3 — D0 recoverability profile

> **Figure 3.** Intervention-conditioned recoverability profile at fixed mismatch onset **S** (6 cm Y shift + occlusion L1 · REPLAN delay 20 steps · n=20). Same-state counterfactual branches share replay through **S**; success = terminal distance to shifted target ≤ 2 cm without forbidden violation. Error bars: Wilson 95% CI. HANDOVER is a collaboration stub excluded from the primary endpoint.

PNG: [`fig3_profile_d0.png`](figures/fig3_profile_d0.png) · Table: [`table1_d0_results.png`](figures/table1_d0_results.png)

---

## Fig 4 — Baseline overlay (RQ-B)

> **Figure 4.** Response menu vs rule baselines at the same anchor **S**. Best-of-menu (max of REPLAN, REOBSERVE, RESHAPE) reaches 95%; REPLAN_d20 alone 95%; B3 situation rule (REOBSERVE path) 85%; B2 UQ-inspired binary rule triggers HANDOVER on all 20 seeds (0% success on primary metric). Pre-registered Option A direction met: menu best > B2 and > B3.

PNG: [`fig4_baseline_overlay.png`](figures/fig4_baseline_overlay.png)

---

## Fig 5 — Occlusion contrast (RQ-P)

> **Figure 5.** Descriptive occlusion contrast: D0 (occlusion L1) vs D1 (no occlusion) for CONTINUE and REPLAN_d20 @ fixed **S**. REPLAN remains 19/20 in both conditions; CONTINUE rises from 0/20 to 1/20 without occlusion. No superiority claim beyond pre-registered descriptive contrast.

PNG: [`fig5_occlusion_contrast.png`](figures/fig5_occlusion_contrast.png)

---

## Simulation panels

> **Simulation panel (schematic).** Top-down ORBIT Dual-STAR Reach workspace showing frozen vs shifted targets, forbidden AABB proxy, and schematic EE divergence after **S**. Static PNG for paper; reproducible Isaac EE traces via `scripts/capture_study1_viewport.sh`.

PNG: [`sim_panel_continue_replan.png`](figures/sim_panel_continue_replan.png) · [`sim_panel_multimode.png`](figures/sim_panel_multimode.png)

**Isaac EE traces (Tier C · seed 0 · 2026-07-24):** [`sim_panel_isaac_traces.png`](figures/sim_panel_isaac_traces.png) · traces in [`isaac_captures/`](figures/isaac_captures/)

---

## Appendix — smoke figures (Tier B)

### Fig A1 — Counterfactual grid (001A smoke)

> Smoke n=5 · 3 cm shift · CONTINUE 0/5 vs REPLAN 4/5. Superseded for claims by Fig 3 (Tier C).

PNG: [`counterfactual_grid.png`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1a_isaac/figures/counterfactual_grid.png)

### Fig A2 — Delay curve (001B smoke)

> Flat REPLAN band at P2@3 cm · RQ-T deferred from main text.

PNG: [`recoverability_vs_delay.png`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1b_isaac/figures/recoverability_vs_delay.png)

---

## Shared disclaimer

```text
Scripted proposer · single ORBIT reach task · occlusion gain-scale proxy v0.1.
Tier C: pre-reg v2.0 · n=20 per branch · branch_replay_ok on all records.
```
