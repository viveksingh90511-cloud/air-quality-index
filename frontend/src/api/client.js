const getBaseURL = () => {
  const url = import.meta.env.VITE_API_URL;
  if (!url) return 'http://localhost:8000/api';
  return url.endsWith('/api') ? url : `${url}/api`;
};

const API_BASE_URL = getBaseURL();


export const apiClient = {
  async get(endpoint) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) throw new Error(`API error: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`GET ${endpoint} failed:`, error);
      throw error;
    }
  },

  async post(endpoint, data) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`API error: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`POST ${endpoint} failed:`, error);
      throw error;
    }
  }
};

export const endpoints = {
  realtime: '/realtime',
  forecast: '/predict-aqi',
  healthRisk: '/health-risk',
  chat: '/chat',
  stations: '/stations'
};
