"""
stats.py
--------
Basic and user-level statistics extracted from the chat DataFrame.
"""

import re
import pandas as pd


LINK_PATTERN = re.compile(r"https?://\S+")


def fetch_stats(df: pd.DataFrame, selected_user: str) -> dict:
    """
    Compute high-level statistics for the selected user (or overall).

    Parameters
    ----------
    df : pd.DataFrame  — full preprocessed chat DataFrame
    selected_user : str — 'Overall' or a specific username

    Returns
    -------
    dict with keys:
        total_messages, total_words, media_count, link_count
    """
    data = df if selected_user == "Overall" else df[df["user"] == selected_user]

    total_messages = len(data)
    total_words = data["word_count"].sum()
    media_count = data["is_media"].sum()
    link_count = data["has_link"].sum()

    return {
        "total_messages": int(total_messages),
        "total_words": int(total_words),
        "media_count": int(media_count),
        "link_count": int(link_count),
    }


def most_active_users(df: pd.DataFrame, top_n: int = 10) -> tuple[pd.Series, pd.DataFrame]:
    """
    Return the most active users by message count.

    Returns
    -------
    counts : pd.Series  — message counts indexed by username (top_n)
    pct_df : pd.DataFrame — percentage share per user
    """
    counts = df["user"].value_counts().head(top_n)
    pct = round(df["user"].value_counts(normalize=True) * 100, 2).reset_index()
    pct.columns = ["User", "Message %"]
    return counts, pct
