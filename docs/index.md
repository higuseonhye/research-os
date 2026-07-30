# Seonhye Gu | Physical AI Research

Independent research on model adequacy, embodied world models, and failure
analysis in simulation.

[GitHub](https://github.com/higuseonhye/research-os) | [Paper 002](paper002/README.md) | [Mismatch Lab](mismatch_lab/README.md)

## Current Work: Paper 002

**When should an embodied agent expand its predictive model instead of
continuing to retune it?**

Paper 002 studies that decision in a preregistered Isaac Sim target-drift
experiment. After the best allowed zero-order parameter repair, a rule-based
adequacy gate can activate a prepared constant-velocity state expansion.

[Read the manuscript PDF](paper002/paper002_manuscript_model_order_v1.1.pdf) | [Supplement](paper002/paper002_supplement_model_order_v1.1.pdf) | [Results and provenance](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_model_order_confirmatory_v1.0/RESULTS.md)

![Confirmatory prediction and control outcomes](paper002/figures/fig2_confirmatory_outcomes.png)

### Confirmatory Result

The complete confirmatory grid contained **400/400 valid
seed-condition-arm cells**. Relative to repaired zero order, gated
constant-velocity expansion produced:

| Primary endpoint | C vs B result | Crossed-bootstrap 95% interval |
| --- | ---: | ---: |
| H=10 prediction error | **-10.806 mm** | [-11.360, -10.331] mm |
| Fixed-horizon final distance | **-13.304 mm** | [-13.599, -12.982] mm |

The expanded model was favorable in **100/100 paired conditions** on both
continuous endpoints. Static retention passed. The adequacy gate fired on
**100/100 persistent-drift trials** and **0/100** static, observation-noise, and
single-impulse controls.

The evidence supports a prepared model-order expansion within the tested Isaac
target-drift family. It does not establish general world-model expansion,
autonomous variable invention, hardware transfer, tissue or contact validity,
clinical efficacy, or peer-reviewed publication.

## Research Portfolio

| Project | Question | Evidence |
| --- | --- | --- |
| **Paper 002 / EXP-SURG-003** | When does structured failure warrant model-order expansion after parameter repair? | Tier C confirmatory complete; [manuscript v1.1](paper002/paper002_manuscript_model_order_v1.1.pdf) |
| **Paper 001 / EXP-SURG-001** | Is a failed state recoverable under a same-state counterfactual intervention? | Tier C complete; [working paper](paper1/paper001_recoverability_complete.pdf) |
| **Mismatch Lab** | How can robot rollouts expose behavior differences that may indicate model inadequacy? | Public specification and [Robot Diff demo](mismatch_lab/diff_explorer_v0.1.html) |

## Research Practice

- Preregistered confirmatory designs and explicit claim boundaries
- Process-isolated simulation cells with complete execution-validity checks
- Paired continuous endpoints, negative controls, and reproducible artifacts
- Public code, configurations, trajectories, figures, and checksum manifests

Paper 002 was independently conducted as personal research while Seonhye Gu
was affiliated with the AI-Based Surgical Robot Innovation Lab. The affiliation
is provided for identification only and does not imply official sponsorship or
institutional endorsement.

Contact: [@higuseonhye](https://github.com/higuseonhye)

---

*Updated 2026-07-30*
