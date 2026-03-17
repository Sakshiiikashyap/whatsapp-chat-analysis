# 💬 WhatsApp Chat Analysis Tool

A production-grade Streamlit web app that turns your exported WhatsApp chat into deep, interactive insights — timelines, activity heatmaps, word clouds, emoji stats, and AI-powered sentiment analysis.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

### 3. Export your WhatsApp chat
- Open any chat in WhatsApp
- Tap **⋮ More options → Export chat → Without media**
- Save the `.txt` file
- Upload it in the app sidebar

---

## 📁 Project Structure

```
whatsapp_analyzer/
│
├── app.py                   # Main Streamlit application
├── preprocessor.py          # Chat file parsing (Android + iPhone)
├── stats.py                 # Basic & user statistics
├── timeline.py              # Monthly & daily timeline charts
├── activity.py              # Day/hour activity analysis + heatmap
├── words.py                 # Word frequency, word cloud, emoji
├── sentiment.py             # VADER / TextBlob sentiment analysis
├── report.py                # HTML report generator
├── generate_sample_chat.py  # Test data generator
└── requirements.txt
```

---

## ✨ Features

| Section | What you get |
|---|---|
| **Basic Stats** | Messages, words, media, links |
| **User Analysis** | Most active users, share % |
| **Timeline** | Monthly + daily message trends |
| **Activity** | Busiest day/hour + day×hour heatmap |
| **Words** | Top-20 words, word cloud |
| **Emoji** | Top emoji used with frequency chart |
| **Sentiment** | Positive / Neutral / Negative distribution + trend |
| **Download** | HTML report + raw CSV export |

---

## 🧪 Testing with Sample Data

```bash
python generate_sample_chat.py
# Creates sample_chat.txt → upload this in the app
```

---

## 📦 Dependencies

- **streamlit** — interactive web UI
- **pandas** — data processing
- **matplotlib / seaborn** — charts & heatmaps
- **wordcloud** — word cloud visualisation
- **emoji** — emoji extraction
- **vaderSentiment** — social-media-tuned sentiment analysis
- **textblob** — fallback sentiment analysis

---

## 📱 Supported Chat Formats

| Platform | Format example |
|---|---|
| Android | `12/31/23, 11:59 PM - User: Message` |
| iPhone  | `[31/12/23, 11:59:00 PM] User: Message` |

Multi-line messages and media-omitted markers are handled automatically.

---

## 💡 Tips

- For group chats, use the **Select user** dropdown to filter by individual.
- The **HTML Report** is fully self-contained and can be shared or printed.
- Run `generate_sample_chat.py` to create test data without needing a real export.
