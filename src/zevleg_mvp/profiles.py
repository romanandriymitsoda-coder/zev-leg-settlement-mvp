from __future__ import annotations
import numpy as np
import pandas as pd

def _daily_shape_evening_peak(hours: np.ndarray) -> np.ndarray:
    # Two peaks: morning + stronger evening; normalized to mean ~1
    h = hours
    morning = np.exp(-0.5*((h-8.0)/2.2)**2)
    evening = 1.7*np.exp(-0.5*((h-19.0)/2.8)**2)
    base = 0.35
    shape = base + morning + evening
    return shape / shape.mean()

def _daily_shape_flat(hours: np.ndarray) -> np.ndarray:
    h = hours
    # Mild day pattern; normalized to mean ~1
    shape = 0.9 + 0.15*np.exp(-0.5*((h-13.0)/4.0)**2)
    return shape / shape.mean()

def _pv_shape_midday(hours: np.ndarray, day_of_year: int) -> np.ndarray:
    # Simple bell around solar noon; seasonal scaling by day-of-year (rough)
    h = hours
    noon = 12.5
    width = 2.6 + 1.2*np.cos(2*np.pi*(day_of_year-172)/365.0)  # wider in summer
    bell = np.exp(-0.5*((h-noon)/width)**2)
    # seasonal amplitude (peak in summer, low in winter)
    season = 0.35 + 0.65*(0.5*(1 + np.cos(2*np.pi*(day_of_year-172)/365.0)))
    return season * bell

def generate_synthetic_year(
    year: int,
    base_load_a_kwh_per_day: float,
    base_load_b_kwh_per_day: float,
    base_load_c_kwh_per_day: float,
    flex_energy_b_kwh_per_day: float,
    flex_shift_share_to_midday: float,
    pv_kwp: float,
    pv_capacity_factor_target: float,
    seed: int = 7,
) -> pd.DataFrame:
    """Return hourly synthetic profiles for one year.

    Columns:
      load_a, load_b, load_c, pv_c, flex_b (flex component included already in load_b)
    """
    rng = np.random.default_rng(seed)
    idx = pd.date_range(f"{year}-01-01", f"{year}-12-31 23:00", freq="h")
    n = len(idx)
    hours = idx.hour.values.astype(float)
    doy = idx.dayofyear.values.astype(int)

    # Baseline loads (kWh per hour), with daily shapes
    shape_a = _daily_shape_evening_peak(hours)
    shape_b = _daily_shape_flat(hours)
    shape_c = _daily_shape_flat(hours)

    # Add mild seasonality: slightly higher winter consumption
    winter_factor = 1.0 + 0.10*np.cos(2*np.pi*(doy-15)/365.0)

    # Random hourly noise (small)
    noise = rng.normal(0, 0.06, size=n)

    load_a = (base_load_a_kwh_per_day/24.0) * shape_a * winter_factor * (1 + noise).clip(0.75, 1.35)
    load_b_base = (base_load_b_kwh_per_day/24.0) * shape_b * winter_factor * (1 + 0.8*noise).clip(0.75, 1.35)
    load_c = (base_load_c_kwh_per_day/24.0) * shape_c * winter_factor * (1 + 0.7*noise).clip(0.75, 1.35)

    # Flexible B component: daily energy that can be shifted to midday window.
    flex = np.zeros(n)
    for day in pd.date_range(f"{year}-01-01", f"{year}-12-31", freq="D"):
        mask = (idx.date == day.date())
        day_hours = idx[mask].hour.values
        # default: evening hours 18-22
        evening_mask = (day_hours >= 18) & (day_hours <= 22)
        midday_mask = (day_hours >= 10) & (day_hours <= 15)

        e = flex_energy_b_kwh_per_day
        e_mid = e * flex_shift_share_to_midday
        e_eve = e - e_mid

        # distribute within windows
        if evening_mask.sum() > 0:
            flex[mask][evening_mask] += e_eve / evening_mask.sum()
        if midday_mask.sum() > 0:
            flex[mask][midday_mask] += e_mid / midday_mask.sum()

    load_b = load_b_base + flex

    # PV profile for C (kWh per hour). Scale to target annual capacity factor.
    pv_raw = np.array([_pv_shape_midday(h, d) for h, d in zip(hours, doy)])
    # Add clouds/noise
    pv_raw = pv_raw * rng.lognormal(mean=-0.05, sigma=0.25, size=n)
    pv_raw[pv_raw < 0] = 0

    # Scale: annual energy = pv_kwp * 8760 * capacity_factor_target
    target_annual_kwh = pv_kwp * 8760.0 * pv_capacity_factor_target
    scale = target_annual_kwh / pv_raw.sum()
    pv_c = pv_raw * scale

    df = pd.DataFrame({
        "load_a": load_a,
        "load_b": load_b,
        "load_c": load_c,
        "pv_c": pv_c,
        "flex_b": flex,
    }, index=idx)
    return df
