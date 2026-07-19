# Paper 1 — Figure captions (frozen v0.1)

> **Evidence:** EXP-SURG-001A/B Isaac · scripted IK-Rel  
> Do not change without bumping version.

---

## Fig 4 — Counterfactual same-state grid

> **Figure 4.** Same-state counterfactual after a task-relevant target shift. From a shared onset state on ORBIT Dual-STAR Reach (IK-Rel), CONTINUE keeps the pre-shift end-effector command while REPLAN tracks the shifted command. Under a scripted pose-relative controller, REPLAN yields successful resolution more often than CONTINUE (Isaac smoke: CONTINUE 0/5 vs REPLAN 4/5; success tolerance 2 cm; shift 3 cm). Preferred response is labeled from terminal outcomes, not from a taxonomy lookup.

**Allowed:** mode separation on this proxy · same-state branching works  
**Not allowed:** learned meta-policy · clinical · universal golden-time law

PNG: [`counterfactual_grid.png`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1a_isaac/figures/counterfactual_grid.png)

---

## Fig 5 — Recoverability vs replan delay

> **Figure 5.** Empirical recoverability versus replan delay for the same target-shift family. After onset, REPLAN is deferred by 0 / 5 / 10 / 20 control steps while CONTINUE never updates the command. For a mild 3 cm shift, REPLAN succeeds at all tested delays (3/3 each), whereas CONTINUE fails (0/3). The smoke shows a **flat high-recoverability band** for delayed REPLAN rather than a sharp cliff—bounding when delay begins to matter at this severity, not yet proving a universal golden-time curve.

**Allowed:** delay as axis · flat band at P2@3 cm  
**Not allowed:** single golden \(t^\star\) · timing novelty settled

PNG: [`recoverability_vs_delay.png`](../../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1b_isaac/figures/recoverability_vs_delay.png)

---

## Shared disclaimer

```text
Smoke · scripted proposer · n small · ORBIT reach proxy.
Paper 1 claims require evidence beyond these plots.
```
