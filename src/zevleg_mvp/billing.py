from __future__ import annotations
import numpy as np
import pandas as pd
from dataclasses import dataclass

@dataclass(frozen=True)
class Tariff:
    energy_price: float     # CHF/kWh
    grid_usage: float       # CHF/kWh
    feed_in: float          # CHF/kWh (remuneration for exports)

@dataclass(frozen=True)
class Scenario:
    name: str
    mode: str               # 'ZEV' or 'LEG'
    leg_discount: float     # e.g. 0.15 means 15% discount on grid usage for shared-to-others portion

def outside_option_bills(df: pd.DataFrame, t: Tariff) -> dict[str, float]:
    """Bills if each archetype stays alone (no sharing)."""
    load_a = df["load_a"].sum()
    load_b = df["load_b"].sum()
    load_c = df["load_c"].sum()
    pv_c = df["pv_c"].sum()

    # A/B import all their load
    bill_a = (t.energy_price + t.grid_usage) * load_a
    bill_b = (t.energy_price + t.grid_usage) * load_b

    # C self-consumes PV only for itself; exports surplus
    import_c = (df["load_c"] - df["pv_c"]).clip(lower=0).sum()
    export_c = (df["pv_c"] - df["load_c"]).clip(lower=0).sum()
    bill_c = (t.energy_price + t.grid_usage) * import_c - t.feed_in * export_c

    return {"A": bill_a, "B": bill_b, "C": bill_c}

def community_utility_bill(df: pd.DataFrame, t: Tariff, s: Scenario) -> float:
    """Utility-bill cost for the community as a whole (PV treated as community asset in this MVP).

    ZEV:
      - grid usage charge applies only on net import at the perimeter (internal sharing avoids grid charges)
    LEG:
      - net import pays full grid usage
      - PV shared from C to others uses public grid => grid usage charge applies at a discount on that portion
    """
    total_load = (df["load_a"] + df["load_b"] + df["load_c"]).values
    pv = df["pv_c"].values

    net_import = np.clip(total_load - pv, 0, None).sum()
    export = np.clip(pv - total_load, 0, None).sum()

    energy_cost = t.energy_price * net_import - t.feed_in * export

    if s.mode.upper() == "ZEV":
        grid_cost = t.grid_usage * net_import
    elif s.mode.upper() == "LEG":
        # PV used by others beyond C's self-consumption
        self_sc = np.clip(df["load_c"].values - 0, 0, None)  # load_c
        pv_to_self = np.minimum(df["load_c"].values, pv)
        pv_surplus_after_self = np.clip(pv - pv_to_self, 0, None)
        load_others = (df["load_a"] + df["load_b"]).values
        pv_to_others = np.minimum(load_others, pv_surplus_after_self).sum()

        # Full grid usage on net imports + discounted grid usage on shared-to-others PV
        grid_cost = t.grid_usage * net_import + t.grid_usage * (1.0 - s.leg_discount) * pv_to_others
    else:
        raise ValueError(f"Unknown mode: {s.mode}")

    return float(energy_cost + grid_cost)

def gross_consumptions(df: pd.DataFrame) -> dict[str, float]:
    return {
        "A": float(df["load_a"].sum()),
        "B": float(df["load_b"].sum()),
        "C": float(df["load_c"].sum()),
    }
