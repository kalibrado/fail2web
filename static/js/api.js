// =====================================================
// static/js/api.js
// Gestion des appels API
// =====================================================

class API {
  static async get(endpoint) {
    try {
      const response = await fetch(`${CONFIG.API_URL}${endpoint}`);
      if (!response.ok) throw new Error(CONFIG.TRANSLATIONS.network_error || 'Network error');
      return await response.json();
    } catch (error) {
      console.error('API GET Error:', error);
      throw error;
    }
  }

  static async post(endpoint, data) {
    try {
      const response = await fetch(`${CONFIG.API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || CONFIG.TRANSLATIONS.error_unknown || 'Unknown error');
      }
      return await response.json();
    } catch (error) {
      console.error('API POST Error:', error);
      throw error;
    }
  }

  static async patch(endpoint, data) {
    try {
      const response = await fetch(`${CONFIG.API_URL}${endpoint}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || CONFIG.TRANSLATIONS.error_unknown || 'Unknown error');
      }
      return await response.json();
    } catch (error) {
      console.error('API PATCH Error:', error);
      throw error;
    }
  }
}

