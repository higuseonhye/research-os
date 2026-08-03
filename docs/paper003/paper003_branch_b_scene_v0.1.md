# Paper 003 — the Branch B scene, and a wrong turn it corrects

> **Finding, 2026-08-04, on A100-SXM4-80GB.** Supersedes the Branch B reasoning
> in [the probe sweep record](../../experiments/surgical_intelligence/exp_surg_004_relation_expansion/results/isaac_probe_sweep_v0.2/RESULTS.md)
> and the tolerance argument in [the two-body note](paper003_two_body_encounter_v0.1.md).

## The scene exists already

`Isaac-Lift-Block-PSM-IK-Rel-Play-v0`:

```
articulations:  ['robot']
rigid_objects:  ['object']          <- the reach task reports []
sensors:        ['ee_frame']
commands:       ['object_pose']
object root_pos_w = [-0.0186, -0.0162, 0.025]
```

Sixteen Lift tasks register, across a block and a needle. The command is
**`object_pose`** — the goal pose of the *object*, not of the end effector. So
the target is a physical rigid body whose position is read from the simulator
rather than a point written into a command, which is exactly what deliverable 2
has been asking for.

## What "incompatible" turned out to mean

The bootstrap script deleted the `lift` and `handover` task folders, labelled
"incompatible non-Reach task folders", with no record of why. Every scene
inventory since has therefore come back with `rigid_objects: []`, and the
conclusion drawn from that — **recorded this morning** — was that real contact
required adding a rigid body to the reach scene by hand, forking the task
family.

The actual incompatibility is **two lines**:

```python
object_pose.goal_pose_visualizer_cfg.markers["frame"].scale = (0.01, 0.01, 0.01)
object_pose.current_pose_visualizer_cfg.markers["frame"].scale = (0.01, 0.01, 0.01)
```

`UniformPoseCommandCfg` lost those attributes in Isaac Lab v1.0.0. They set a
**debug visualisation marker's scale**. Nothing else in the task touches them —
not the dynamics, not the rewards, not the termination criterion. But
`import_packages` walks the whole task tree, so one `AttributeError` aborts the
entire registration, and deleting the folders made Reach import again.

Deleting them also deleted the answer to the question the project spent a GPU
session and a day of design reasoning on.

The bootstrap now drops those two lines instead of the folders, and keeps an
untouched copy alongside.

## The placement tolerance is settled at 20 mm

`lift/mdp/terminations.py`:

```python
threshold: float = 0.02   # "The threshold for the object to reach the goal position"
```

This matters for a reason the earlier reasoning got backwards. The two-body note
argued that a forked task family does not inherit its predecessor's tolerance,
so 20 mm was open and would have to come from the new scene. It does come from
the new scene — and it is **the same 20 mm**, set independently for object
placement in a scene that has always had objects, long before Paper 003 existed.

The object's own scale corroborates it: the block sits at `z = 0.025`, so the
tolerance is roughly the object's half-height.

**So the tolerance is not an open parameter and never was.** It is 20 mm on two
independent grounds, and choosing otherwise would be choosing a parameter by
which arm it favours.

## What that costs

The capability-crossing endpoint needs `success(B)` in a near-zero band. Under
the injected coupling one contact pass displaces the target by roughly 15 mm
against that 20 mm tolerance, and arm B lands 0.50–0.90 across every encounter,
speed and gain tried. A tolerance of 20 mm does not make the endpoint reachable
by itself.

What changes is that the displacement is no longer ours to set. Under real
contact it follows from the object's mass, the contact normal and the pushing
body's momentum — none of them free parameters, all of them measurable. Whether
a struck block moves more or less than 20 mm in six steps is now an empirical
question about the scene rather than a design choice, which is the right footing
for it.

## What the runner needs

Three names differ from the reach task, and one thing is structural:

| | Reach | Lift |
| --- | --- | --- |
| Articulation | `robot_1`, `robot_2` | `robot` |
| End-effector sensor | `ee_1_frame` | `ee_frame` |
| Command | `ee_1_pose` | `object_pose` |
| Target | a point written into the command | **a rigid body read from the scene** |

The last row is the whole point and also the work: the cell driver currently
*sets* the target each step. Against a real object it must *read* the pose and
let contact move it, which means the pushing bodies have to become real too.

## Status

| Item | State |
| --- | --- |
| Branch B scene | **found**, registers, has a rigid object |
| Placement tolerance | **settled at 20 mm**, corroborated independently |
| Bootstrap | **fixed** — patches two lines instead of deleting the tasks |
| Real-contact runner | **not started**; the target must be read, not written |
| H1 reachability | still unknown, but now an empirical question about contact |
