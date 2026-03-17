"""
words.py
--------
Common word analysis, word cloud, and emoji analysis.
"""

import re
import collections
from typing import Optional

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from wordcloud import WordCloud
import emoji

# ── Stop words (English + common WhatsApp filler) ────────────────────────────
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "it", "its", "this", "that", "was", "are", "be",
    "been", "have", "has", "had", "do", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "not", "no", "i", "you", "he",
    "she", "we", "they", "me", "him", "her", "us", "them", "my", "your",
    "his", "our", "their", "what", "which", "who", "when", "where", "how",
    "so", "if", "than", "then", "just", "like", "up", "out", "also", "more",
    "now", "very", "ok", "okay", "yeah", "yes", "no", "lol", "haha", "ha",
    "<media", "omitted>", "null", "https", "http", "www",
}

ACCENT = "#25D366"
BG     = "#0d1117"
FG     = "#e6edf3"
GRID   = "#21262d"


def _clean_tokens(text: str) -> list[str]:
    """Lowercase, strip punctuation, remove stopwords and short tokens."""
    tokens = re.findall(r"\b[a-z]{3,}\b", text.lower())
    return [t for t in tokens if t not in STOPWORDS]


def _apply_dark_style(ax, fig):
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)


def common_words(
    df: pd.DataFrame,
    selected_user: str,
    top_n: int = 20,
) -> plt.Figure:
    """
    Horizontal bar chart of the most frequently used words.
    """
    data = df if selected_user == "Overall" else df[df["user"] == selected_user]
    non_media = data[~data["is_media"]]["message"]

    all_tokens = []
    for msg in non_media:
        all_tokens.extend(_clean_tokens(msg))

    if not all_tokens:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No words to display.", ha="center", va="center", color=FG)
        return fig

    counter = collections.Counter(all_tokens)
    most_common = counter.most_common(top_n)
    words, counts = zip(*most_common)

    fig, ax = plt.subplots(figsize=(8, max(4, top_n * 0.35)))
    ax.barh(words[::-1], counts[::-1], color=ACCENT, edgecolor="none")
    ax.set_title(f"Top {top_n} Most Common Words", fontsize=13, fontweight="bold")
    ax.set_xlabel("Frequency")
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.tight_layout()
    _apply_dark_style(ax, fig)
    return fig


def generate_wordcloud(df: pd.DataFrame, selected_user: str) -> plt.Figure:
    """
    Generate and return a word cloud figure.
    """
    data = df if selected_user == "Overall" else df[df["user"] == selected_user]
    non_media = data[~data["is_media"]]["message"]

    all_tokens = []
    for msg in non_media:
        all_tokens.extend(_clean_tokens(msg))

    if not all_tokens:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "Not enough text data.", ha="center", va="center", color=FG)
        fig.patch.set_facecolor(BG)
        return fig

    text = " ".join(all_tokens)

    wc = WordCloud(
        width=800,
        height=400,
        background_color=BG,
        colormap="YlGn",
        max_words=200,
        prefer_horizontal=0.85,
        collocations=False,
    ).generate(text)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Word Cloud", fontsize=13, fontweight="bold", color=FG)
    fig.patch.set_facecolor(BG)
    plt.tight_layout()
    return fig


def emoji_analysis(
    df: pd.DataFrame,
    selected_user: str,
    top_n: int = 15,
) -> tuple[Optional[plt.Figure], pd.DataFrame]:
    """
    Extract and count all emoji used in messages.

    Returns
    -------
    fig : matplotlib Figure (bar chart) or None if no emoji found
    emoji_df : DataFrame with columns ['Emoji', 'Count']
    """
    data = df if selected_user == "Overall" else df[df["user"] == selected_user]
    non_media = data[~data["is_media"]]["message"]

    all_emoji = []
    for msg in non_media:
        all_emoji.extend(
            ch for ch in msg if ch in emoji.EMOJI_DATA
        )

    if not all_emoji:
        return None, pd.DataFrame(columns=["Emoji", "Count"])

    counter = collections.Counter(all_emoji)
    emoji_df = pd.DataFrame(
        counter.most_common(top_n), columns=["Emoji", "Count"]
    )

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(emoji_df["Emoji"], emoji_df["Count"], color=ACCENT, edgecolor="none")
    ax.set_title(f"Top {top_n} Emoji Used", fontsize=13, fontweight="bold")
    ax.set_ylabel("Count")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    # Ensure emoji render properly on the x-axis
    ax.tick_params(axis="x", labelsize=14)

    _apply_dark_style(ax, fig)
    plt.tight_layout()
    return fig, emoji_df
