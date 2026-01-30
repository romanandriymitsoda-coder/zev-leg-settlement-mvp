from __future__ import annotations
import json
import os
import sys
from pathlib import Path

import pandas as pd

# Ensure the src/ directory is on the import path when running from a clone
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from zevleg_mvp.profiles import generate_synthetic_year
from zevleg_mvp.billing import (
    Tariff,
    Scenario,
    outside_option_bills,
    community_utility_bill,
    gross_consumptions,
)
from zevleg_mvp.settlement import rule1_proportional, rule2_no_harm_budget_balanced
from zevleg_mvp.metrics import deltas, loser_share, max_increase
from zevleg_mvp.plots import plot_bill_changes, plot_fairness_frontier

HERE = os.path.dirname(__file__)

def main():
    # Load config
    with open(os.path.join(HERE, "..", "configs", "default.json"), "r", encoding="utf-8") as f:
        cfg = json.load(f)

    out_dir = os.path.join(HERE, "..", "outputs")
    os.makedirs(out_dir, exist_ok=True)

    tcfg = cfg["tariff"]
    tariff = Tariff(
        energy_price=tcfg["energy_price_chf_per_kwh"],
        grid_usage=tcfg["grid_usage_chf_per_kwh"],
        feed_in=tcfg["feed_in_chf_per_kwh"],
    )

    pcfg = cfg["profiles"]
    df = generate_synthetic_year(
        year=cfg["year"],
        seed=cfg["seed"],
        base_load_a_kwh_per_day=pcfg["base_load_a_kwh_per_day"],
        base_load_b_kwh_per_day=pcfg["base_load_b_kwh_per_day"],
        base_load_c_kwh_per_day=pcfg["base_load_c_kwh_per_day"],
        flex_energy_b_kwh_per_day=pcfg["flex_energy_b_kwh_per_day"],
        flex_shift_share_to_midday=pcfg["flex_shift_share_to_midday"],
        pv_kwp=pcfg["pv_kwp"],
        pv_capacity_factor_target=pcfg["pv_capacity_factor_target"],
    )

    outside = outside_option_bills(df, tariff)
    gross = gross_consumptions(df)

    rows_long = []
    points = []

    for scfg in cfg["scenarios"]:
        scenario = Scenario(name=scfg["name"], mode=scfg["mode"], leg_discount=scfg["leg_discount"])
        group_cost = community_utility_bill(df, tariff, scenario)

        alloc1 = rule1_proportional(group_cost, gross)
        delta1 = deltas(alloc1, outside)

        alloc2 = rule2_no_harm_budget_balanced(alloc1, outside, group_cost)
        delta2 = deltas(alloc2, outside)

        for actor in ["A", "B", "C"]:
            rows_long.append({"scenario": scenario.name, "rule": "R1", "actor": actor, "bill_chf": alloc1[actor], "outside_chf": outside[actor], "delta_chf": delta1[actor]})
            rows_long.append({"scenario": scenario.name, "rule": "R2", "actor": actor, "bill_chf": alloc2[actor], "outside_chf": outside[actor], "delta_chf": delta2[actor]})

        points.append({
            "scenario": scenario.name,
            "rule": "R1",
            "label": f"{scenario.name}-R1",
            "loser_share": loser_share(delta1),
            "max_increase_chf": max_increase(delta1),
        })
        points.append({
            "scenario": scenario.name,
            "rule": "R2",
            "label": f"{scenario.name}-R2",
            "loser_share": loser_share(delta2),
            "max_increase_chf": max_increase(delta2),
        })

    df_long = pd.DataFrame(rows_long)
    df_points = pd.DataFrame(points)

    df_long.to_csv(os.path.join(out_dir, "scenario_details.csv"), index=False)
    df_points.to_csv(os.path.join(out_dir, "scenario_summary.csv"), index=False)

    plot_bill_changes(df_long, os.path.join(out_dir, "graph1_bill_change.png"))
    plot_fairness_frontier(df_points, os.path.join(out_dir, "graph2_fairness_frontier.png"))

    print("Wrote outputs to:", out_dir)

if __name__ == "__main__":
    main()
