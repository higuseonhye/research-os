# When reality outruns the model: representation reconstruction

> Live: **[higuseonhye.github.io/research-os](https://higuseonhye.github.io/research-os/)**
> Source: [`docs/index.md`](../index.md)

---

**Research question:** When persistent observations cannot be explained by the
current model class, when should an embodied system expand its predictive state
instead of continuing to retune parameters?

| Program | Evidence | Status |
| --- | --- | --- |
| **Paper 001** | Recoverability at fixed mismatch state | Tier C complete - [working paper](https://github.com/higuseonhye/research-os/blob/master/docs/paper1/paper001_recoverability_complete.pdf) |
| **Paper 002** | Failure-conditioned target-dynamics model-order expansion | Tier C confirmatory complete - [manuscript v1.1](https://github.com/higuseonhye/research-os/blob/master/docs/paper002/paper002_manuscript_model_order_v1.1.pdf) |
| **Mismatch Lab** | Robot Diff and model-adequacy open specification | Public spec - [hub](https://github.com/higuseonhye/research-os/tree/master/docs/mismatch_lab) |
| **Study 002** | Dream-curriculum pilot | Tier B archived |

## Paper 002: Confirmatory Result

A preregistered Isaac Sim study compared repaired zero-order target dynamics
with a gated constant-velocity state expansion. The confirmatory grid completed
all **400/400** seed-condition-arm cells.

| Primary endpoint | C vs B result |
| --- | ---: |
| H=10 prediction error | **-10.806 mm**, 95% CI [-11.360, -10.331] |
| Fixed-horizon final distance | **-13.304 mm**, 95% CI [-13.599, -12.982] |

The expanded model was favorable in 100/100 paired conditions on both continuous
endpoints. Static retention passed for both arms, and the adequacy gate fired on
100/100 persistent-drift trials and 0/100 static, noise, and impulse controls.

[Paper 002 hub](https://github.com/higuseonhye/research-os/tree/master/docs/paper002)

[Manuscript v1.1 PDF](https://github.com/higuseonhye/research-os/blob/master/docs/paper002/paper002_manuscript_model_order_v1.1.pdf)

[Supplement v1.1 PDF](https://github.com/higuseonhye/research-os/blob/master/docs/paper002/paper002_supplement_model_order_v1.1.pdf)

[Confirmatory results and provenance](https://github.com/higuseonhye/research-os/blob/master/experiments/surgical_intelligence/exp_surg_003_wm_expansion/results/isaac_model_order_confirmatory_v1.0/RESULTS.md)

## Claim Boundary

Supported: within the tested Isaac target-drift family, structured failure after
zero-order repair can warrant a prepared velocity-state expansion that improves
prediction-linked control without static regression.

Not claimed: general world-model expansion, autonomous variable invention,
hardware transfer, tissue/contact validity, clinical efficacy, or peer-reviewed
publication.

## More

[Research OS](https://github.com/higuseonhye/research-os)

[Paper 001](https://github.com/higuseonhye/research-os/tree/master/docs/paper1)

[Mismatch Lab demo](https://higuseonhye.github.io/research-os/mismatch_lab/diff_explorer_v0.1.html)

[Public boundary](https://github.com/higuseonhye/research-os/blob/master/docs/PUBLIC_BOUNDARY.md)

---

*Updated 2026-07-30*
