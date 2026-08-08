import api from './api';

/**
 * Tarot service — handles interaction with backend tarot APIs.
 */
const tarotService = {
  /**
   * Generate a three-card tarot reading.
   * Backend: POST /tarot/three-card-reading
   */
  generateThreeCardReading: async (question) => {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    const response = await api.post(
      '/tarot/three-card-reading',
      { question },
      {
        headers: {
          Authorization: token ? `Bearer ${token}` : undefined,
        },
      }
    );
    return response.data;
  },

  /**
   * Fetch the authenticated user's three-card reading history.
   * Backend: GET /tarot/three-card-readings
   */
  getThreeCardHistory: async () => {
    const response = await api.get('/tarot/three-card-readings');
    return response.data;
  },

  /**
   * Fetch a single three-card reading entry by ID.
   * Backend: GET /tarot/three-card-readings/{reading_id}
   */
  getThreeCardReadingDetail: async (readingId) => {
    const response = await api.get(`/tarot/three-card-readings/${readingId}`);
    return response.data;
  },
};

export default tarotService;
