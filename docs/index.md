# Seonhye Gu | Research Portfolio

**When should an intelligent system decide that its current understanding of the
world is no longer sufficient — and how should it construct a better one?**

That question is the through-line of everything below. Physical AI is the
current testbed, not the boundary of the question: embodiment is used because it
makes mismatch, timing, intervention, and recovery observable and consequential.

[Research program](program/README.md) | [GitHub](https://github.com/higuseonhye/research-os) | [Mismatch Lab](mismatch_lab/README.md)

## The Sequence

Each paper changes the decision under test, not the question.

| | Decision under test | Status |
| --- | --- | --- |
| **Paper 001** | Is the failure recoverable at all? | Tier C complete |
| **Paper 002** | Repair the parameters, or change the model class? | Tier C complete |
| **Paper 003** | Does changing it open capability a repair cannot reach? | Design |

## Paper 002 — Failure-Conditioned Model-Order Expansion

**When should an embodied agent expand its predictive model instead of
continuing to retune it?**

A preregistered Isaac Sim target-drift experiment. After the best allowed
zero-order parameter repair, a rule-based adequacy gate can activate a prepared
constant-velocity state expansion.

[Project page](paper002/project_page.html) | [Manuscript PDF](paper002/paper002_manuscript_model_order_v1.1.pdf) | [Supplement](paper002/paper002_supplement_model_order_v1.1.pdf) | [Results and provenance](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_model_order_confirmatory_v1.0/RESULTS.md)

[![Arm-level prediction, control, and success outcomes](paper002/figures/fig2_confirmatory_outcomes.png)](paper002/project_page.html)
<br><sub>Arm-level prediction, control, and success outcomes across the 400-cell confirmatory grid, plotted from the frozen result artifact.</sub>

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

## Paper 003 — Beyond Error Reduction (design)

**When the gap is a missing *relation* between entities rather than a missing
mode, does structural expansion open task capability that repair cannot reach?**

Paper 002 measured success as lower prediction error. Paper 003 asks a harder
question: does expansion move task variants from **unachievable to achievable**?

Two design-stage findings, both from running the code rather than reasoning
about it:

- **The relation gate separates cleanly.** It fires 10/10 on proximity-driven
  coupling and **0/10** on the persistent drift Paper 002 handles — necessary,
  because firing there would mean the existing mode operator already explains
  the failure.
- **The task shape decides whether anything is measurable at all.** In a
  continuous reach-and-hold task the arms were indistinguishable, because
  continuous re-aiming averages prediction error away. Adding an **irreversible
  commitment** separated them completely:

| Task | Parameter repair | Mode expansion | Relation expansion |
| --- | ---: | ---: | ---: |
| Continuous tracking | 0.30 | 0.25 | 0.35 |
| **Commitment point** | **0.00** | 0.29 | **0.69** |

Arm B's lockout speed is predicted from the task geometry rather than fitted, so
it can be preregistered as a point prediction. The relation arm **estimates** the
second entity's motion from observation rather than being told it; under a clean
observation it reaches 1.00, and the 0.69 above is what it costs to have to infer
the relation under noise. An oracle arm is kept as an explicit ceiling.

**Design-stage only** — not preregistered, not run in Isaac. See the
[Paper 003 hub](paper003/README.md) and
[commitment-point task](paper003/paper003_commitment_task_v0.1.md).

## Research Portfolio

| Project | Question | Evidence |
| --- | --- | --- |
| **Paper 002 / EXP-SURG-003** | When does structured failure warrant model-order expansion after parameter repair? | Tier C confirmatory complete; [project page](paper002/project_page.html) · [manuscript v1.1](paper002/paper002_manuscript_model_order_v1.1.pdf) |
| **Paper 003** | When failure reveals a missing *relation*, does expansion unlock capability, not just lower error? | Design v0.1; [docs](paper003/README.md) |
| **Paper 001 / EXP-SURG-001** | Is a failed state recoverable under a same-state counterfactual intervention? | Tier C complete; [working paper](paper1/paper001_recoverability_complete.pdf) |
| **Mismatch Lab** | How can robot rollouts expose behavior differences that may indicate model inadequacy? | Public specification and [Robot Diff demo](mismatch_lab/diff_explorer_v0.1.html) |

## Research Practice

- Preregistered confirmatory designs and explicit claim boundaries
- Process-isolated simulation cells with complete execution-validity checks
- Paired continuous endpoints, negative controls, and reproducible artifacts
- Public code, configurations, trajectories, figures, and checksum manifests
- Negative and design-stage results are published alongside positive ones, with
  the reasoning that produced them

Paper 002 was independently conducted as personal research while Seonhye Gu
was affiliated with the AI-Based Surgical Robot Innovation Lab. The affiliation
is provided for identification only and does not imply official sponsorship or
institutional endorsement.

Contact: [@higuseonhye](https://github.com/higuseonhye)

---

*Updated 2026-07-31*
