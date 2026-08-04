# The SELF arm — H2's last competitor, measured

> **Case A. H2 stands.**
> Preregistered decision rule, locked before the arm was implemented:
> [`paper003_self_arm_prereg_v1.0.md`](../../../../../docs/paper003/paper003_self_arm_prereg_v1.0.md).
> CPU, injected coupling. Excluded from confirmatory evidence as a *physical*
> claim; the arm comparison it settles is not physical.

## The question

H2 requires `relation > parameter repair > the target's own trajectory`. The
third term had never been measured here, and it is the term that already killed
one design — **carriage** was rejected within an hour of being recommended
because a single-entity model matched the relational arm exactly.

Capture was chosen over carriage on the argument that a still target has no
history to learn from before the arrival. Arm D then turned out to be unable to
act before commit offset **+4**, so every scored cell sits four or more steps
*into* the carry — which is where the target's own trajectory has begun to
carry the carrier's pattern. Whether the argument survives that is what this
run asks.

## Result

200 paired cells, drawn from 623 seeds. `capture` coupling, `burst` schedule,
one body, commit offset in [+4, +6].

| Arm | Success | Acted |
| --- | ---: | ---: |
| A — initial position | 0.000 | — |
| B — parameter repair | 0.000 | — |
| C — mode operator | 0.025 | — |
| **SELF — own trajectory** | **0.000** | 0.675 |
| **D — relation** | **0.650** | 0.795 |

| Decision rule | | |
| --- | --- | :---: |
| Discordant pairs | D only **130**, SELF only **0** | |
| Superiority, one-sided exact McNemar | p = 7.3 × 10⁻⁴⁰ (α = 0.05) | **PASS** |
| Margin | +0.650 (≥ 0.15) | **PASS** |

**Case A. H2 stands.** Not one of the 200 cells had SELF land where D did not.

## The competitor was working, and lost for the predicted reason

A competitor that acts on two-thirds of cells and never once lands invites the
suspicion that it is broken, and a headline result resting on a broken
competitor would be worse than no result. It is not broken.

| Arm | Median miss | p10 | p90 |
| --- | ---: | ---: | ---: |
| B | 45.0 mm | 30.0 | 75.0 |
| C | 60.0 mm | 45.0 | 75.0 |
| SELF | 45.0 mm | 30.0 | 75.0 |
| **D** | **15.0 mm** | **0.0** | 75.0 |

Against a 20 mm tolerance, arm D's median miss is inside it and its 10th
percentile is exact.

The mechanism is the one the design predicted:

- **SELF has a median of 4 steps of its own motion at commitment**, range 1 to 6.
  The burst cycle is 10 on, 4 off — period 14. It has seen less than a third of
  one cycle and cannot place itself in the phase.
- **Acting makes it worse.** Median miss 60.0 mm on the 135 cells where it
  identified a pattern, against 30.0 mm on the 65 where it declined and fell
  back to arm B. 60 mm is 4 steps at 15 mm/step — exactly one pause. It
  extrapolates straight through a pause it has no way to see coming.
- **Arm D reads the carrier**, which has been moving since before the capture:
  median commit step 16, more than a full cycle. That is the information the
  relation supplies and the target's own history does not.

This is the strongest form Case A could take. SELF is not failing because it was
weakened — it is ungated, by preregistered design, while arm D must pass the
relation gate — it is failing because what it can observe is structurally
insufficient.

## Stated limitation

SELF's disadvantage rests on how little of its own history it has at
commitment, and that is a consequence of the commit window running to +6. A
window extending far enough for the target to complete a burst cycle would
eventually let SELF identify the pattern from its own trajectory, and that is
the carriage failure mode returning.

**So H2 holds in the regime the design operates in, and the protection is
bounded in time rather than absolute.** The bound is not tunable in either
direction: the window is fixed on the structure of the action and the offset
band on where arm D can act, both before this run.

Measuring where the bound lies is a separate question, on fresh seeds, and is
not answered here — the preregistration forbids extending this run's band after
seeing its result, and that clause is doing its job rather than being an
inconvenience.

## Provenance

- `scripts/paper003_self_arm.py`, which implements the locked rule and has no
  flag to relax any part of it
- Arm defined in `CommitmentEpisode._project_self`; pinned by
  `test_paper003_commitment_episode.py::SelfArmTests`, whose fixtures are
  synthetic and deliberately exclude the population above
- 232 tests pass, all CPU
