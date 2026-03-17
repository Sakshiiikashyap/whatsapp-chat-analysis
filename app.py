"""
app.py
------
WhatsApp Chat Analysis Tool — Streamlit front-end.

Run with:
    streamlit run app.py
"""

import io
import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use("Agg")

from preprocessor import preprocess
from stats      import fetch_stats, most_active_users
from timeline   import monthly_timeline, daily_timeline
from activity   import most_active_day, most_active_hour, activity_heatmap
from words      import common_words, generate_wordcloud, emoji_analysis
from sentiment  import sentiment_analysis
from report     import build_html_report

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WhatsApp Chat Analyser",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Dark background */
    .stApp { background-color: #0d1117; color: #e6edf3; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #161b22;
        border-right: 1px solid #21262d;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px;
    }
    div[data-testid="metric-container"] label {
        color: #8b949e !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #25D366 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    /* Section headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #e6edf3;
        border-left: 4px solid #25D366;
        padding-left: 12px;
        margin: 28px 0 12px 0;
    }

    /* Divider */
    hr { border-color: #21262d; }

    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Helper ────────────────────────────────────────────────────────────────────
def section(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/WhatsApp.svg/120px-WhatsApp.svg.png",
        width=60,
    )
    st.title("WhatsApp Analyser")
    st.markdown("---")

    uploaded = st.file_uploader(
        "📂 Upload your chat export (.txt)",
        type=["txt"],
        help="Export a chat from WhatsApp → More options → Export chat → Without media",
    )

    if uploaded:
        raw_text = uploaded.read().decode("utf-8", errors="replace")

        try:
            df = preprocess(raw_text)
        except ValueError as e:
            st.error(str(e))
            st.stop()

        users = ["Overall"] + sorted(df["user"].unique().tolist())
        selected_user = st.selectbox("👤 Select user", users)

        st.markdown("---")
        st.markdown(
            f"**📅 Date range**  \n"
            f"{df['date'].min()} → {df['date'].max()}"
        )
        st.markdown(f"**👥 Participants:** {df['user'].nunique()}")

        run_analysis = st.button("🔍 Analyse", use_container_width=True)
    else:
        st.info("Upload a WhatsApp `.txt` export to get started.")
        st.stop()


# ── Main panel ────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='color:#25D366; margin-bottom:4px;'>💬 WhatsApp Chat Analysis</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='color:#8b949e; margin-bottom:24px;'>Analysing: "
    f"<strong style='color:#e6edf3;'>{uploaded.name}</strong> "
    f"&nbsp;|&nbsp; User: <strong style='color:#e6edf3;'>{selected_user}</strong></p>",
    unsafe_allow_html=True,
)

