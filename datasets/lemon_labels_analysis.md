# LEMON labels.json Analysis

> EXP-SPIKE-LEMON-001 · Source: [visurg-ai/LEMON labels.json](https://github.com/visurg-ai/LEMON/blob/main/labels.json) · 2026-07-10

## Schema

Each record has 7 fields:

| Field | Type | Example | Surg-Data Lake mapping |
| --- | --- | --- | --- |
| `youtubeId` | string | `80czDESoMiQ` | `asset_id` → `lemon:video:{youtubeId}` |
| `md5` | string | `bfcb3fb8...` | YouTube-source hash (HF curated mp4 differs) |
| `procedureName` | string[] | `["splenectomy", "pancreatectomy"]` | `procedure_tags[]` (multi-label) |
| `robotic` | bool | `false` | `robotic_context.is_robotic_assisted` |
| `title` | string | procedure description | `metadata.title` |
| `resolution` | `[w, h]` | `[1280, 720]` | YouTube meta; use ffprobe on HF files |
| `informative` | bool | `true` | filter flag (all 4194 are informative) |

HF filenames follow `{youtubeId}.mp4` — direct join key between labels and repo files.

## Catalog Statistics

| Metric | Value |
| --- | --- |
| Total videos | **4,194** |
| HF repo files (metadata smoke) | 4,196 (+2 non-label assets) |
| Robotic-assisted | 1,667 (39.8%) |
| Non-robotic (laparoscopic) | 2,527 (60.2%) |
| Unique procedure tags | **35** |
| Multi-label videos | 266 (6.3%) |
| Duplicate youtubeId / md5 | 0 |

Full counts: [`metadata/lemon_labels_summary.json`](metadata/lemon_labels_summary.json)

## Procedure Distribution (top 10)

| Procedure | Total | Robotic |
| --- | ---: | ---: |
| colectomy | 308 | 130 |
| hernia_repair | 295 | 196 |
| appendectomy | 252 | 32 |
| thymectomy | 236 | 102 |
| cholecystectomy | 229 | 52 |
| adhesiolysis | 196 | 40 |
| low_anterior_resection | 190 | 84 |
| nephrectomy | 189 | 98 |
| esophagectomy | 174 | 94 |
| nissen_fundoplication | 170 | 62 |

Rare tags: `vaginectomy` (7), `cecectomy` (2).

## Resolution

| Resolution | Count | Share |
| --- | ---: | ---: |
| 1280×720 | 3,960 | 94.4% |
| 960×720 | 123 | 2.9% |
| Other | 111 | 2.7% |

## Implications for SRI Program

### RQ1 (perception / representation)

- LEMON is **multi-label procedure classification** + **robotic vs laparoscopic** — good for LemonFM-style pretraining and domain adaptation probes.
- 35 procedure types cover abdominal, thoracic, and urologic cases — broader than ORBIT Reach (embodied subset).

### RQ2+ (action / embodied)

- **No action labels** — video-only; complements ORBIT/dVRK, does not replace SIB embodied benchmarks.
- Robotic subset (1,667) is the best bridge to **da Vinci**-style platforms if we later add phase/tool annotations.

### Subset strategy (recommended)

| Use case | Filter | Approx. size |
| --- | --- | --- |
| LemonFM smoke | 5 robotic + 5 lap, diverse procedures | 10 (manifest v0) |
| Robotic pretrain slice | `robotic == true` | 1,667 |
| Procedure-balanced eval | stratified sample per procedure tag | 35–70 |
| Full catalog | all informative | 4,194 |

## Surg-Data Lake Registration

First 10-asset manifest (metadata only, no blobs in git):

- [`manifests/lemon_v0.yaml`](../manifests/lemon_v0.yaml)
- Regenerate: `python scripts/build_lemon_manifest.py`

Selection policy: 5 robotic + 5 laparoscopic, diverse `procedure_tags`, HF URI on demand.

## Subset Validation (2026-07-10)

RunPod download + ffprobe + local playback confirmed for manifest v0 (10 clips). See [`experiments/phase2_spikes/lemon_subset_run_log.md`](../experiments/phase2_spikes/lemon_subset_run_log.md).

## Next

- [x] Download manifest subset on RunPod (`hf download`, 10 clips)
- [ ] LemonFM inference smoke on `pfTqwcFbTIU.mp4`
- [ ] Expand manifest to procedure-stratified eval set (35 clips)
