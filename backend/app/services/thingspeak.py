import httpx
from app.core.config import settings

THINGSPEAK_URL = f"https://api.thingspeak.com/channels/{settings.THINGSPEAK_CHANNEL_ID}/feeds.json"

async def fetch_evara_data(results: int = 60):
    """
    Fetches raw data from ThingSpeak and normalizes it.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{THINGSPEAK_URL}?results={results}&api_key={settings.THINGSPEAK_READ_KEY}")

            if response.status_code != 200:
                return {"error": f"ThingSpeak API Error: {response.status_code}"}

            data = response.json()
            feeds = data.get('feeds', [])

            cleaned_history = []

            for feed in feeds:
                try:
                    cleaned_history.append({
                        "created_at": feed.get("created_at"),
                        "entry_id": feed.get("entry_id"),
                        "voltage": float(feed.get("field1") or 0),
                        "tds": float(feed.get("field2") or 0),
                        "temp": float(feed.get("field3") or 0)
                    })
                except (ValueError, TypeError):
                    continue

            return {
                "latest": cleaned_history[-1] if cleaned_history else None,
                "history": cleaned_history
            }

        except httpx.RequestError as e:
            print(f"Network Error: {e}")
            return {"error": "Connection to ThingSpeak failed"}
