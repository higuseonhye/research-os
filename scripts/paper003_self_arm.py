"""The SELF arm test: is the relation distinguishable from the target's own path?

Implements the decision rule in `docs/paper003/paper003_self_arm_prereg_v1.0.md`
exactly, and nothing else. The rule was locked before this file was written.

    population   capture coupling, burst schedule, 1 body, condition `coupled`
    eligibility  valid and resolved, commit offset in [+4, +8]
    sample       n = 200 eligible cells, seeds from 3000 upward

The band and the seeds moved once, under the amendment recorded in the rule:
`dispense_latency` was derived from the physical carry speed and rose from 6 to
8, the commit window is one dispense-length either side of the arrival, and the
band is where arm D can act - measured on seeds 2000-2119, disjoint from these.
Nothing else moved: the arm, the asymmetry, alpha, the margin, n and the test
are as first locked.
    pairing      SELF and D scored on the same cell
    test         one-sided exact McNemar on discordant pairs, alpha = 0.05
    margin       p_D - p_SELF >= 0.15
    verdict      H2 survives only if both hold; otherwise H2 is rejected

There is no flag to relax any of those, on purpose.

    python scripts/paper003_self_arm.py
"""

from __future__ import annotations

import argparse
import json
from math import comb

import numpy as np

from wm_expansion.cell import CellSpec, run_cell
from wm_expansion.commitment_episode import EpisodeSpec
from wm_expansion.encounter import EncounterSpec

TARGET = np.array([0.20, 0.0, 0.40])

# Preregistered. Not command-line options.
SAMPLE = 200
OFFSET_BAND = (4, 8)
ALPHA = 0.05
MARGIN = 0.15
FIRST_SEED = 3000


def collect(sample: int = SAMPLE, seed_cap: int = 20_000) -> tuple[list[dict], int]:
    """Draw seeds from 300 upward until `sample` eligible cells are collected."""

    spec = EpisodeSpec()
    encounter = EncounterSpec(bodies=1, schedule="burst")
    eligible: list[dict] = []
    seed = FIRST_SEED
    while len(eligible) < sample and seed < FIRST_SEED + seed_cap:
        record = run_cell(
            TARGET,
            spec,
            encounter,
            CellSpec(condition="coupled", seed=seed, coupling="capture"),
            drive=lambda target: False,
        )
        offset = record["commit_offset"]
        if (
            record["valid"]
            and record["resolved"] is not None
            and offset is not None
            and OFFSET_BAND[0] <= offset <= OFFSET_BAND[1]
        ):
            eligible.append(record)
        seed += 1
    return eligible, seed - FIRST_SEED


def exact_mcnemar_one_sided(wins: int, losses: int) -> float:
    """P(X >= wins) for X ~ Binomial(wins + losses, 0.5).

    The discordant pairs are the whole of the information in a paired binary
    comparison: cells where both arms landed, or neither did, say nothing about
    which is better. Exact rather than the chi-square approximation because the
    discordant count can be small and the approximation is not trustworthy there.
    """

    total = wins + losses
    if total == 0:
        return 1.0  # no discordant pairs: no evidence of any difference
    tail = sum(comb(total, k) for k in range(wins, total + 1))
    return tail / 2.0**total


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=str, default=None)
    args = parser.parse_args()

    records, seeds_drawn = collect()
    n = len(records)
    if n < SAMPLE:
        raise SystemExit(f"only {n} eligible cells in {seeds_drawn} seeds; rule needs {SAMPLE}")

    d = np.array([r["resolved"]["D"] for r in records])
    s = np.array([r["resolved"]["SELF"] for r in records])
    p_d, p_self = float(d.mean()), float(s.mean())
    wins = int(np.count_nonzero(d & ~s))
    losses = int(np.count_nonzero(~d & s))
    p_value = exact_mcnemar_one_sided(wins, losses)
    margin = p_d - p_self

    superiority = p_value < ALPHA
    sufficient = margin >= MARGIN
    survives = superiority and sufficient

    print(f"eligible cells      n = {n}  (from {seeds_drawn} seeds)")
    print(f"  arm A             {np.mean([r['resolved']['A'] for r in records]):.3f}")
    print(f"  arm B             {np.mean([r['resolved']['B'] for r in records]):.3f}")
    print(f"  arm C             {np.mean([r['resolved']['C'] for r in records]):.3f}")
    print(f"  arm SELF          {p_self:.3f}   acted {np.mean([r['self_estimated'] for r in records]):.3f}")
    print(f"  arm D             {p_d:.3f}   acted {np.mean([r['d_estimated'] for r in records]):.3f}")
    print()
    print(f"discordant pairs    D only {wins}   SELF only {losses}")
    print(f"  superiority       p = {p_value:.5f}   (alpha {ALPHA})      {'PASS' if superiority else 'FAIL'}")
    print(f"  margin            {margin:+.3f}        (>= {MARGIN})        {'PASS' if sufficient else 'FAIL'}")
    print()
    print(f"VERDICT   {'Case A - H2 stands' if survives else 'Case B - H2 REJECTED'}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "n": n,
                    "seeds_drawn": seeds_drawn,
                    "p_D": p_d,
                    "p_SELF": p_self,
                    "margin": margin,
                    "discordant_D_only": wins,
                    "discordant_SELF_only": losses,
                    "p_value": p_value,
                    "superiority": superiority,
                    "margin_met": sufficient,
                    "h2_survives": survives,
                },
                handle,
                indent=2,
            )


if __name__ == "__main__":
    main()
