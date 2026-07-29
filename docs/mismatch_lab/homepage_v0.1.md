# Mismatch Lab — Homepage v0.1

> Copy for public landing · GitHub Pages or standalone site

---

## Hero

**Headline**

> What changed between these two robot runs?

**Subhead**

> Mismatch Lab helps teams understand robot behavior — and spot when a difference means the model no longer fits reality.

**Primary CTA:** Try Robot Diff  
**Secondary CTAs:** Explore cases · Run the benchmark · Read the research

---

## Above the fold demo (embedded)

Preloaded case: **Persistent target drift**

```text
Run A (baseline policy)     Run B (after drift onset)
         ↓                              ↓
    Prediction track              Observation track
         ↓                              ↓
    Difference grows at t=8 … t=35
         ↓
    Repair ×3 did not absorb error
         ↓
    Adequacy hint: consider structural review
```

User does not read a paper to understand the problem.

---

## Product strip (four verbs)

| Verb | One line |
| --- | --- |
| **Replay** | Watch robot rollouts like video — with prediction overlay |
| **Diff** | Compare two runs; auto-find behavior shifts and divergence |
| **Explain** | Timeline of interesting moments and what the model expected |
| **Discover** | Search thousands of rollouts for episodes worth inspecting |

Fine print (tooltip): Adequacy insights appear when differences persist after recovery attempts.

---

## Upload strip (pilot)

**Headline:** Upload a rollout. Get a diff report.

If upload not ready:

> **Join the pilot** — early access to Model Adequacy SDK and batch diff on your logs.

Form fields: name · email · org · stack (Isaac / custom / sim-only) · use case

---

## Four explorer cases (cards)

| Case | User question | Adequacy? |
| --- | --- | --- |
| **Policy A vs B** | What changed after my ablation? | No |
| **Sim vs real** | Where does sim diverge from hardware? | Maybe |
| **Repair plateau** | Why didn't retuning help? | Yes |
| **Drift vs noise** | Is this sensor noise or real dynamics change? | Yes |

Each card opens interactive Diff viewer with timeline slider.

---

## Research strip

**Headline:** Built on open research

- Paper 001 — recoverability at fixed mismatch
- Paper 002 — failure-conditioned model adequacy (EXP-SURG-003)
- Preliminary mock pilot · confirmatory sim next

Links: Research OS · prereg · benchmark spec

---

## Vision strip (footer, short)

> Long term: physical AI that keeps learning when reality breaks its assumptions.

Not the hero. One paragraph max.

---

## SEO / social

**Title:** Mismatch Lab — Robot Diff & Model Adequacy  
**Description:** Compare robot rollouts, explain behavior shifts, and detect when your world model needs more than retuning.  
**OG image:** Side-by-side diff timeline screenshot

---

## Navigation

```text
Diff Explorer | Benchmark | Research | API Docs | Join Pilot
```

---

*Updated 2026-07-29*
