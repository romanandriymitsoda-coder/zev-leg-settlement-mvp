from __future__ import annotations

def rule1_proportional(group_cost: float, gross_consumption: dict[str, float]) -> dict[str, float]:
    total = sum(gross_consumption.values())
    return {k: group_cost * (v/total) for k, v in gross_consumption.items()}

def rule2_no_harm_budget_balanced(
    alloc_rule1: dict[str, float],
    outside: dict[str, float],
    group_cost: float
) -> dict[str, float]:
    """No one pays more than outside option; fund caps from winners' savings; budget balanced.

    If the cap is infeasible (sum(outside) < group_cost), raise ValueError.
    """
    if sum(outside.values()) + 1e-9 < group_cost:
        raise ValueError("No-harm infeasible: group cost exceeds sum of outside-option bills")

    pay = dict(alloc_rule1)

    # Cap harmed participants to their outside option
    harmed = [k for k in pay if pay[k] > outside[k]]
    for k in harmed:
        pay[k] = outside[k]

    required = group_cost - sum(pay.values())
    if required <= 1e-9:
        # already covers or exceeds (numerical)
        # If exceeds due to rounding, scale down slightly
        if sum(pay.values()) > group_cost:
            scale = group_cost / sum(pay.values())
            pay = {k: v*scale for k, v in pay.items()}
        return pay

    winners = [k for k in pay if pay[k] < outside[k]]
    slack = {k: outside[k] - pay[k] for k in winners}
    total_slack = sum(slack.values())
    if total_slack + 1e-9 < required:
        raise ValueError("No-harm infeasible: winners' savings insufficient to fund caps")

    for k in winners:
        pay[k] += required * (slack[k] / total_slack)

    # Budget balance fix
    diff = group_cost - sum(pay.values())
    if abs(diff) > 1e-6:
        # distribute diff across winners (tiny)
        for k in winners:
            pay[k] += diff * (slack[k] / total_slack)

    return pay
