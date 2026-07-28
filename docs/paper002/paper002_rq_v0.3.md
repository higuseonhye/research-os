# Paper 002 — Research questions v0.3

> **Positioning:** [paper002_description_v0.1.md](paper002_description_v0.1.md)  
> **Pre-reg:** [paper002_prereg_v0.3.md](paper002_prereg_v0.3.md)

---

## Central question

> Under a frozen mock–Isaac occlusion contract, does a **continuous cheap proxy score** (five-seed median) rank exported occlusion mismatches by their **same-state counterfactual value** in Isaac simulation — and does a constrained LLM proposer meet prespecified adequacy vs a rule proposer?

This is **not** “does LLM generate a good training curriculum?” It is **“does the proxy predict which physics experiments are worth running?”**

---

## Sub-questions

| ID | Question | Hypothesis |
| --- | --- | --- |
| **RQ-B1** | Proxy validity on export set | H1 |
| **RQ-B2** | Selection utility (top vs bottom) | H2 |
| **RQ-B3** | LLM proposer adequacy | H3 |
| **RQ-B4** | Coverage vs diversity (G vs D) | S2 · exploratory |
| **RQ-B5** | Consensus vs single-seed export | S1 · sensitivity |

---

## Program sentence

> Paper 001 asks **how to measure** response quality after mismatch.  
> Paper 002 asks **which mismatches are worth measuring** before spending GPU on physics.

---

## Novelty (one line)

> POET/PLR/GenSim optimize **learning** from generated environments; Paper 002 validates **experiment selection** via mock-to-physics rank transfer @ same-state CF.
