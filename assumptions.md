# Assumptions (MVP)

This MVP is intentionally minimal. It is designed to demonstrate the *method* (settlement-rule comparison + fairness metrics)
rather than to exactly replicate any specific Swiss DSO’s billing logic.

## Tariffs (in `configs/default.json`)
- energy price: 0.18 CHF/kWh
- grid usage charge: 0.12 CHF/kWh
- feed-in remuneration: 0.08 CHF/kWh

Replace these with ElCom tariff data later (e.g., via LINDAS/SPARQL).

## LEG network-charge discount
- modelled as a parameter on grid usage charges for the *PV shared to other meters*:
  `grid_usage * (1 - discount) * pv_to_others`
- scenarios include 15% and 30% discount factors (configurable)

## Profiles
- hourly synthetic year (no external data needed)
- A: evening-peaking household
- B: household + flexible daily EV/HP energy shifted into 10:00–15:00 window
- C: household + PV generation; PV treated as a community asset in the community case

## Settlement rules
- Rule 1: group utility-bill cost allocated proportional to gross consumption
- Rule 2: no participant pays above outside option; cap funded by winners’ savings; budget balanced
