# Experiment loop (public)

Every package follows the same rhythm:

1. **Smoke** — validate pipeline and direction (Tier B · small n)
2. **Proper** — pre-registered scale (Tier C · frozen design)
3. **Update** — committed summaries in `experiments/.../results/`
4. **Adjust** — next hypothesis from data · log in design doc appendix or new version

Pre-registration **freezes design**, not permission to run. Direction changes get a new version or appendix — not silent edits to frozen cells.

**Examples in this repo:**

| Package | Design doc | Results |
| --- | --- | --- |
| Paper 1 Phase C | [`phase_c_proper_run_prereg_v1.0.md`](paper1/phase_c_proper_run_prereg_v1.0.md) | [`study1_proper/summary.json`](../experiments/surgical_intelligence/exp_surg_001_execute_or_defer/results/study1_proper/summary.json) |
| Study 2 Phase 1 | [`stage2/study2_phase1_design_v0.1.md`](stage2/study2_phase1_design_v0.1.md) | [`exp_surg_002/results/`](../experiments/surgical_intelligence/exp_surg_002_dream_curriculum/results/) |
