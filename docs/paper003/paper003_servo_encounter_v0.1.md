# The encounter has to arrive before it carries

> **Design note, 2026-08-05, written before the change was measured.** Follows
> [the rendezvous note](paper003_rendezvous_v0.1.md), which argued that a grasp
> needs an arrival; this fixes what the encounter becomes once the arrival has
> to be produced by servoing rather than by a script.

## The measurement that forces it

| | |
| --- | ---: |
| capture radius, measured | **< 1 mm** |
| arm's steady-state error following a moving script | **7.3 mm** |
| separation a servo reaches, no script to chase | **0.002 mm** |

Seven-fold apart, and the 7.3 mm is the IK controller's, not the schedule's — it
was 7.5 mm at 2 mm/step and 7.7 at 2.5, and no speed removes it. **A
script-following approach cannot produce a capture in this scene.**
[The measurement](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/capture_pilot_v0.1/RESULTS.md)

## The arrival stays inside the episode

The obvious shortcut is to grasp before the episode starts, the way `--preroll`
brings the arm to the start line, and record only the carry. **That is not
available**, and the reason is the paper's rather than the simulator's.

The commit window is one dispense-length either side of the arrival. If the
arrival happens before step 0, the window has no anchor inside the episode, and
every commit sits in the riding tail — which is exactly the regime the window was
introduced to exclude, where a constant-velocity model absorbs the motion and
the single-entity arm eventually matches the relational one.

So the episode must contain: a still target, an approach, the taking hold, and
the carry. In that order, observed.

## What the encounter supplies changes

Under a script the encounter gave the body's **positions** at each step, and the
arm chased them. Under a servo it gives the **direction** instead:

```text
before the grasp   the arm goes to the object, wherever the object is
at the grasp       the gripper closes; this is the arrival
after the grasp    the arm moves along the drawn axis, on the burst schedule
```

The drawn azimuth still decides which way the carry runs, and it is still drawn
per seed, so encounters remain distinguishable from one another. What is dropped
is the pretence that the body's position was known in advance — it never was,
since the arm could not reach it.

Nothing about the *relation* changes: the target is perfectly still until a body
takes hold, and then it rides. That is what `capture_displacement` has always
said and what the physics has now been shown to do.

## The open question, and how it gets settled

`contact_arrivals` anchors the commit window on a body crossing
`interaction_radius` — 12 mm in this scene. The grasp happens under 1 mm. At
roughly 3 mm/step those are about four steps apart, so the **anchor and the
capture are not the same event**, and arm D cannot act until it has three riding
steps after the capture.

Whether that leaves a usable overlap is a measurement, not a choice. It is
recorded here in advance that the three quantities involved —
`interaction_radius`, the commit window's half-width, and `min_carriage_run` —
**are not to be adjusted against each other after seeing the result.** The window
is fixed on the structure of the action, the run on the collision equilibrium,
and the radius is a property of the scene to be measured. If they do not overlap,
that is a finding about this task, and the honest response is the same one the
onset question got: write down what the design cannot do.

What *may* change on measured grounds is the encounter — how fast the carry runs
and how long the bursts are — since those are the encounter's own parameters and
have never been fixed. Any such change is stated before the run that tests it.
