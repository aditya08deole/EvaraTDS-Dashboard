import axios from 'axios';

// ThingSpeak Configuration - Simplified and Optimized
const THINGSPEAK_CHANNEL_ID = '2713286';
const THINGSPEAK_READ_KEY = 'EHEK3A1XD48TY98B';
const THINGSPEAK_API = `https://api.thingspeak.com/channels/${THINGSPEAK_CHANNEL_ID}/feeds.json`;

// Optimized: Fetch live data with reduced payload
export const getDashboardData = async () => {
  try {
    const response = await axios.get(THINGSPEAK_API, {
      params: {
        api_key: THINGSPEAK_READ_KEY,
        results: 60 // Last 60 readings
      },
      timeout: 5000 // 5 second timeout for reliability
    });

    const feeds = response.data.feeds || [];
    if (feeds.length === 0) return null;

    const latest = feeds[feeds.length - 1];
    const tdsValue = parseFloat(latest.field2) || 0;
    
    return {
      latest: {
        tds: tdsValue,
        temp: parseFloat(latest.field3) || 0,
        voltage: parseFloat(latest.field1) || 0,
        created_at: latest.created_at
      },
      history: feeds.map((feed: any) => ({
        created_at: feed.created_at,
        tds: parseFloat(feed.field2) || 0,
        temp: parseFloat(feed.field3) || 0
      })),
      system_status: tdsValue > 150 ? 'CRITICAL' : 'NORMAL',
      last_updated: latest.created_at,
      channel_info: response.data.channel
    };
  } catch (error) {
    console.error("ThingSpeak Error:", error);
    return null;
  }
};