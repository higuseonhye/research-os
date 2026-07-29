# Paper 002 — Confirmatory experiment spec v0.1

> **Status:** design · runnable minimum · **not frozen**  
> **Pre-reg:** [paper002_prereg_wm_expansion_v0.1.md](paper002_prereg_wm_expansion_v0.1.md)  
> **Experiment package:** [`exp_surg_003_wm_expansion`](../../experiments/surgical_intelligence/exp_surg_003_wm_expansion/README.md)

---

## Core sentence

> When a fixed dynamics model cannot explain **persistent drift failure** with parameter update alone, does adding a **drift dynamics expert** (L3 structural expansion) improve prediction and control on **novel drift conditions**?

---

## Primary RQ

> Do **persistent, structured prediction failures** justify model-class expansion — does adding a new dynamics expert outperform parameter-only repair on held-out drift prediction and behavior, without nominal regression?

---

## Hypotheses

| ID | Claim |
| --- | --- |
| **H1 — Prediction** | L3 modular expansion shows lower **held-out drift trajectory prediction error** than L1 parameter update (horizon *H*=10 · pre-specified). |
| **H2 — Behavior** | L3 shows higher **Ep2 task success** or recoverability than L1 on held-out drift. |
| **H3 — Retention** | L3 does **not** significantly degrade nominal static performance (non-inferiority · margin δ). |
| **H4 — Gate validity** | Rule-based expansion gate fires on **persistent drift** · rarely on observation noise or one-time impulse (negative controls). |

H4 is required — without it the system looks like “add expert whenever performance drops.”

---

## Environment

**Platform:** ORBIT Surgical Reach / Isaac Lab reach (`Isaac-Reach-Dual-STAR-IK-Rel-Play-v0` or documented successor).

**Task:** end-effector reaches 3D target.

**Observation** `o_t`:

```text
joint positions · joint velocities · end-effector pose · observed target pose
```

**Action** `a_t`: joint command or Cartesian delta.

**Success:** `distance(EE, target) < ε` for *N* consecutive steps.

Surgical realism is secondary to **controlled dynamics mismatch**.

### True modes (hidden from initial WM)

| Mode | Dynamics |
| --- | --- |
| **M0 static** | `x_target(t+1) = x_target(t)` |
| **M1 drift** | `x_target(t+1) = x_target(t) + v_drift Δt` after onset |

Initial agent WM assumes **M0 only** (static or noisy target observation).

### Why drift, not jump (Paper 001)

One-time target jump can be explained as observation error · one-shot disturbance · position-estimation error.

Persistent drift yields residuals that are:

```text
persistent · directionally structured · temporally correlated
```

→ parameter repair within static model class should **fail** · motivates structural inadequacy test.

---

## Agent world model

### W₀ — initial (static-only training)

```text
Encoder:   z_t = E(o_t)
Dynamics:  ẑ_{t+1} = F0(z_t, a_t)
Decoder:   ô_{t+1} = D(ẑ_{t+1})
```

**v0.1 backbone (pick one):** small MLP · **GRU dynamics (recommended)** · compact RSSM · deterministic latent transition.

No Dreamer-scale or video diffusion required for v0.1.

### W₁ — after L3 modular expansion

```text
z_t = E(o_t)
p(m_t | history) = G(z≤t, residual≤t)
ẑ_{t+1} = Σ_m p(m_t=m) F_m(z_t, a_t)
```

| Module | Role |
| --- | --- |
| **F0** | static dynamics expert (pretrained) |
| **F1** | drift dynamics expert (**new**) |
| **G** | mode gate (**new**) |

L3 adds **F1 + G**, not a single latent scalar.

### Controller (required for behavior chain)

**Recommended: MPC / model-based trajectory selection** — world-model rollouts drive action choice.

```text
candidate actions → WM rollout → predicted EE/target trajectory → cost J → select a_t

J = distance-to-target + control cost + safety cost + uncertainty penalty
```

Fixed policy + replan signal (Paper 001 menu) is **deferred** — avoids response-menu framing.

---

## Arms

