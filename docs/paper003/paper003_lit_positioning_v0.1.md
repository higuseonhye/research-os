# Paper 003 — Lit positioning: execution-horizon framing vs internal RQ v0.1

> **Purpose:** ground the "framing note" in [paper003_rq_v0.1.md](paper003_rq_v0.1.md) with actual papers, so the lab-intro framing and the internal RQ can be told apart on paper, not just in conversation.
> **As of:** 2026-07-31 — these are recent preprints, positioning may need a refresh before submission.

---

## What the "execution horizon" literature actually studies

| Paper | Authors | What it does |
| --- | --- | --- |
| [Dynamic Execution Horizon Prediction for Chunk-based Robot Policies (DEHP)](https://arxiv.org/abs/2606.11408) | Zhao, Bogdanovic, Sohal, Tao, Darvish, Aspuru-Guzik, **Shkurti, Garg** | Learns how many actions of a **frozen** chunk policy to execute before requerying — trains a lightweight horizon head via online RL on top of a pretrained, unchanged policy |
| [PACE: Phase-Aware Chunk Execution for Robot Policies with Action Chunking](https://arxiv.org/pdf/2606.00537) | — | Adapts horizon per manipulation phase; discards unexecuted chunk suffix before replanning |
| [Spatial Attention: Adapting Execution Horizons for Diffusion Policies via Observation Sensitivity](https://arxiv.org/pdf/2607.04739) | — | Horizon adaptation driven by observation sensitivity, still within a fixed diffusion policy |
| [Deployment-Time Reliability of Learned Robot Policies](https://arxiv.org/pdf/2603.11400) | Garg-affiliated | Closest to "model adequacy" language, but at deployment-time monitoring level, not structural revision |

**Common thread:** all of these hold the **policy / model class fixed** and ask *how often should it be re-queried, and how far can it be trusted open-loop before the next observation?* This is an **L1-adjacent** question (correction frequency within a fixed representation) — not an **L3** question (whether the representation itself needs to change).

---

## Where Paper 003 differs

Paper 003's RQ sits one level up: not *"how often to replan"* but *"when repair within the current model class is insufficient, does changing the model class (adding a relation) unlock tasks that no amount of replanning frequency could reach?"*

A chunk policy that requeries every single step is still bounded by what its representation **can express**. Paper 003 tests whether the binding constraint is representation adequacy, not query frequency — the axis these execution-horizon papers don't touch.

```text
Execution-horizon literature:  WHEN to re-query a fixed model      (frequency)
Paper 002 / 003:               WHETHER the model class itself      (structure)
                                needs to change, and whether that
                                unlocks tasks frequency cannot reach
```

---

## Not claiming

- Not a critique of execution-horizon work — it is an **orthogonal, complementary axis** (frequency vs structure), not a competing or superseded approach.
- Not claiming DEHP/PACE/Spatial-Attention are wrong, or that Paper 002/003 makes them unnecessary — a system could need both adaptive horizons *and* structural revision.

---

## Open item

- [ ] Re-check this list closer to submission — execution-horizon work is moving fast (3 of 4 papers above are from the last two months as of this writing).

---

## Links

| Doc | Path |
| --- | --- |
| RQ (framing note references this doc) | [paper003_rq_v0.1.md](paper003_rq_v0.1.md) |
| Method draft | [paper003_description_v0.1.md](paper003_description_v0.1.md) |
