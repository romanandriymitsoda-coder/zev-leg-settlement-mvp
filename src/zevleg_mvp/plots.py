from __future__ import annotations
import pandas as pd
import matplotlib.pyplot as plt

def plot_bill_changes(df_long: pd.DataFrame, outpath: str) -> None:
    """Grouped bar chart of Δ bill by archetype, scenario, rule."""
    # df_long columns: scenario, rule, actor, delta_chf
    order_s = list(dict.fromkeys(df_long['scenario']))
    order_r = list(dict.fromkeys(df_long['rule']))
    actors = list(dict.fromkeys(df_long['actor']))

    # Create a tidy pivot for plotting with consistent positions
    fig, ax = plt.subplots(figsize=(11, 5))
    x = range(len(order_s))
    width = 0.12

    # For each actor+rule, plot bars across scenarios
    offset = - (len(actors)*len(order_r)-1)/2 * width
    i = 0
    for actor in actors:
        for rule in order_r:
            sub = df_long[(df_long.actor==actor) & (df_long.rule==rule)]
            y = [float(sub[sub.scenario==s]['delta_chf'].values[0]) for s in order_s]
            ax.bar([xi + offset + i*width for xi in x], y, width=width, label=f"{actor}-{rule}")
            i += 1

    ax.axhline(0, linewidth=1)
    ax.set_xticks(list(x))
    ax.set_xticklabels(order_s)
    ax.set_ylabel("Δ bill vs outside option (CHF/year)")
    ax.set_title("Annual bill change per archetype (negative = savings)")
    ax.legend(ncols=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    plt.close(fig)

def plot_fairness_frontier(df_points: pd.DataFrame, outpath: str) -> None:
    """Scatter plot: loser share vs max increase."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df_points['loser_share'], df_points['max_increase_chf'])
    for _, r in df_points.iterrows():
        ax.annotate(r['label'], (r['loser_share'], r['max_increase_chf']), textcoords="offset points", xytext=(6,6), fontsize=9)
    ax.set_xlabel("Loser share (fraction with Δ>0)")
    ax.set_ylabel("Max bill increase (CHF/year)")
    ax.set_title("Fairness / dispute-risk frontier across scenarios")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    plt.close(fig)