| Arm | Label | Intervention |
| --- | --- | --- |
| **A** | No update | `W_after = W0` |
| **B** | Parameter update (L1) | Fine-tune `θ0 → θ0'` on F0 only · architecture unchanged |
| **C** | Modular expansion (L3) | Add F1 + G · F0 frozen or low LR |
| **D** | Oracle (optional) | `m_t = true target mode` · **upper bound / pipeline diagnostic only** |

**Primary contrast:** **C vs B**.

All arms share: same Ep1 evidence · same **data budget** · matched update data volume. Compute / param count reported separately if not equal.

---

## Protocol phases

```text
Phase 0  Pretrain on M0 static only (no drift exposure)
Phase 1  Ep1 — failure exposure (drift condition)
Phase 2  K × L1 repair attempts on held-out Ep1 window
Phase 3  Expansion gate (rule-based · pre-registered)
Phase 4  Arm-specific intervention (A / B / C / D)
Phase 5  Ep2 — novel related drift (≠ Ep1 trajectory)
Phase 6  Nominal static retention evaluation
```

### Phase 0 — Pretraining

- Train: static targets only  
- Val: held-out static positions  
- **No drift data**  
- Stop: static success ≥ preset · prediction error stable · seed variance checked  

### Phase 1 — Ep1 failure exposure

Example drift instance:

```text
onset: step 20 · direction: +x · speed: 0.01 m/s · duration: 30 steps
```

Log: observations · actions · latents · 1-step & multi-step predictions · residuals · uncertainty · controller response · success · recoverability trajectory.

All arms use **identical Ep1 trajectory / evidence budget** before intervention split.

### Phase 2 — Repair attempts

```text
for k in 1...K:
    update F0 parameters
    evaluate on held-out Ep1-like window
```

Residual structurally persistent → expansion candidate.

### Phase 3 — Expansion gate (rule-based)

```text
Gate = 1 iff ALL:

  mean(residual_after_repair) > τ_error
  K repair attempts failed
  residual_autocorrelation > τ_a
  ΔNLL = NLL(F0_repaired) - NLL(F1_candidate) > τ_nll   [held-out Ep1 slice]
```

Pre-registered thresholds · tuned on **pilot seeds only** · never on confirmatory seeds.

### Phase 5 — Ep2 novelty

Must differ from Ep1 on ≥2 of: initial target position · drift direction · drift speed · drift onset · robot initial joints.

Same structural regime: **M1 drift**.

| Factor | Ep1 example | Ep2 example |
| --- | --- | --- |
| direction | +x | +y or diagonal |
| speed | 1.0 cm/s | 0.7 or 1.3 cm/s |
| onset | step 20 | step 12 or 28 |
| start pose | set A | held-out set B |
| target region | A | B |

### Phase 6 — Static retention

All arms on held-out **M0 static** · question: did drift adaptation break nominal world?

---

## Data splits

```text
Train-static
Ep1-adaptation
Ep2-held-out-drift
Static-retention
Gate-negative-controls
```

### Gate negative controls (H4)

| ID | Condition | Expected gate rate |
| --- | --- | --- |
| **N1** | Observation noise ↑ · dynamics static | Low |
| **N2** | Single target impulse then stop | Low or medium |
| Nominal static | M0 | Very low |
| Persistent drift | M1 | High |

---

## Outcomes

### Primary (confirmatory · pre-fix one or two)

| ID | Metric | Spec |
| --- | --- | --- |
| **O1** | Held-out drift **multi-step prediction error** | `PE_H = (1/H) Σ_h ||x_{t+h} - x̂_{t+h}||²` · **H=10** confirmatory · H=5,20 secondary |
| **O2** | Ep2 **task success** | target reached within T_max without safety violation |

Prediction-only improvement without behavior change **fails** the program chain.

### Secondary

Mismatch detection latency · recovery latency · min target distance · cumulative tracking error · control effort · replan count · safety violations · uncertainty calibration · gate FP/FN rate · static retention · model size · update compute · adaptation sample efficiency.

Recoverability (optional composite):

```text
R = success reward - λ1·recovery_time - λ2·control_cost - λ3·safety_violations
```

Confirmatory analysis prefers **raw O1/O2** over composite scores.

### Mechanistic (exploratory · Appendix A)

