#!/usr/bin/env python3
"""
Get Telegram Group Chat ID
Run this after adding the bot to your group and sending a message
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env file")
    print("   Please add your bot token to backend/.env")
    exit(1)

print("🔍 Fetching recent updates from Telegram...")
print()

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url)

if response.status_code != 200:
    print(f"❌ Error: Failed to fetch updates (status {response.status_code})")
    print(f"   Response: {response.text}")
    exit(1)

data = response.json()

if not data.get("ok"):
    print("❌ Error: Telegram API returned an error")
    print(f"   Response: {data}")
    exit(1)

results = data.get("result", [])

if not results:
    print("⚠️  No updates found. Please:")
    print("   1. Add @EvaraTDS_bot to your Telegram group")
    print("   2. Send any message in the group")
    print("   3. Run this script again")
    exit(0)

print("✅ Found updates! Here are the chats:")
print()

seen_chats = {}

for update in results:
    message = update.get("message", {})
    chat = message.get("chat", {})
    
    chat_id = chat.get("id")
    chat_title = chat.get("title", "Private Chat")
    chat_type = chat.get("type", "unknown")
    
    if chat_id and chat_id not in seen_chats:
        seen_chats[chat_id] = {
            "title": chat_title,
            "type": chat_type
        }

if not seen_chats:
    print("⚠️  No chat information found in updates")
    exit(0)

print("=" * 60)
for chat_id, info in seen_chats.items():
    icon = "👥" if info["type"] in ["group", "supergroup"] else "👤"
    print(f"{icon} Chat: {info['title']}")
    print(f"   Type: {info['type']}")
    print(f"   Chat ID: {chat_id}")
    
    if info["type"] in ["group", "supergroup"]:
        print()
        print("   ✨ For your .env file, add:")
        print(f"   TELEGRAM_GROUP_CHAT_ID={chat_id}")
        print()
        print("   ✨ For Vercel, run:")
        print(f"   vercel env add TELEGRAM_GROUP_CHAT_ID")
        print(f"   Then enter: {chat_id}")
    
    print("=" * 60)

print()
print("💡 Tips:")
print("   • Group chat IDs are negative numbers")
print("   • Personal chat IDs are positive numbers")
print("   • Use group chat ID for broadcasting alerts to all members")
print()
