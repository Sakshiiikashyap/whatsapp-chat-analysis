"""
sentiment.py
------------
Sentiment analysis using VADER (preferred) with TextBlob as fallback.
Classifies each message as Positive, Negative, or Neutral.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# VADER is faster and better tuned for social media text
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _VADER_AVAILABLE = True
except ImportError:
    _VADER_AVAILABLE = False

try:
    from textblob import TextBlob
    _TEXTBLOB_AVAILABLE = True
except ImportError:
    _TEXTBLOB_AVAILABLE = False


BG     = "#0d1117"
FG     = "#e6edf3"
COLORS = {
    "Positive": "#25D366",
    "Neutral":  "#58a6ff",
    "Negative": "#f85149",
}


def _classify_vader(text: str, analyzer) -> str:
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    return "Neutral"


def _classify_textblob(text: str) -> str:
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.05:
        return "Positive"
    elif polarity < -0.05:
        return "Negative"
    return "Neutral"


def sentiment_analysis(
    df: pd.DataFrame,
    selected_user: str,
) -> tuple[plt.Figure, plt.Figure, pd.DataFrame]:
    """
    Perform sentiment analysis on messages.

    Parameters
    ----------
    df : pd.DataFrame
    selected_user : str

    Returns
    -------
    pie_fig  : matplotlib Figure – sentiment distribution pie chart
    bar_fig  : matplotlib Figure – sentiment over time line chart
    sent_df  : DataFrame with sentiment column appended
    """
    data = df if selected_user == "Overall" else df[df["user"] == selected_user]
    non_media = data[~data["is_media"]].copy()

    if non_media.empty:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No data.", ha="center", va="center", color=FG)
        fig.patch.set_facecolor(BG)
        return fig, fig, non_media

    # ── Classify ─────────────────────────────────────────────────────────
    if _VADER_AVAILABLE:
        analyzer = SentimentIntensityAnalyzer()
        non_media["sentiment"] = non_media["message"].apply(
            lambda m: _classify_vader(m, analyzer)
        )
    elif _TEXTBLOB_AVAILABLE:
        non_media["sentiment"] = non_media["message"].apply(_classify_textblob)
    else:
        non_media["sentiment"] = "Neutral"

    # ── Pie chart ─────────────────────────────────────────────────────────
    counts = non_media["sentiment"].value_counts()
    labels = counts.index.tolist()
    sizes  = counts.values.tolist()
    colors = [COLORS.get(l, "#aaa") for l in labels]

    pie_fig, ax = plt.subplots(figsize=(6, 5))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        colors=colors,
        startangle=140,
        wedgeprops={"edgecolor": BG, "linewidth": 2},
    )
    for t in texts + autotexts:
        t.set_color(FG)
    ax.set_title("Sentiment Distribution", fontsize=13, fontweight="bold", color=FG)
    pie_fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    plt.tight_layout()

    # ── Monthly sentiment trend ───────────────────────────────────────────
    trend = (
        non_media.groupby(["month_name", "year", "month", "sentiment"])
        .size()
        .reset_index(name="count")
        .sort_values(["year", "month"])
    )

    bar_fig, ax2 = plt.subplots(figsize=(12, 4))
    for sentiment, color in COLORS.items():
        subset = trend[trend["sentiment"] == sentiment]
        if not subset.empty:
            ax2.plot(
                subset["month_name"],
                subset["count"],
                label=sentiment,
                color=color,
                marker="o",
                markersize=4,
                linewidth=2,
            )

    ax2.set_title("Sentiment Trend Over Time", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Month")
    ax2.set_ylabel("Messages")
    ax2.legend(facecolor=BG, edgecolor="#444", labelcolor=FG)
    plt.xticks(rotation=45, ha="right", fontsize=8)

    bar_fig.patch.set_facecolor(BG)
    ax2.set_facecolor(BG)
    ax2.tick_params(colors=FG)
    ax2.xaxis.label.set_color(FG)
    ax2.yaxis.label.set_color(FG)
    ax2.title.set_color(FG)
    for spine in ax2.spines.values():
        spine.set_edgecolor("#21262d")
    ax2.grid(color="#21262d", linestyle="--", linewidth=0.5)
    plt.tight_layout()

    return pie_fig, bar_fig, non_media
