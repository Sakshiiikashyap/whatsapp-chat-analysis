"""
timeline.py
-----------
Monthly and daily message timeline analysis.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ── Shared style ─────────────────────────────────────────────────────────────
ACCENT = "#25D366"      # WhatsApp green
BG     = "#0d1117"
FG     = "#e6edf3"
GRID   = "#21262d"


def _apply_dark_style(ax, fig):
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)
    ax.grid(color=GRID, linestyle="--", linewidth=0.5)


def monthly_timeline(df: pd.DataFrame, selected_user: str) -> plt.Figure:
    """
    Line chart of total messages per calendar month.

    Parameters
    ----------
    df : pd.DataFrame
    selected_user : str

    Returns
    -------
    matplotlib Figure
    """
    data = df if selected_user == "Overall" else df[df["user"] == selected_user]

    timeline = (
        data.groupby(["year", "month", "month_name"])
        .size()
        .reset_index(name="messages")
        .sort_values(["year", "month"])
    )

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(
        timeline["month_name"],
        timeline["messages"],
        color=ACCENT,
        linewidth=2,
        marker="o",
        markersize=5,
    )
    ax.fill_between(
        timeline["month_name"],
        timeline["messages"],
        alpha=0.15,
        color=ACCENT,
    )
    ax.set_title("Monthly Timeline", fontsize=14, fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Messages")
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.tight_layout()
    _apply_dark_style(ax, fig)
    return fig


def daily_timeline(df: pd.DataFrame, selected_user: str) -> plt.Figure:
    """
    Line chart of total messages per day.

    Returns
    -------
    matplotlib Figure
    """
    data = df if selected_user == "Overall" else df[df["user"] == selected_user]

    daily = data.groupby("date").size().reset_index(name="messages")

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(
        daily["date"],
        daily["messages"],
        color="#58a6ff",
        linewidth=1.2,
        alpha=0.9,
    )
    ax.fill_between(daily["date"], daily["messages"], alpha=0.1, color="#58a6ff")
    ax.set_title("Daily Timeline", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Messages")
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.tight_layout()
    _apply_dark_style(ax, fig)
    return fig
