# ZEV/LEG settlement-rule MVP simulator (Python)

A tiny, reproducible simulator for a Swiss ZEV/LEG thesis pre-proposal. It:
- compares **two settlement rules** (baseline proportional vs **no-harm cap with budget-balanced side-payments**),
- switches **ZEV vs LEG** and applies a **topology-dependent network-charge discount** (e.g., 15% / 30%),
- reports **winners/losers** (delta bill vs outside option) and a **fairness view** (max increase + loser share).

> Research question → outputs  
> How do ZEV vs LEG settlement rules shift cost fairness and dispute risk?  
> Synthetic hourly demand/PV + tariff params → two figures + CSV summaries in `outputs/` and `docs/`.

## Quick start (copy/paste)

**macOS / Linux (bash/zsh):**
```bash
cd "$(dirname "$0")"
./run.sh
```
_If needed: `chmod +x run.sh` once._

**Windows (PowerShell):**
```powershell
cd $PSScriptRoot  # or: cd path\to\repo
.\run.bat
```
These scripts create `.venv` if missing, activate it, install `requirements.txt`, run `scripts/run_mvp.py`, and write outputs into `outputs/`.

Manual fallback (all platforms, after `cd` to repo):
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/run_mvp.py
```

## Results (figures)

![Annual bill change](docs/graph1_bill_change.png)  
*Annual Δ bill per archetype (A/B/C) for each scenario under Rule 1 vs Rule 2; bars below zero are savings.*

![Fairness frontier](docs/graph2_fairness_frontier.png)  
*Fairness / dispute-risk frontier: loser share vs max bill increase, labeled by scenario and rule.*

### Outputs produced
- `outputs/graph1_bill_change.png` — annual delta bill per archetype (A/B/C) for each scenario and rule.
- `outputs/graph2_fairness_frontier.png` — scatter of loser share vs max increase (fairness/dispute-risk frontier) with labels.
- `outputs/scenario_summary.csv` — compact table per scenario/rule with fairness metrics.
- `outputs/scenario_details.csv` — long-form table per scenario/rule/actor with bills and deltas.

The default configuration lives in `configs/default.json`. Tweak tariff levels, profile parameters, or scenario definitions there and re-run the script to regenerate the four outputs.

## How the model works

**Archetypes (synthetic, 1 year, hourly resolution)**
- **A** – inflexible household with an evening-peaking demand shape.
- **B** – flexible household: same base load plus EV/heat-pump energy shifted toward midday PV hours.
- **C** – PV prosumer: household load plus rooftop PV generation (PV treated as a community asset in the community case).

**Tariff structure**
- Energy price (CHF/kWh), grid-usage charge (CHF/kWh), feed-in remuneration for exported PV (CHF/kWh) — all set in `configs/default.json`.

**ZEV vs LEG**
- **ZEV**: internal PV sharing is behind a single “perimeter”; grid-usage applies only on **net import at the perimeter**.
- **LEG**: PV shared from the prosumer to other meters uses the public grid. Net import pays full grid usage, and the *shared-to-others* PV portion pays grid usage multiplied by a **discount factor** (e.g., 15% or 30%). The discount applies only to that shared-to-others portion.

**Settlement rules (inside the community)**
- **Rule 1 – proportional allocation**: community utility-bill cost is allocated to A/B/C in proportion to their gross annual consumption.
- **Rule 2 – no-harm, budget-balanced**: no one pays more than their **outside option** (what they would pay alone); caps for harmed participants are funded from winners’ savings; totals remain equal to the community bill (budget balance).

**Fairness metrics**
- **Delta bill per actor**: community bill minus outside-option bill (negative = savings, positive = harm).
- **Loser share**: fraction of actors with delta > 0 (worse off).
- **Max increase**: largest delta > 0 across actors (simple dispute-risk proxy).

## Scenarios

The demo runner evaluates three scenarios from `configs/default.json`:
- `ZEV`
- `LEG_15` (LEG with 15% discount on the shared-to-others PV grid-usage portion)
- `LEG_30` (LEG with 30% discount)

Each scenario is evaluated under both settlement rules (Rule 1 and Rule 2); results are exported to `outputs/` as described above.

## Dependencies

Minimal and focused on the scientific core: `numpy`, `pandas`, `matplotlib` (see `requirements.txt`).

## Data sources & assumptions
- Synthetic hourly load/PV profiles are generated procedurally (see `src/zevleg_mvp/profiles.py`) using the parameters in `configs/default.json`.
- Tariffs (energy price, grid usage, feed-in) are parameters in `configs/default.json`.
- Thesis extension: replace those tariff parameters with official ElCom tariff data fetched from LINDAS via SPARQL (see LINDAS/ElCom tariff catalog reference).

## Thesis extension plan (next steps)
- Wire the SPARQL fetch to import official ElCom tariff data into the config layer.
- Cross-check synthetic profiles against a small set of measured smart-meter traces; document variance.
- Add sensitivity analysis (PV size, flexibility share, tariff spread) with small Monte-Carlo sweeps.
- Package notebooks/figures for committee review (single command to regenerate all artefacts).

## GitHub / repo hygiene

`.gitignore` ignores the local virtual environment (`.venv/`), Python bytecode (`__pycache__/`, `*.pyc`), generated outputs (`outputs/`), and macOS metadata (`.DS_Store`). For publication you can either keep outputs ignored and attach example figures via GitHub Releases/screenshots, or temporarily remove `outputs/` from `.gitignore` and commit a curated subset.
