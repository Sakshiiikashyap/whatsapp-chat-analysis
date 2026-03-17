"""
activity.py
-----------
Day-of-week, hour-of-day, and heatmap activity analysis.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import numpy as np

ACCENT = "#25D366"
BG     = "#0d1117"
FG     = "#e6edf3"
GRID   = "#21262d"

ORDERED_DAYS = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday",
]


def _apply_dark_style(ax, fig):
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)


def most_active_day(df: pd.DataFrame, selected_user: str) -> plt.Figure:
    """
    Horizontal bar chart – message count by day of week.
    """
    data = df if selected_user == "Overall" else df[df["user"] == selected_user]

    day_counts = (
        data["weekday_name"]
        .value_counts()
        .reindex(ORDERED_DAYS, fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(
        day_counts.index[::-1],
        day_counts.values[::-1],
        color=ACCENT,
        edgecolor="none",
    )
    # Highlight the busiest day
    max_idx = day_counts.values.argmax()
    bars[len(bars) - 1 - max_idx].set_color("#ffd700")

    ax.set_title("Activity by Day of Week", fontsize=13, fontweight="bold")
    ax.set_xlabel("Messages")
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.tight_layout()
    _apply_dark_style(ax, fig)
    return fig


def most_active_hour(df: pd.DataFrame, selected_user: str) -> plt.Figure:
    """
    Bar chart – message count by hour of day (0-23).
    """
    data = df if selected_user == "Overall" else df[df["user"] == selected_user]

    hour_counts = data["hour"].value_counts().sort_index().reindex(range(24), fill_value=0)

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(hour_counts.index, hour_counts.values, color=ACCENT, width=0.85, edgecolor="none")
    ax.set_title("Activity by Hour of Day", fontsize=13, fontweight="bold")
    ax.set_xlabel("Hour (24-hr)")
    ax.set_ylabel("Messages")
    ax.set_xticks(range(24))
    ax.set_xticklabels([f"{h:02d}" for h in range(24)], fontsize=8)
    plt.tight_layout()
    _apply_dark_style(ax, fig)
    return fig


def activity_heatmap(df: pd.DataFrame, selected_user: str) -> plt.Figure:
    """
    Seaborn heatmap: rows = day of week, columns = hour of day.
    """
    data = df if selected_user == "Overall" else df[df["user"] == selected_user]

    pivot = (
        data.groupby(["weekday_name", "hour"])
        .size()
        .reset_index(name="messages")
        .pivot(index="weekday_name", columns="hour", values="messages")
        .reindex(ORDERED_DAYS)
        .reindex(columns=range(24), fill_value=0)
        .fillna(0)
    )

    fig, ax = plt.subplots(figsize=(14, 5))
    sns.heatmap(
        pivot,
        ax=ax,
        cmap="YlGn",
        linewidths=0.4,
        linecolor=BG,
        annot=False,
        cbar_kws={"label": "Messages"},
    )
    ax.set_title("Activity Heatmap (Day × Hour)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Hour")
    ax.set_ylabel("")
    ax.tick_params(axis="x", labelsize=8)

    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)

    # Color bar text
    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.set_tick_params(color=FG)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=FG)
    cbar.set_label("Messages", color=FG)

    plt.tight_layout()
    return fig
