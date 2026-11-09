"""
Run this ONCE on your PC to generate a session string.
Copy the printed string and save it as TELEGRAM_SESSION in Railway env vars.
"""
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID   = 38143190
API_HASH = "0f960cc824ec349169a29747bddabeee"

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.start()
    session_string = client.session.save()

    # Save to file so it's never lost
    with open("session.txt", "w") as f:
        f.write(session_string)

    print("\n" + "="*60)
    print("YOUR SESSION STRING (also saved to session.txt):")
    print("="*60)
    print(session_string)
    print("="*60)
    print("\nSession saved to session.txt — you can close this window.")
    await client.disconnect()
    input("\nPress Enter to close...")

asyncio.run(main())
