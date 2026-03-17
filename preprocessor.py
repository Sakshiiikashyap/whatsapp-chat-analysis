"""
preprocessor.py
---------------
Handles parsing and preprocessing of WhatsApp exported chat files.
Supports both Android and iPhone export formats.
"""

import re
import pandas as pd


# ── Regex Patterns ──────────────────────────────────────────────────────────

# Android: "12/31/23, 11:59 PM - User: Message"
ANDROID_PATTERN = re.compile(
    r"(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}(?:\s?[APap][Mm])?)\s-\s([^:]+?):\s(.+)"
)

# iPhone: "[31/12/23, 11:59:00 PM] User: Message"
IPHONE_PATTERN = re.compile(
    r"\[(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}:\d{2}(?:\s?[APap][Mm])?)\]\s([^:]+?):\s(.+)"
)

# System messages to skip (case-insensitive partial matches)
SYSTEM_KEYWORDS = [
    "messages and calls are end-to-end encrypted",
    "joined using this group's invite link",
    "added you",
    "was added",
    "left",
    "removed",
    "changed the subject",
    "changed this group",
    "changed their phone number",
    "security code changed",
    "created group",
    "pinned a message",
    "deleted this message",
    "this message was deleted",
    "you were added",
    "missed voice call",
    "missed video call",
]

MEDIA_OMITTED = "<media omitted>"
LINK_PATTERN = re.compile(r"https?://\S+")


def _is_system_message(message: str) -> bool:
    """Return True if the message is a WhatsApp system notification."""
    msg_lower = message.lower().strip()
    return any(kw in msg_lower for kw in SYSTEM_KEYWORDS)


def _detect_format(raw_text: str):
    """Detect whether the file is Android or iPhone format."""
    if IPHONE_PATTERN.search(raw_text[:2000]):
        return "iphone"
    if ANDROID_PATTERN.search(raw_text[:2000]):
        return "android"
    return None


def _parse_messages(raw_text: str, fmt: str) -> list[dict]:
    """
    Parse raw chat text into a list of message dictionaries.
    Handles multi-line messages by merging continuation lines.
    """
    pattern = IPHONE_PATTERN if fmt == "iphone" else ANDROID_PATTERN
    records = []
    current = None

    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue

        match = pattern.match(line)
        if match:
            if current:
                records.append(current)
            date, time, user, message = match.groups()
            current = {
                "date_str": date.strip(),
                "time_str": time.strip(),
                "user": user.strip(),
                "message": message.strip(),
            }
        else:
            # Continuation of a multi-line message
            if current:
                current["message"] += " " + line

    if current:
        records.append(current)

    return records


def preprocess(raw_text: str) -> pd.DataFrame:
    """
    Main preprocessing function.

    Parameters
    ----------
    raw_text : str
        Raw text content of the exported WhatsApp chat file.

    Returns
    -------
    pd.DataFrame
        Cleaned, structured DataFrame with columns:
        ['date', 'time', 'user', 'message',
         'year', 'month', 'month_name', 'day', 'hour', 'weekday', 'weekday_name',
         'is_media', 'has_link', 'word_count']
    """
    fmt = _detect_format(raw_text)
    if fmt is None:
        raise ValueError(
            "Unrecognised WhatsApp export format. "
            "Please export from the WhatsApp app (Android or iPhone)."
        )

    records = _parse_messages(raw_text, fmt)

    if not records:
        raise ValueError("No messages could be parsed from the file.")

    df = pd.DataFrame(records)

    # ── Filter system messages ───────────────────────────────────────────
    df = df[~df["message"].apply(_is_system_message)].reset_index(drop=True)

    # ── Parse datetime ───────────────────────────────────────────────────
    # Normalise separators so pandas can parse consistently
    df["datetime"] = pd.to_datetime(
        df["date_str"] + " " + df["time_str"],
        infer_datetime_format=True,
        dayfirst=True,
        errors="coerce",
    )
    df = df.dropna(subset=["datetime"]).reset_index(drop=True)

    df["date"] = df["datetime"].dt.date
    df["time"] = df["datetime"].dt.time
    df["year"] = df["datetime"].dt.year
    df["month"] = df["datetime"].dt.month
    df["month_name"] = df["datetime"].dt.strftime("%b %Y")
    df["day"] = df["datetime"].dt.day
    df["hour"] = df["datetime"].dt.hour
    df["weekday"] = df["datetime"].dt.dayofweek          # 0 = Monday
    df["weekday_name"] = df["datetime"].dt.strftime("%A")

    # ── Derived flags ────────────────────────────────────────────────────
    df["is_media"] = df["message"].str.lower().str.strip() == MEDIA_OMITTED.lower()
    df["has_link"] = df["message"].apply(lambda m: bool(LINK_PATTERN.search(m)))
    df["word_count"] = df["message"].apply(
        lambda m: 0 if m.lower().strip() == MEDIA_OMITTED.lower() else len(m.split())
    )

    # ── Final column selection ────────────────────────────────────────────
    return df[[
        "date", "time", "user", "message",
        "year", "month", "month_name", "day", "hour",
        "weekday", "weekday_name",
        "is_media", "has_link", "word_count",
    ]]
