# Embodied AI Evaluation Landscape 2024–2026 (v0.1)

> **Superseded by:** [`evaluation_landscape_2024_2026_v0.2.md`](evaluation_landscape_2024_2026_v0.2.md) (+ ReSYNC cluster · paradigm map)  
> **Status:** desk synthesis · **not** a full survey · PDF spot-check only  
> **Purpose:** validate whether a **decision-layer evaluation protocol** (continue / reobserve / retry / replan / stop / ask human) is genuinely open  
> **Date:** 2026-07-22

---

## One-sentence verdict

Most recent failure/recovery work evaluates **detection → recovery action** or **task success after a monitor**; almost none standardize **same-state, multi-mode response selection** with **safety-of-decision metrics** — but **partial overlaps exist** (binary handover, HRI recovery preference, hazard HITL), so the claim must be **narrow and protocol-specific**, not “empty field.”

---

## Master comparison table (8 failure/eval papers + our scaffold)

> **v0.1 note:** RoboFAC and ResponsibleRobotBench were first listed under “Adjacent work” only — that was a **scope mistake**. They belong in the main table because both are **benchmark + evaluation protocol** papers and directly overlap our wedge (correction vs HITL vs safety metrics).

| Paper | Venue / year | Core question | Environment · data | Failure / deviation source | Model output evaluated | Baselines (typical) | Primary metrics | Ablations (typical) | Decision menu? | Safety-of-decision metrics? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Guardian** [2512.01946](https://arxiv.org/abs/2512.01946) | CoRL WS 2025 · arXiv | Did the robot fail? Planning vs execution? Why? | RLBench · BridgeDataV2 · UR5-Fail · OOD RoboFail | Perturb success traj → planning + execution failures | Binary detection · multi-class category · CoT reasoning | InternVL · Qwen3-VL · GPT-4.1 · AHA · Sentinel · MLP-CLIP | Detection accuracy (ID/OOD) · category confusion · **downstream task success** w/ 3D-LOTUS++ monitor | Data mix · view count · CoT · training size | **No** — detect then replan/re-execute in pipeline demo | **No** — no unsafe-continue / premature-stop rates |
| **Dream2Fix** [2603.13528](https://arxiv.org/abs/2603.13528) | arXiv 2026 | Can VLM predict **executable recovery** from counterfactual failures? | Real demos · generative world model (Ctrl-World) · 120k+ paired samples | Action perturbation in world model → verified failure video | Success/fail · failure type · **trajectory-level correction** | Gemini-3-Flash · prior analyzers · OpenVLA stack | Correction accuracy (19.7→81.3%) · **closed-loop recovery rate** (~46%) · zero-shot on OpenVLA failures | Verification filter · schema ablations | **No** — assumes recovery is appropriate | **No** |
| **FailSafe** [2510.01642](https://arxiv.org/abs/2510.01642) | arXiv 2025 | Can VLM **detect + emit recovery Δpose** for VLA failures? | ManiSkill · Franka (+ xArm cross-embodiment) | Simulator pose deviation + sanity-checked recovery | Failure yes/no · failure type · **executable recovery action** | Qwen2.5-VL · Gemini · GPT-4o · π₀-FAST · OpenVLA · OpenVLA-OFT | Binary success · type accuracy · action cosine sim · **VLA task success w/ monitor** (+22.6% avg) | Camera view · embodiment · w/o FailSafe-VLM | **No** — monitor triggers recovery | **No** |
| **REPAIR-Bench** [2606.29937](https://arxiv.org/abs/2606.29937) | arXiv 2026 | How do **users** perceive failures & prefer recovery in medical HRI? | RFM-HRI · 41 participants · 214 trials · crash-cart WoZ | Induced comm failures (speech/timing/comprehension/search) | Session failure · failure type · **ranked recovery strategies** | HRNN · Mistral-7B QLoRA · single-session models | Detection F1 · localization MAE (~3s) · Hit@5 / F1@5 for recovery prefs | QLoRA vs zero-shot · hierarchical vs flat | **Partial** — recovery **preference**, not manipulation mode at fixed state | **Partial** — timing error on **detection**, not unsafe autonomy |
| **RoboFailRing** [ACL 2026](https://aclanthology.org/2026.acl-long.602/) | ACL 2026 | Can retrieval make **early** failure detection + better VLM reasoning? | 6k+ failure traj · 81 sim tasks · real-world eval | Pre-built failure memory · similarity retrieval | Similarity-based fail report · grounded reasoning for cause/repair | VLM-only retrospective baselines | OOD detection success ~80% · **detection time ~50%** · reasoning accuracy +35% real | w/o memory · w/o grounding | **No** | **No** |
| **SuFIA-BC** [2504.14857](https://arxiv.org/abs/2504.14857) | ICRA 2025 | Do BC policies solve **surgical subtasks** under perception shifts? | ORBIT-Surgical digital twin · photoreal tasks | Policy rollouts · demo count · camera / object OOD | **Task success** only (needle lift, suture, retraction, …) | ACT · DP3 · multi-view / point-cloud variants | Success rate · sample efficiency · viewpoint / object generalization | Demo count · encoder · camera shift | **No** — notes missing corrective behavior qualitatively | **No** |
| **RoboFAC** [2505.12224](https://arxiv.org/abs/2505.12224) | arXiv 2025 | Can a **failure-centric VLM** diagnose failures and **correct** a running VLA? | ManiSkill (+ YCB · ReplicaCAD · AI2-THOR) · real SO-100 · **9,440 fail traj · 78k QA** | Expert-policy substage errors · teleop failures · 6-type taxonomy | 8 QA types: detect · locate · explain · **high/low correction** · task ID/plan | GPT-4o · Qwen2.5-VL · Gemini · RoboFAC-3B/7B · **No Correction** VLA | QA accuracy / LLM-judge scores · **closed-loop success** (47.5→61.25% @ 4 rounds) · latency | Low vs high correction · w/o fine-tune · correction round ablation | **No** — always “correct” when paused; no continue/stop menu | **No** — success uplift only |
| **ResponsibleRobotBench** [2512.04308](https://arxiv.org/abs/2512.04308) | arXiv 2025 | Can LMM agents manipulate **safely under hazards** and know when to **call human**? | Physics sim · **23 multi-stage tasks** · 100 fixed layouts · elec / fire-chem / human hazards | Hazard scenarios · adversarial vs defense prompts · UNS vs COS task types | Hazard prediction · safety-aware plan · skills / poses / code actions · **`call_human_help`** | GPT-4o · GPT-4o-mini · Qwen 7B/72B · InternVL · action-repr ablations | **Success · safety rate · safe success rate (SSR)** · hazard detection · **cost** · fine-grained error taxonomy | HITL vs autonomous · w/o history · N-shot · action representation · attack/defense prompts | **Partial** — human help is **one skill**, not multi-mode @ fixed state | **Partial** — SSR + hazard metrics; not unsafe-continue @ manipulation deviation |
| **001A–D (ours · smoke)** | research-os | At fixed mismatch **S**, how do **response × timing** affect resolution? | ORBIT Isaac reach · scripted IK-Rel | Controlled shift / occlusion @ fixed onset | **Intervention choice** + delay → terminal judge | CONTINUE · REPLAN · REOBSERVE · RESHAPE · HANDOVER(log) | Profile \( \hat{R}_a(s,t) \) · mode separation · (Phase C) n=20 | Delay · occlusion · mode ablations | **Yes** — core object | **Planned** — unsafe continue / premature stop / escalation errors in Phase C+ |

---

## What the field mostly evaluates (2024–2026 failure line)

| Layer | Common? | Typical metrics |
| --- | --- | --- |
| Task success | ✅ universal | Success rate · episodes |
| Failure detection | ✅ very common | Accuracy · F1 · category accuracy |
| Failure explanation | ✅ common | VQA scores · human/LLM judge |
| Recovery generation | ✅ rising fast | Recovery success · correction accuracy · VLA uplift |
| Detection **timing** | ⚠️ some | RoboFailRing latency · REPAIR localization error |
| **Response selection** (multi-mode menu at fixed state) | ❌ rare as benchmark | — |
| **Safety of decision** (unsafe continue, wrong escalation, missed handoff) | ❌ almost absent in manipulation | Surgical UQ: partial (binary) |

---

## Adjacent work (Tier 1 + others · kill-test relevant)

| Line | arXiv / venue | Overlap with our wedge | Gap vs us |
| --- | --- | --- | --- |
| **Surgical UQ** | [2501.10561](https://arxiv.org/abs/2501.10561) | Continue vs **handover** under uncertainty | Binary · not multi-mode @ same state |
| **CMFR (REALM)** | ACL 2025 workshop | Multi-stage replan on TEACH | Plan repair · not standardized decision taxonomy |
| **Recovery RL / RTA** | classic + When-to-act [2605.12561](https://arxiv.org/abs/2605.12561) | Backup / timing / safety shield | Control-theoretic · not VLM decision menu eval |
| **ERR@HRI** | 2024–2025 challenges | Multimodal **interaction** failure detection | Social HRI errors · not manipulation recovery choice |

**Kill-test result (v0.1):** **0 Kill** on “evaluation protocol for multi-mode response @ same onset” — refine positioning; do **not** claim nobody studies failure or handover.

---

## Honest novelty boundary (what we can claim today)

### Strong (defensible after Phase C)

1. **Same-state counterfactual protocol** — fair comparison of intervention modes at mismatch onset (001A scaffold).
2. **Intervention-conditioned recoverability profiles** \( R_a(s,t) \) — empirical, not a learned estimator claim.
3. **Surgical reach proxy** with occlusion / reshape / reobserve modes — extends BC-benchmark lines (SuFIA) toward **decision evaluation**, not policy SOTA.

### Weak (do not lead with)

- “First to study robot failure” — false.
- “First LLM recovery” — Dream2Fix / FailSafe / RoboFAC.
- “First human handoff” — Surgical UQ · REPAIR-Bench · ResponsibleRobotBench.
- “First timing” — RoboFailRing · REPAIR localization · When-to-act (different setting).

### Our actual wedge (one paragraph)

> Prior failure benchmarks ask **whether** failure occurred and **what recovery action** to execute. We ask: **given a detected non-nominal state S, which response class** (continue, reobserve, retry/replan, reshape, stop, handover) **maximizes successful resolution — and at what cost in unsafe continuation, premature stop, and escalation error?** We evaluate this via **same-state counterfactual replay**, not by training a new VLA.

---

## Metric gap table (your surgical-style metrics)

| Metric | Guardian | Dream2Fix | FailSafe | REPAIR | RoboFailRing | SuFIA-BC | RoboFAC | RespRobotBench | **001 (target)** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Task / recovery success | ✅ pipeline | ✅ | ✅ VLA uplift | ❌ (prefs) | ❌ | ✅ task only | ✅ w/ critic | ✅ SSR | ✅ resolution |
| Detection accuracy | ✅ | ✅ (in schema) | ✅ | ✅ | ✅ | ❌ | ✅ QA | ✅ hazard | Optional add-on |
| Recovery action quality | ❌ | ✅ | ✅ | ✅ prefs | explain only | ❌ | ✅ hi/lo correct | ❌ (plan/skill) | Secondary |
| **Response selection accuracy** | ❌ | ❌ | ❌ | partial | ❌ | ❌ | ❌ | partial | **Primary (Phase C+)** |
| Unsafe continuation rate | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | partial (safety rate) | **Primary** |
| Premature stop | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | partial (over-refusal) | **Primary** |
| Wrong / missed escalation | ❌ | ❌ | ❌ | partial | ❌ | ❌ | ❌ | partial (HITL gap) | **Primary** |
| Intervention timing error | ❌ | ❌ | ❌ | ✅ detect | ✅ detect | ❌ | ❌ | ❌ | **RQ-T** |
| Same-state CF fairness | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **Core method** |

---

## Mapping: their experiment pattern → our Paper 1 design

```text
THEIR PATTERN (typical)
  success traj → inject failure → detect → generate recovery → task success

OUR PATTERN (001A–D)
  shared rollout → mismatch @ S → fork(response, delay) → terminal judge → profile table
```

| Design element | Borrow from prior art | Our twist |
| --- | --- | --- |
| Failure injection | Guardian / FailSafe perturbation · Dream2Fix counterfactual | Fixed-onset **S** for fair mode comparison |
| Baselines | Zero-shot VLM · fine-tuned monitors · VLA+monitor stacks | Rule CONTINUE · REPLAN · (+ stretch) Surgical UQ binary |
| Metrics | Detection acc · recovery success · pipeline uplift | **Profile metrics** + decision confusion + safety errors |
| Data scale | 10k–120k failure pairs | Start **20–50 scripted scenarios** · n=20 confirmatory |
| Human | REPAIR preference labels | HANDOVER stub → Stage 2 collaboration log |

---

## University vs industry (why both care)

| Audience | What they hear | Why evaluation protocol fits |
| --- | --- | --- |
| **University lab** | New benchmark · dataset · metrics · reproducible test suite | NeurIPS/ICML D&B · CoRL · RSS · ICRA — benchmark papers are first-class |
| **Industry (surgical / physical AI)** | Regression testing · escalation policy · incident reduction · deployment gate | Intuitive / PI / Figure need **when to call the human**, not another VLA leaderboard |

**Entry strategy:** publish **protocol + profiles + open scenarios** first; offer industry **validation harness** language second.

---

## Next desk actions (this week)

1. **PDF spot-check** Tier 1 Surgical UQ + VAP-TAMP against § “Adjacent work”.
2. **PDF spot-check** RoboFAC + ResponsibleRobotBench (rows added v0.1 · desk-level only).
3. Freeze **exception–response taxonomy v0.1** aligned with 001D modes.
4. Draft **ground-truth label rules** per scenario (which mode is “correct” @ S).
5. Phase C: primary endpoint = **profile separation**; stretch = **decision confusion vs UQ binary**.

---

## References (quick links)

| Paper | Link |
| --- | --- |
| Guardian | https://arxiv.org/abs/2512.01946 |
| Dream2Fix | https://arxiv.org/abs/2603.13528 |
| FailSafe | https://arxiv.org/abs/2510.01642 |
| REPAIR-Bench | https://arxiv.org/abs/2606.29937 |
| RFM-HRI (REPAIR data) | https://arxiv.org/abs/2603.05641 |
| RoboFailRing | https://aclanthology.org/2026.acl-long.602/ |
| SuFIA-BC | https://arxiv.org/abs/2504.14857 |
| RoboFAC | https://arxiv.org/abs/2505.12224 |
| ResponsibleRobotBench | https://arxiv.org/abs/2512.04308 |
| Our RQ v1.0 | [`research_question.md`](research_question.md) |
| Lit positioning | [`lit_positioning_v1.md`](lit_positioning_v1.md) |
