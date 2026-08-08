import api from './api';

/**
 * Palm analysis service — uses the shared `api` axios instance
 * which automatically injects Authorization: Bearer <token> on every request.
 */
const palmService = {
  /**
   * Upload a palm image for analysis.
   * Backend: POST /palm/analyze
   */
  analyzePalm: async (imageFile) => {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    const formData = new FormData();

    formData.append('file', imageFile);

    const response = await api.post(
      '/palm/analyze',
      formData,
      {
        headers: {
          Authorization: token ? `Bearer ${token}` : undefined,
        },
      }
    );

    console.log('API response:', response);
    console.log('API response data:', response.data);

    return response.data;
  },

  /**
   * Fetch the logged-in user's palm history, newest first.
   * Backend: GET /palm/history  → returns a flat list (array)
   */
  getHistory: async () => {
    const response = await api.get('/palm/history');
    return Array.isArray(response.data) ? response.data : response.data.analyses ?? [];
  },

  /**
   * Fetch a single palm analysis by ID.
   * Backend: GET /palm/analyses/{analysis_id}
   */
  getAnalysisById: async (analysisId) => {
    const response = await api.get(`/palm/analyses/${analysisId}`);
    return response.data;
  },

  /**
   * Delete a palm analysis by ID.
   * Backend: DELETE /palm/analyses/{analysis_id}
   */
  deleteAnalysis: async (analysisId) => {
    const response = await api.delete(`/palm/analyses/${analysisId}`);
    return response.data;
  },

  /**
   * Generate AI interpretation for an existing palm analysis.
   * Backend: POST /reports/{analysis_id}
   */
  generateInterpretation: async (analysisId) => {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    const response = await api.post(
      `/reports/${analysisId}`,
      null,
      {
        headers: {
          Authorization: token ? `Bearer ${token}` : undefined,
        },
      }
    );

    return response.data;
  },

  /**
   * Download generated personality report PDF for an analysis.
   * Backend: GET /pdf/{analysis_id}
   * Returns: Blob (PDF)
   */
  downloadReportPdf: async (analysisId) => {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    const response = await api.get(
      `/pdf/${analysisId}`,
      {
        responseType: 'blob',
        headers: {
          Authorization: token ? `Bearer ${token}` : undefined,
        },
      }
    );

    return response.data;
  },
};

export default palmService;

