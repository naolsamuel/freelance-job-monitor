"""
Telegram Job Filter Bot
========================
Monitors t.me/freelance_ethio and forwards matching jobs to @Dsambill3

Profile: Naol Samuel — Front-End Web Developer / CS Student
         Also looking for: Video Editing gigs

Run:
    python bot.py

First run will ask for your phone number + OTP to log in.
Session is saved so you won't be asked again.
"""

import asyncio
import re
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ─── CONFIG — loaded from environment variables (never hardcoded) ─────────────
API_ID         = int(os.environ["TELEGRAM_API_ID"])
API_HASH       = os.environ["TELEGRAM_API_HASH"]
SESSION_STRING = os.environ["TELEGRAM_SESSION"]   # generated once via gen_session.py

TARGET_CHANNEL = "freelance_ethio"
MY_USERNAME    = "Dsambill3"

# ─── FILTER KEYWORDS ─────────────────────────────────────────────────────────
# Keywords extracted from Naol's resume + video editing interest
RESUME_KEYWORDS = [
    # Web / Front-End
    "html", "css", "javascript", "js", "frontend", "front-end", "front end",
    "web developer", "web development", "web design", "ui", "ux", "ui/ux",
    "responsive", "dom", "react", "vue", "angular", "typescript",
    "git", "github", "node", "rest api", "api",
    # General dev
    "software developer", "software engineer", "full stack", "fullstack",
    "computer science", "programmer", "coding", "developer", "intern",
    "junior developer", "trainee",
    # Video editing (always include)
    "video edit", "video editing", "video editor", "video production",
    "premiere", "after effects", "davinci", "capcut", "final cut",
    "motion graphics", "animation", "youtube", "content creator",
    "reels", "shorts", "tiktok edit", "subtitles", "color grading",
    "videography", "multimedia", "motion",
]

# Scoring: how many keyword matches needed to forward the post
MIN_SCORE = 1

# ─────────────────────────────────────────────────────────────────────────────

def score_message(text: str) -> tuple[int, list[str]]:
    """Return (match_count, matched_keywords) for a job post."""
    text_lower = text.lower()
    matched = [kw for kw in RESUME_KEYWORDS if kw in text_lower]
    return len(matched), matched


def format_notification(original_text: str, matched: list[str], channel: str) -> str:
    """Format the DM notification message."""
    preview = original_text[:600].strip()
    tags = ", ".join(f"`{m}`" for m in matched[:8])
    return (
        f"🎯 **New Matching Job from @{channel}**\n\n"
        f"{preview}{'...' if len(original_text) > 600 else ''}\n\n"
        f"──────────────────\n"
        f"✅ Matched: {tags}"
    )


async def main():
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()

    # Resolve our own user to send DMs
    me = await client.get_entity(MY_USERNAME)
    print(f"✅ Logged in. Will forward matches to @{MY_USERNAME}")

    # Resolve target channel
    channel = await client.get_entity(TARGET_CHANNEL)
    print(f"✅ Monitoring: t.me/{TARGET_CHANNEL}")
    print(f"🔍 Watching for {len(RESUME_KEYWORDS)} keywords…\n")

    @client.on(events.NewMessage(chats=channel))
    async def handler(event):
        text = event.message.message or ""
        if not text.strip():
            return

        score, matched = score_message(text)
        if score >= MIN_SCORE:
            notification = format_notification(text, matched, TARGET_CHANNEL)
            await client.send_message(me, notification, parse_mode="md")
            print(f"📨 Forwarded job post (score={score}, matched={matched[:4]})")
        else:
            print(f"⏭  Skipped post (score={score})")

    print("🤖 Bot running — press Ctrl+C to stop\n")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
