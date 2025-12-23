import axios from 'axios';

// Use environment variable for API URL, fallback to relative path for Vercel deployment
const API_URL = import.meta.env.VITE_API_URL || '';

// Use the v1 API prefix from backend settings
export const getDashboardData = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/v1/dashboard`);
    return response.data;
  } catch (error) {
    console.error("API Error", error);
    return null;
  }
};