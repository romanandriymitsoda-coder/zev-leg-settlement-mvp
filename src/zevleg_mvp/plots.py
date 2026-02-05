from __future__ import annotations

import hashlib
import pandas as pd
import matplotlib.pyplot as plt


def plot_bill_changes(df_long: pd.DataFrame, outpath: str) -> None:
    """Grouped bar chart: delta bill per archetype by scenario, split per rule."""
    order_s = list(dict.fromkeys(df_long["scenario"]))
    actors = list(dict.fromkeys(df_long["actor"]))
    rules = ["R1", "R2"]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    x = list(range(len(order_s)))
    bar_width = 0.8 / max(len(actors), 1)

    for ax, rule, title in zip(axes, rules, ["Rule 1 - proportional", "Rule 2 - no-harm"]):
        sub = df_long[df_long.rule == rule]
        pivot = sub.pivot(index="scenario", columns="actor", values="delta_chf").reindex(order_s)
        for idx, actor in enumerate(actors):
            offset = (idx - (len(actors) - 1) / 2) * bar_width
            y = pivot[actor].astype(float).tolist()
            positions = [xi + offset for xi in x]
            ax.bar(positions, y, width=bar_width, label=actor)
        ax.axhline(0, linewidth=1, color="gray")
        ax.set_xticks(x)
        ax.set_xticklabels(order_s)
        ax.set_title(title)
        ax.grid(True, axis="y", alpha=0.25)

    axes[0].set_ylabel("Delta bill vs outside option (CHF/year)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.suptitle("Annual bill change per archetype (negative = savings)")
    fig.legend(handles, labels, loc="upper center", ncols=len(actors), bbox_to_anchor=(0.5, 1.08), fontsize=8, title="Actor")
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(outpath, dpi=200)
    plt.close(fig)


def plot_fairness_frontier(df_points: pd.DataFrame, outpath: str) -> None:
    """Scatter plot: loser share vs max increase with deterministic label offsets."""

    def _label_offset(label: str) -> tuple[int, int]:
        """Deterministic, small text offsets derived from a hash to avoid overlap."""
        digest = hashlib.sha1(label.encode("utf-8")).digest()

        def _component(b_mag: int, b_sign: int) -> int:
            magnitude = 6 + (b_mag % 13)  # 6-18 point shift
            sign = 1 if (b_sign % 2) else -1
            return magnitude * sign

        return _component(digest[0], digest[1]), _component(digest[2], digest[3])

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df_points["loser_share"], df_points["max_increase_chf"])

    near_mask = (df_points["loser_share"] <= 0.02) & (df_points["max_increase_chf"] <= 10)
    near = df_points[near_mask].sort_values("label").reset_index(drop=True)
    far = df_points[~near_mask]

    # Stack near-origin labels upward with deterministic spacing
    for i, r in near.iterrows():
        dx, dy = 8, 10 + i * 15  # dy increases by 15 points per stacked label
        ax.annotate(
            r["label"],
            (r["loser_share"], r["max_increase_chf"]),
            textcoords="offset points",
            xytext=(dx, dy),
            fontsize=9,
            bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "alpha": 0.7, "edgecolor": "none"},
        )

    # Other points use hash-based deterministic offsets
    for _, r in far.iterrows():
        dx, dy = _label_offset(r["label"])
        ax.annotate(
            r["label"],
            (r["loser_share"], r["max_increase_chf"]),
            textcoords="offset points",
            xytext=(dx, dy),
            fontsize=9,
            bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "alpha": 0.7, "edgecolor": "none"},
        )

    ax.set_xlabel("Loser share (fraction with delta>0)")
    ax.set_ylabel("Max bill increase (CHF/year)")
    ax.set_title("Fairness / dispute-risk frontier across scenarios")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    plt.close(fig)
