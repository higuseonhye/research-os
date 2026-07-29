# Paper 002 — Physical validation roadmap v0.1 (DRAFT)

> **Status:** design · **not promoted to experiments/** until sim Go gates pass  
> **Sim first:** EXP-SURG-003 (Isaac/mock) · [confirmatory spec](paper002_confirmatory_spec_v0.1.md)  
> **Physical (deferred):** EXP-REAL-001 · private protocol until freeze

---

## Purpose

Validate whether **failure-conditioned model adequacy** and **repair vs structural expansion** (Paper 002 mechanism) merit **low-cost physical replication** — not to claim clinical or industrial deployment.

**Working name:** Physical Testbed for Failure-Driven World-Model Reconstruction

**Not:** “Open Recoverability Robot” (Paper 001 credential · not program center)

---

## Sim before hardware (2026-07 decision)

| Phase | Share | Action |
| --- | --- | --- |
| **Simulation** | ~80% | EXP-SURG-003 mock + Isaac · Go gates below |
| **Hardware prep** | ~20% | Schema · adapter stub · BOM research (private) |
| **Purchase** | **Hold** | SO-101 follower until **all Go gates** pass |

Buying hardware before **L1 fail · L3 win on held-out drift** risks debugging servos instead of model adequacy.

**Next sim deliverable:** five priority experiments (strong repair · parameter control · missing mode · noise gate · compositional Ep2) — see private Go gates doc.

---

## Program center (unchanged)

> When the current **model class** cannot explain **persistent failure**, does **prepared structural expansion** beat **parameter repair** on **novel related** conditions — without nominal regression?

Recoverability = **measurement window** on Ep2 · not the program title.

---

## Planned physical cell (private detail)

**Candidate platform:** SO-101 follower arm (LeRobot ecosystem) — low-cost, reproducible, **not** final clinical evidence.

**First task (draft):** planar **push** (preferred over grasp) · controlled friction / mass perturbations · same A/B/C arms as sim.

**Full protocol:** private [exp_real_001_protocol](https://github.com/higuseonhye/builder-os-private/blob/master/working/research/paper002/exp_real_001_protocol.md) · public after freeze.

---

## Go / No-Go gates (hardware purchase)

Purchase **only if** sim pilot + confirmatory show:

| Gate | Criterion (initial · tune at pre-reg) |
| --- | --- |
| **G1 Mechanism** | C > B on Ep2 success · **≥15–20 pp** · multi-step prediction **≥15%** lower · static retention **≤5 pp** drop |
| **G2 Robustness** | Holds across ≥2 of: direction · onset · pose · drift magnitude |
| **G3 Identifiability** | Oracle separates expert vs gate vs observation limits |
| **G4 Physical contract** | Runs on **joint pose · commanded action · EE pose · RGB object pose** only (no privileged physics in claim path) |
| **G5 Gate validity** | False expansion on noise/impulse **≤10%** |

**No-Go →** revise perturbation taxonomy · repair baseline · or task — **do not buy robot**.

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
Sim (Paper 002 v0.1)     mechanism · adequacy test · L1 vs L3
        ↓ Go gates
SO-101 (EXP-REAL-001)    mechanism survives sensor noise · backlash · contact
        ↓ selective
Precision arm / lab      partial reproduction · not artifact of cheap servos
        ↓ later
Task-relevant / clinical NOT claimed from SO-101 alone
```

---

## Public promotion rule

| Tier | Location |
| --- | --- |
| Frozen protocol + results | `research-os/experiments/physical_world_model/` (future) |
| BOM · purchase · assembly | **private** `working/hardware/so101/` |
| Thinking · daily | **vault** |

---

## Links

- [Confirmatory spec](paper002_confirmatory_spec_v0.1.md)
- [VESSL runbook](vessl_runbook_v0.1.md)
- [EXP-SURG-003](https://github.com/higuseonhye/research-os/tree/master/experiments/surgical_intelligence/exp_surg_003_wm_expansion)
