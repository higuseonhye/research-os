<section class="hero">
  <p class="kicker">Independent research | Physical AI as the current testbed</p>
  <h1>After the Spill</h1>
  <p class="lead">How far should an embodied system change after unexpected experience?</p>
  <p>
    Robots and embodied agents do not only need to learn from experience. They
    need to decide whether an experience is noise, a recoverable disturbance, a
    sign of model inadequacy, or evidence that the system itself must change.
  </p>
  <p class="cta-row">
    <a class="button primary" href="program/after_the_spill_v2.html">Program charter</a>
    <a class="button" href="paper002/project_page.html">Paper 002 evidence</a>
    <a class="button" href="mismatch_lab/">Mismatch Lab</a>
    <a class="button" href="https://github.com/higuseonhye/builder-lab">Builder Lab</a>
  </p>
</section>

## The Question

Most AI research asks:

> How should a system learn?

This program asks a narrower and harder question:

> **How much should a system change after reality contradicts its current model?**

The research object is the change decision:

```text
Experience -> Evidence -> Operator -> Closure
```

The working principle is simple enough to be useful and dangerous enough to
audit:

> Intelligence is the ability to determine the smallest sufficient change after
> unexpected experience.

## What Exists Here

<div class="evidence-grid">
  <div>
    <h3>Foundation</h3>
    <p>D000-D006 define the program's formal objects, terminology, novelty audit, literature matrix, evaluation protocol, and roadmap.</p>
  </div>
  <div>
    <h3>Papers</h3>
    <p>Paper 001-005 test different change operators: recover, repair, expand, dispose, and coordinate.</p>
  </div>
  <div>
    <h3>Products</h3>
    <p>Robot Diff and Mismatch Lab turn rollout comparison into evidence for model adequacy and recovery decisions.</p>
  </div>
  <div>
    <h3>Builder Lab</h3>
    <p>Small, reproducible Physical AI experiments. Current status: Planning.</p>
  </div>
</div>

## Evidence So Far

| Track | What it contributes | Status |
| --- | --- | --- |
| **Paper 001: Recoverability** | Measures whether a system can still recover from the same post-mismatch state | Tier C complete |
| **Paper 002: Model Adequacy** | Tests when parameter repair should give way to a prepared model-order expansion | Tier C complete |
| **Paper 003: Representation Expansion** | Tests whether adding a missing relation can open capability repair cannot reach | Negative under real contact; written up |
| **Mismatch Lab** | Public surface for diff, replay, explanation, and benchmark design | Spec/demo |
| **Builder Lab** | Public execution surface for small Physical AI experiments | Planning |

Selected proof points:

- Paper 001: REPLAN 19/20 vs CONTINUE 0/20 under a fixed mismatch state.
- Paper 002: 400/400 valid confirmatory cells; gated expansion improves prediction-linked control without static regression in the tested target-drift family.
- Paper 003: the prepared relation operator did not transfer to real contact; the mode operator remained sufficient in the tested scene.

## Program Map

| Paper | Core decision | Operator |
| --- | --- | --- |
| **001 Recoverability** | Can the system still recover from here? | Recover / Replan |
| **002 Model Adequacy** | Is repair inside the current model class still enough? | Repair / Expand |
| **003 Representation Expansion** | Is the missing thing a representation? | Expand |
| **004 Experience Disposition** | What should be done with the experience itself? | Ignore / Preserve / Escalate |
| **005 Recovery Orchestration** | How should multiple recovery capabilities be sequenced? | Coordinate |

## Start Here

| If you want... | Go to |
| --- | --- |
| The whole program in one document | [After the Spill v2](program/after_the_spill_v2.md) |
| The document that tries to break the idea | [D001 Claim & Novelty Audit](program/D001_claim_novelty_audit.md) |
| The strongest current evidence | [Paper 002 project page](paper002/project_page.html) |
| The public product/lab surface | [Mismatch Lab](mismatch_lab/) |
| The public execution lab | [Builder Lab](https://github.com/higuseonhye/builder-lab) |
| The repository | [GitHub](https://github.com/higuseonhye/research-os) |

## Boundary

This is independent personal research by Seonhye Gu. The current evidence is
controlled simulation evidence. The program does not claim clinical deployment,
hardware transfer, autonomous structural self-improvement, universal resilience,
arbitrary causal discovery, or a complete theory of intelligence.

Negative and design-stage results are kept in the record because a program gets
stronger by rejecting weak claims early.

*Updated 2026-08-05*
