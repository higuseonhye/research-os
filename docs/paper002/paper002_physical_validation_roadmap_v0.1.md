# Paper 002 — Physical validation roadmap v0.2 (DRAFT)

> **Status:** design · confirmatory **experiments/** promotion after sim Go gates  
> **Sim (Track A):** EXP-SURG-003 · [confirmatory spec](paper002_confirmatory_spec_v0.1.md)  
> **Physical anchor (Track B):** SO-101 · observability cell · private until freeze

---

## Purpose

Validate whether **failure-conditioned model adequacy** and **repair vs structural expansion** survive **real sensors** — not to claim clinical deployment.

**Working name:** Physical Testbed for Failure-Driven World-Model Reconstruction

**Not:** “Open Recoverability Robot” (Paper 001 credential · not program center)

---

## Research layers (program)

| Layer | Question | Primary venue |
| --- | --- | --- |
| **L1 Mechanism** | Does L3 expansion beat L1 repair when a dynamics **mode** is missing? | Simulation (EXP-SURG-003) |
| **L2 Observability** | Can inadequacy be detected **without privileged state**? | SO-101 anchor (Track B) |
| **L3 Task value** | Does expansion improve success/safety in task-relevant settings? | Precision arm · surgical-like · later |

Ultimate question is **embodied**. Paper 002 v0.1 **isolates mechanism** in L1 before L2/L3 claims.

---

## Parallel tracks (2026-07 rev.)

| Track | Share | Action |
| --- | --- | --- |
| **A — Paper 002 sim** | 70–80% | EXP-SURG-003 · Go gates · pre-reg · confirmatory |
| **B — Physical anchor** | 20–30% | SO-101 · logging · repeatability · failure-signal observability |

**Anchor purchase:** justified as **2–3 year program instrument** — not as Paper 002 confirmatory on day one.

**EXP-REAL-001 A/B/C:** runs **after** sim Go gates G1–G5 · hardware confirmatory protocol **not yet public** (promote after pre-reg freeze).

---

## Program center (unchanged)

> When the current **model class** cannot explain **persistent failure**, does **prepared structural expansion** beat **parameter repair** on **novel related** conditions — without nominal regression?

Recoverability = **measurement window** on Ep2 · not the program title.

---

## Planned physical cell (private detail)

**Candidate platform:** SO-101 follower arm (LeRobot ecosystem) — low-cost, reproducible, **not** final clinical evidence.

**First task (draft):** planar **push** (preferred over grasp) · controlled friction / mass perturbations · same A/B/C arms as sim.

**Full protocol:** EXP-REAL-001 · promote to `experiments/` after pre-reg freeze · not linked from this repo until then.

---

## Go / No-Go gates (EXP-REAL-001 confirmatory — not anchor purchase)

Run full A/B/C protocol on hardware **only if** sim pilot + confirmatory show:

| Gate | Criterion (initial · tune at pre-reg) |
| --- | --- |
| **G1 Mechanism** | C > B on Ep2 success · **≥15–20 pp** · multi-step prediction **≥15%** lower · static retention **≤5 pp** drop |
| **G2 Robustness** | Holds across ≥2 of: direction · onset · pose · drift magnitude |
| **G3 Identifiability** | Oracle separates expert vs gate vs observation limits |
| **G4 Physical contract** | Runs on **joint pose · commanded action · EE pose · RGB object pose** only (no privileged physics in claim path) |
| **G5 Gate validity** | False expansion on noise/impulse **≤10%** |

**No-Go →** revise perturbation taxonomy · repair baseline · or task — **do not** run confirmatory on hardware.

**Track B (anchor) may proceed regardless** — assembly · logging · repeatability · raw perturbation trajectories only.

---

## Sim–real contract (sketch)

```text
Paper002Environment
├── IsaacAdapter      ← EXP-SURG-003
└── SO101Adapter      ← EXP-REAL-001 (after Go)
```

Shared: world model · repair/expansion arms · gate · metrics · episode protocol  
Different: physics backend · sensors · command interface · reset

---

## Evidence ladder (honest claims)

```text
L1  Sim (Paper 002)        mechanism · L1 vs L3 · Go gates
        ↓
L2  SO-101 (Track B)       observability · sensor contract · residuals
        ↓ confirmatory after Go
L2b EXP-REAL-001           frozen A/B/C on real robot
        ↓ selective
L3  Precision / task       partial reproduction · safety · intervention
        ↓ later
    Clinical / surgical    NOT claimed from SO-101 alone
```

---

## Public promotion rule

| Tier | Location |
| --- | --- |
| Frozen protocol + results | `research-os/experiments/physical_world_model/` (future) |
| BOM · purchase · assembly | Private working records · not in research-os |
| Thinking · daily | Private vault · not in research-os |

---

## Links

- [Confirmatory spec](paper002_confirmatory_spec_v0.1.md)
- [VESSL runbook](vessl_runbook_v0.1.md)
- [EXP-SURG-003](https://github.com/higuseonhye/research-os/tree/master/experiments/surgical_intelligence/exp_surg_003_wm_expansion)
