# Paper 002 figures

All panels and CSV tables are generated directly from the frozen confirmatory JSON artifacts.

```bash
python scripts/plot_paper002_model_order.py
```

| File | Content |
| --- | --- |
| `fig1_confirmatory_protocol.png` | Preregistered protocol and arms |
| `fig2_confirmatory_outcomes.png` | Arm-level prediction, control, and success outcomes |
| `fig3_condition_effects.png` | C-minus-B effects across all ten fresh conditions |
| `fig4_representative_trajectory.png` | Process-isolated seed 300/C04 trajectory |
| `fig5_gate_and_retention.png` | H3 retention and H4 gate controls |
| `tables/*.csv` | Machine-readable manuscript tables |
| `manifest.json` | Source and output SHA-256 hashes |

Every panel is plotted from the frozen confirmatory artifact. No rendered Isaac Sim viewport frame is included.
