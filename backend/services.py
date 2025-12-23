import httpx
import os
from datetime import datetime

# Configuration
CHANNEL_ID = os.getenv("THINGSPEAK_CHANNEL_ID", "2713286")
THINGSPEAK_URL = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json"

async def fetch_evara_data(results: int = 60):
    """
    Fetches the last 'results' entries from ThingSpeak.
    Processes them for the dashboard.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Fetch last N entries
            response = await client.get(f"{THINGSPEAK_URL}?results={results}")
            data = response.json()
            
            feeds = data.get('feeds', [])
            processed_feeds = []

            for feed in feeds:
                # Parse data safely
                try:
                    tds = float(feed.get('field2', 0) or 0)
                    temp = float(feed.get('field3', 0) or 0)
                    voltage = float(feed.get('field1', 0) or 0)
                    timestamp = feed.get('created_at')
                except ValueError:
                    continue # Skip corrupt frames

                processed_feeds.append({
                    "created_at": timestamp,
                    "tds": tds,
                    "temp": temp,
                    "voltage": voltage
                })

            # Get Latest Reading for Status
            latest = processed_feeds[-1] if processed_feeds else None
            
            # Analyze for Alerts (TDS > 150)
            system_status = "NORMAL"
            if latest and latest['tds'] > 150:
                system_status = "CRITICAL_HIGH_TDS"

            return {
                "channel_info": data.get('channel', {}),
                "latest": latest,
                "history": processed_feeds,
                "status": system_status
            }

        except Exception as e:
            print(f"Error fetching ThingSpeak: {e}")
            return {"error": "Failed to fetch data"}