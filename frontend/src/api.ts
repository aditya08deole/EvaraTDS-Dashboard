import axios from 'axios';

// Ensure this matches your backend URL (default FastAPI port is 8000)
const API_URL = 'http://localhost:8000';

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