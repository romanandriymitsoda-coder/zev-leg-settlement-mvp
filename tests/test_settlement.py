from __future__ import annotations
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from zevleg_mvp.metrics import deltas, loser_share
from zevleg_mvp.settlement import rule1_proportional, rule2_no_harm_budget_balanced


def _example_case():
    """Deterministic toy case with feasible no-harm caps."""
    gross = {"A": 100.0, "B": 100.0, "C": 100.0}
    outside = {"A": 90.0, "B": 110.0, "C": 120.0}
    group_cost = 300.0  # below sum(outside) so caps are feasible
    alloc_r1 = rule1_proportional(group_cost, gross)
    alloc_r2 = rule2_no_harm_budget_balanced(alloc_r1, outside, group_cost)
    return outside, group_cost, alloc_r2


def test_rule2_caps_at_outside_option():
    outside, _, alloc_r2 = _example_case()
    for actor, payment in alloc_r2.items():
        assert payment <= outside[actor] + 1e-9


def test_rule2_budget_balance():
    outside, group_cost, alloc_r2 = _example_case()
    total = sum(alloc_r2.values())
    assert math.isclose(total, group_cost, rel_tol=0, abs_tol=1e-6)


def test_rule2_loser_share_zero():
    outside, _, alloc_r2 = _example_case()
    delta = deltas(alloc_r2, outside)
    assert loser_share(delta) <= 1e-9