Latent logging · cluster separation · expert selection timeline · **never primary endpoint or gate trigger**.

Always pair mechanism with: “…associated with lower held-out prediction error and improved Ep2 success.”

---

## Sample size

### Engineering pilot (excluded from confirmatory)

```text
3 arms × 5 seeds × 10 Ep2 conditions
```

Goals: drift strength calibration · gate sanity · metric variance · oracle upper bound · **find L1-fail / L3-succeed regime**.

### Confirmatory target

```text
3 arms × 10 seeds × 30 held-out drift conditions = 900 Ep2 episodes
```

Minimum start: `10 seeds × 20 conditions`. **Paired:** same seed + condition across arms.

---

## Statistics

**Prediction error:** mixed-effects or paired bootstrap / permutation.

```text
prediction_error ~ arm + drift_speed + drift_direction + onset + (1|seed) + (1|condition)
```

**Task success:** logistic mixed model or condition-level paired bootstrap.

**Pre-registered contrasts:**

```text
C vs B   (primary)
C vs A   (secondary)
```

**H3 retention:** one-sided **non-inferiority** · L3 static success not worse than baseline by > **δ** (e.g. 5 pp · fixed at freeze).

---

## Success criteria (minimum to support v0.1)

```text
1. L1 repair leaves structured drift residual on Ep1
2. L3 beats L1 on held-out drift prediction (O1)
3. L3 beats L1 on Ep2 behavior (O2)
4. L3 does not materially harm static performance (H3)
5. Gate does not fire indiscriminately on noise/impulse (H4)
```

### Diagnostic null patterns

| Result | Interpretation |
| --- | --- |
| L1 ≈ L3 | Drift not structurally hard enough · redesign mismatch |
| Oracle fails | Controller or task feasibility issue |
| L3 pred ↑ · behavior flat | Planner not using improved WM |
| L3 drift ↑ · static ↓ | Expert isolation / gating insufficient |

---

## Figures

| Fig | Content |
| --- | --- |
| 1 | Concept: Reality → static WM → failure → L1 vs L3 → Ep2 |
| 2 | Reality \| Belief: scene · predicted target · expert · gate · uncertainty |
| 3 | Main: prediction error · Ep2 success · static retention by arm |
| 4 | Mechanism: latent before/after · expert timeline · residual (with Fig 3) |
| Video | top · robot · predicted vs actual future · active expert · gate |

---

## Implementation order

| Step | Milestone |
| --- | --- |
| 1 | Add `target_mode · drift_velocity · drift_onset · drift_duration` to ORBIT reach config |
| 2 | Train static-only latent dynamics (GRU/RSSM-lite) |
| 3 | Wire **MPC** to WM predictions |
| 4 | Run A + B first — **if B fully solves drift, redesign regime before L3** |
| 5 | Add F1 + G (L3) |
| 6 | Negative-control conditions (N1 · N2) |
| 7 | Pilot → freeze τ_error · K · τ_a · τ_nll on pilot seeds |
| 8 | Confirmatory run on fresh seeds |

### First engineering milestone (blocking)

> In static-only W₀, **reasonable L1 parameter repair cannot explain held-out drift**, but **adding F1 explains it**.

Without this regime, structural expansion necessity cannot be tested.

---

## v0.1 summary

```text
Train:     static world only
Ep1:       persistent unseen drift → static WM fails
Gate:      can L1 explain held-out residual?
Arms:      A none · B repair F0 · C add F1+G
Ep2:       new position · direction · speed · onset
Primary:   multi-step prediction error (H=10) · task success
Safety:    static retention · gate on noise/impulse
Mechanism: latent · expert selection · residual (supporting)
```

---

## Links

| Doc | Path |
| --- | --- |
| Pre-reg | [paper002_prereg_wm_expansion_v0.1.md](paper002_prereg_wm_expansion_v0.1.md) |
| Analysis plan | [paper002_analysis_plan_v0.3.md](paper002_analysis_plan_v0.3.md) |
| Config | [`confirmatory_v0.1.yaml`](../../experiments/surgical_intelligence/exp_surg_003_wm_expansion/config/confirmatory_v0.1.yaml) |