if not run_analysis:
    st.markdown(
        """
        <div style='text-align:center; padding: 80px 20px; color:#8b949e;'>
          <div style='font-size:4rem;'>📊</div>
          <h3 style='color:#e6edf3; margin:12px 0 6px;'>Ready to analyse</h3>
          <p>Select a user in the sidebar and click <strong>Analyse</strong>.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ════════════════════════════════════════════════════════════════════════════ #
# 1. BASIC STATS
# ════════════════════════════════════════════════════════════════════════════ #
section("📈 Basic Statistics")
stats = fetch_stats(df, selected_user)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Messages", f"{stats['total_messages']:,}")
c2.metric("Total Words",    f"{stats['total_words']:,}")
c3.metric("Media Shared",   f"{stats['media_count']:,}")
c4.metric("Links Shared",   f"{stats['link_count']:,}")


# ════════════════════════════════════════════════════════════════════════════ #
# 2. USER ANALYSIS (group chats only)
# ════════════════════════════════════════════════════════════════════════════ #
if selected_user == "Overall" and df["user"].nunique() > 1:
    section("👥 User Activity")
    counts, pct_df = most_active_users(df)

    col_chart, col_table = st.columns([2, 1])

    import matplotlib.pyplot as plt

    fig_users, ax = plt.subplots(figsize=(8, max(4, len(counts) * 0.4)))
    ax.barh(counts.index[::-1], counts.values[::-1], color="#25D366", edgecolor="none")
    ax.set_title("Messages per User", fontsize=13, fontweight="bold")
    ax.set_xlabel("Messages")
    fig_users.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")
    ax.tick_params(colors="#e6edf3")
    ax.xaxis.label.set_color("#e6edf3")
    ax.title.set_color("#e6edf3")
    for spine in ax.spines.values():
        spine.set_edgecolor("#21262d")
    plt.tight_layout()

    col_chart.pyplot(fig_users)
    col_table.dataframe(pct_df, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════ #
# 3. TIMELINE
# ════════════════════════════════════════════════════════════════════════════ #
section("📅 Timeline Analysis")
col_m, col_d = st.columns(2)

fig_month = monthly_timeline(df, selected_user)
fig_day   = daily_timeline(df, selected_user)
col_m.pyplot(fig_month)
col_d.pyplot(fig_day)


# ════════════════════════════════════════════════════════════════════════════ #
# 4. ACTIVITY PATTERNS
# ════════════════════════════════════════════════════════════════════════════ #
section("⏰ Activity Patterns")
col_a1, col_a2 = st.columns(2)
fig_dow = most_active_day(df, selected_user)
fig_hour = most_active_hour(df, selected_user)
col_a1.pyplot(fig_dow)
col_a2.pyplot(fig_hour)

st.markdown("")
fig_heat = activity_heatmap(df, selected_user)
st.pyplot(fig_heat)


# ════════════════════════════════════════════════════════════════════════════ #
# 5. WORD ANALYSIS
# ════════════════════════════════════════════════════════════════════════════ #
section("💬 Word Analysis")
col_w1, col_w2 = st.columns(2)

fig_words = common_words(df, selected_user)
col_w1.pyplot(fig_words)

fig_wc = generate_wordcloud(df, selected_user)
col_w2.pyplot(fig_wc)

section("😊 Emoji Analysis")
fig_emoji, emoji_df = emoji_analysis(df, selected_user)
if fig_emoji:
    col_e1, col_e2 = st.columns([2, 1])
    col_e1.pyplot(fig_emoji)
    col_e2.dataframe(emoji_df, use_container_width=True, hide_index=True)
else:
    st.info("No emoji found in the selected messages.")


# ════════════════════════════════════════════════════════════════════════════ #
# 6. SENTIMENT ANALYSIS
# ════════════════════════════════════════════════════════════════════════════ #
section("🧠 Sentiment Analysis")

with st.spinner("Running sentiment analysis…"):
    pie_fig, trend_fig, sent_df = sentiment_analysis(df, selected_user)

col_s1, col_s2 = st.columns([1, 2])
col_s1.pyplot(pie_fig)
col_s2.pyplot(trend_fig)

if not sent_df.empty and "sentiment" in sent_df.columns:
    counts_s = sent_df["sentiment"].value_counts()
    st.markdown("")
    c1, c2, c3 = st.columns(3)
    c1.metric("😊 Positive", f"{counts_s.get('Positive', 0):,}")
    c2.metric("😐 Neutral",  f"{counts_s.get('Neutral', 0):,}")
    c3.metric("😞 Negative", f"{counts_s.get('Negative', 0):,}")


# ════════════════════════════════════════════════════════════════════════════ #
# 7. DOWNLOAD REPORT
# ════════════════════════════════════════════════════════════════════════════ #
st.markdown("---")
section("📥 Download Report")

figs_for_report = {
    "Monthly Timeline":      fig_month,
    "Daily Timeline":        fig_day,
    "Activity by Day":       fig_dow,
    "Activity by Hour":      fig_hour,
    "Activity Heatmap":      fig_heat,
    "Most Common Words":     fig_words,
    "Word Cloud":            fig_wc,
    "Emoji Analysis":        fig_emoji,
    "Sentiment Distribution": pie_fig,
    "Sentiment Trend":        trend_fig,
}

html_report = build_html_report(stats, selected_user, figs_for_report)

col_dl1, col_dl2 = st.columns(2)

col_dl1.download_button(
    label="📄 Download HTML Report",
    data=html_report.encode("utf-8"),
    file_name="whatsapp_analysis_report.html",
    mime="text/html",
    use_container_width=True,
)

# CSV export of raw data
csv_data = (
    df[["date", "time", "user", "message",
        "year", "month", "day", "hour", "weekday_name",
        "is_media", "has_link", "word_count"]]
    .to_csv(index=False)
    .encode("utf-8")
)

col_dl2.download_button(
    label="📊 Download CSV Data",
    data=csv_data,
    file_name="whatsapp_chat_data.csv",
    mime="text/csv",
    use_container_width=True,
)

st.success("✅ Analysis complete! Scroll up to explore your insights.")
