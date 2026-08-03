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
| **Paper 003** | Does changing it open capability a repair cannot reach? | Isaac pilot run; not preregistered |

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

### The task shape decides whether anything is measurable

In a continuous reach-and-hold task the arms were **indistinguishable**, because
continuous re-aiming averages prediction error away. Only an **irreversible
commitment** — a placement that cannot be corrected once made — separated them.
That negative result is what produced the design.

### Isaac calibration pilot

Ten seeds, four conditions, run in simulation. **Excluded from confirmatory
evidence**, in the same posture as Paper 002's engineering pilot.

| Condition | Missing structure | Parameter repair | Mode expansion | Relation expansion |
| --- | --- | ---: | ---: | ---: |
| Coupled | relation | 0.56 | 0.22 | **0.67** |
| Drift | mode | 0.00 | **1.00** | 0.00 |
| Static / noise | none | 1.00 / 0.40 | 1.00 / 0.00 | 1.00 / 0.40 |

**The result is the dissociation, not the relation arm winning.** The mode
operator takes the drift condition outright and the relation operator declines
there, scoring identically to plain repair. Each answers only the gap it was
built for — which is what rules out the relation arm simply being a stronger
predictor. On both no-gap conditions it is numerically identical to repair, so
adding the operator costs nothing where it does not apply.

**Its 0.67 against 0.56 is six cells against five.** One cell. Reported as a
sample-size observation, not an effect.

### What was withdrawn

An earlier version of this page reported the relation arm at 1.00. That came
from a **degenerate encounter geometry** — a fixed head-on approach, which made
ten seeds ten translations of a single encounter and concealed a modelling
error. Once the geometry was randomised the arm fell to worse than plain repair,
the error was found and fixed, and the original figure was retracted.

**Design-stage** — not preregistered. The coupling is still injected rather than
arising from simulated contact, so the relation arm inverts a function this
repository wrote; under real contact its model becomes misspecified and its
accuracy is **expected to drop**, a prediction recorded before that run. See the
[Paper 003 hub](paper003/README.md), the
[pilot results and correction log](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/isaac_relation_pilot_v0.1/RESULTS.md),
and the [draft preregistration](paper003/paper003_prereg_draft_v0.1.md).

## Research Portfolio

| Project | Question | Evidence |
| --- | --- | --- |
| **Paper 002 / EXP-SURG-003** | When does structured failure warrant model-order expansion after parameter repair? | Tier C confirmatory complete; [project page](paper002/project_page.html) · [manuscript v1.1](paper002/paper002_manuscript_model_order_v1.1.pdf) |
| **Paper 003** | When failure reveals a missing *relation*, does expansion unlock capability, not just lower error? | Calibration pilot run, excluded from evidence; [docs](paper003/README.md) · [pilot results](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/isaac_relation_pilot_v0.1/RESULTS.md) |
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

*Updated 2026-08-04*
