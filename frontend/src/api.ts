import axios from 'axios';

// Direct ThingSpeak Integration for Ultra-Fast Real-Time Data
const THINGSPEAK_CHANNEL_ID = '2713286';
const THINGSPEAK_READ_KEY = 'EHEK3A1XD48TY98B';
const THINGSPEAK_API = `https://api.thingspeak.com/channels/${THINGSPEAK_CHANNEL_ID}/feeds.json`;

// Fetch live data directly from ThingSpeak - Ultra-fast, no backend dependency
export const getDashboardData = async () => {
  try {
    const response = await axios.get(THINGSPEAK_API, {
      params: {
        api_key: THINGSPEAK_READ_KEY,
        results: 60 // Last 60 readings for charts
      }
    });

    const feeds = response.data.feeds || [];
    
    if (feeds.length === 0) {
      return null;
    }

    // Get latest reading
    const latest = feeds[feeds.length - 1];
    
    // Transform data for dashboard
    const latestData = {
      tds: parseFloat(latest.field2) || 0,
      temp: parseFloat(latest.field3) || 0,
      voltage: parseFloat(latest.field1) || 0,
      created_at: latest.created_at
    };

    // Transform history for charts
    const history = feeds.map((feed: any) => ({
      created_at: feed.created_at,
      entry_id: feed.entry_id,
      voltage: parseFloat(feed.field1) || 0,
      tds: parseFloat(feed.field2) || 0,
      temp: parseFloat(feed.field3) || 0
    }));

    // Determine system status
    const tdsValue = latestData.tds;
    let system_status = 'NORMAL';
    if (tdsValue > 150) {
      system_status = 'CRITICAL';
    } else if (tdsValue > 120) {
      system_status = 'WARNING';
    }

    return {
      latest: latestData,
      history: history,
      system_status: system_status,
      last_updated: latest.created_at,
      channel_info: response.data.channel
    };
  } catch (error) {
    console.error("ThingSpeak API Error:", error);
    return null;
  }
};