import api from './api';

/**
 * Tarot service — handles interaction with backend tarot APIs.
 */
const tarotService = {
  /**
   * Fetch all tarot cards.
   * Backend: GET /tarot/cards
   */
  getTarotCards: async () => {
    const response = await api.get('/tarot/cards');
    return response.data;
  },

  /**
   * Generate a three-card tarot reading.
   * Backend: POST /tarot/three-card-reading
   */
  generateThreeCardReading: async (question, cardIds = []) => {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    const payload = { question };
    if (Array.isArray(cardIds) && cardIds.length > 0) {
      payload.card_ids = cardIds;
      payload.cards = cardIds;
    }
    const response = await api.post(
      '/tarot/three-card-reading',
      payload,
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
