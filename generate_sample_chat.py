"""
generate_sample_chat.py
-----------------------
Generates a sample WhatsApp Android-format chat file for testing.
Run:  python generate_sample_chat.py
"""

import random
from datetime import datetime, timedelta

USERS = ["Alice", "Bob", "Charlie", "Diana"]

MESSAGES = [
    "Hey everyone! How's it going?",
    "Did you see the game last night? Incredible!",
    "I'm running a bit late, sorry 😅",
    "Can we reschedule for tomorrow?",
    "That's absolutely amazing! 🎉",
    "I totally agree with you on that.",
    "Not sure about this, seems risky.",
    "Let's meet at the usual place.",
    "Check out this article: https://example.com/news",
    "Haha that's so funny 😂😂",
    "Good morning everyone ☀️",
    "Anyone up for coffee later?",
    "I just finished the project!",
    "This is taking forever honestly.",
    "Love you all ❤️",
    "What time works for everyone?",
    "I disagree, this doesn't seem right.",
    "Wow, I didn't expect that at all!",
    "Happy birthday! 🎂🎉",
    "That made my day, thank you!",
    "When is the deadline again?",
    "I'm so tired today 😴",
    "Let's do this! 💪",
    "Terrible weather today ugh",
    "Just saw the news, unbelievable.",
    "<Media omitted>",
    "Thanks for sharing!",
    "No worries at all.",
    "Sounds good to me 👍",
    "I'll be there in 10 minutes.",
]

def generate(output_path: str = "sample_chat.txt", num_messages: int = 500):
    start = datetime(2023, 1, 1, 8, 0, 0)
    lines = []

    for i in range(num_messages):
        dt = start + timedelta(minutes=random.randint(1, 180))
        start = dt
        user = random.choice(USERS)
        msg  = random.choice(MESSAGES)
        timestamp = dt.strftime("%-m/%-d/%y, %I:%M %p")
        lines.append(f"{timestamp} - {user}: {msg}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Sample chat written to {output_path} ({num_messages} messages)")

if __name__ == "__main__":
    generate()
