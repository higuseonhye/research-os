# Figure & table standards

> **Status:** adopted 2026-07-31 · applies going forward to all papers, retrofit onto Paper 002 now
> **Reference points:** [ORBIT-Surgical Fig. 1](https://arxiv.org/abs/2404.16027) (numbered simulation-task grid) · [concept-graphs.github.io](https://concept-graphs.github.io/) and other georgegu1997-linked project pages (Nerfies-template academic project page)

---

## Rule zero

**Every figure is a real capture from an actual run** — Isaac Sim viewport render, plotted data from a frozen result artifact, or a schematic of protocol/architecture explicitly labeled as a schematic. Never an AI-generated image standing in for simulation output. This repo's evidentiary value depends on that boundary; see [PUBLIC_BOUNDARY.md](PUBLIC_BOUNDARY.md).

---

## Two artifacts per paper

### 1. `docs/paperNNN/figures/README.md` (evidence index — already the convention)

Keep the existing pattern (see [paper002/figures/README.md](paper002/figures/README.md), [paper1/figures/README.md](paper1/figures/README.md)): generation command, file table, `manifest.json` with source/output hashes. Order the table itself in this sequence:

| Order | Content | Source |
| --- | --- | --- |
| 1 | **Teaser** — one real Isaac viewport frame or short GIF showing the task | viewport capture |
| 2 | **Pipeline / protocol figure** — architecture or experimental design diagram | schematic (labeled as such) |
| 3 | **Primary results figure(s)** — the headline comparison | plotted from frozen result artifact |
| 4 | **Secondary / condition-level figures** | plotted from frozen result artifact |
| 5 | **Representative trajectory / qualitative panel** — real capture, one seed called out by ID | viewport or trace capture |
| — | **Tables** | `tables/*.csv`, machine-readable, referenced by number in the manuscript |

This is the artifact of record — reproducible, hash-manifested, cited in the manuscript.

### 2. `docs/paperNNN/project_page.html` (public-facing summary — new)

A standalone, self-contained HTML page (same posture as [mismatch_lab/diff_explorer_v0.1.html](mismatch_lab/diff_explorer_v0.1.html) — plain HTML, no build step, served directly by GitHub Pages). Structure, adapted from the Nerfies-template convention:

```text
1. Title + status line (Tier label, date, "not peer-reviewed" if applicable)
2. Resource links — manuscript PDF, supplement, code, results artifact
3. One-sentence tagline
4. Central question (verbatim from the RQ doc)
5. Teaser (viewport GIF/image once captured; static plot until then)
6. Approach — pipeline figure + 2-3 sentence method summary
7. Results — headline figure(s) + primary endpoint table, narrated not just tabulated
8. Claim boundary — supported / not supported (verbatim from README "Claim Boundary")
9. Links back to full docs (RQ, description, related work, NAMING.md)
```

Do not invent results narration beyond what the linked docs already state — this page summarizes, it does not introduce new claims.

---

## Portfolio integration

`docs/index.md` (GitHub Pages landing) links each paper's `project_page.html` and, once available, shows a teaser GIF per entry — matching the georgegu1997-style thumbnail-next-to-title layout, adapted to this repo's plainer aesthetic (no framework, GFM + `jekyll-theme-minimal`).

---

## Capture status (2026-07-31)

| Paper | Real viewport capture | Project page |
| --- | --- | --- |
| Paper 001 | Partial — `capture_study1_viewport.sh` saves EE-trace JSON, plotted as schematic (`sim_panel_isaac_traces.png`), not a raw rendered frame | Not built |
| Paper 002 | Not yet — figures are matplotlib plots from frozen JSON, no viewport render | Building now from existing figures ([paper003 tracking task](paper003/README.md) N/A — see repo TaskList) |
| Paper 003 | N/A — design stage | Convention applies from RQ/method lock forward |

**Open item:** none of the existing capture scripts save an actual rendered camera frame yet — only trajectory data. Adding real viewport-to-file capture requires a GPU (VESSL/RunPod) run; see [scripts/capture_paper002_viewport.sh](../scripts/capture_paper002_viewport.sh) (prepared, not yet executed).

---

## Links

| Doc | Path |
| --- | --- |
| Public boundary (what may be shown) | [PUBLIC_BOUNDARY.md](PUBLIC_BOUNDARY.md) |
| Paper 002 figures | [paper002/figures/README.md](paper002/figures/README.md) |
| Paper 1 figures | [paper1/figures/README.md](paper1/figures/README.md) |
