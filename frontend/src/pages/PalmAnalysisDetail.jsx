import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import palmService from '../services/palmService';

/**
 * PalmAnalysisDetail
 * Shows the full detail of a single palm analysis, including all 21 landmarks.
 * Route: /palm-analysis/:analysis_id
 * API:   GET /palm/analyses/{analysis_id}  (JWT injected automatically)
 */
const PalmAnalysisDetail = () => {
  const { analysis_id } = useParams();
  const navigate = useNavigate();

  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState('');

  // ── Fetch single analysis ─────────────────────────────────────────────────────
  useEffect(() => {
    const fetchDetail = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await palmService.getAnalysisById(analysis_id);
        setAnalysis(data);
      } catch (err) {
        console.error('Failed to load analysis detail:', err);
        if (err.response?.status === 401) {
          authService.logout();
          navigate('/login');
          return;
        }
        if (err.response?.status === 404) {
          setError('Palm analysis not found or does not belong to your account.');
        } else {
          setError(
            err.response?.data?.detail || 'Failed to load analysis details.'
          );
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDetail();
  }, [analysis_id, navigate]);

  // ── Helpers ────────────────────────────────────────────────────────────────────
  const formatDate = (iso) => {
    if (!iso) return 'N/A';
    return new Date(iso).toLocaleString(undefined, {
      weekday: 'long', year: 'numeric', month: 'long',
      day: '2-digit', hour: '2-digit', minute: '2-digit',
    });
  };

  const fmt = (val) =>
    val !== null && val !== undefined ? Number(val).toFixed(4) : 'N/A';

  // ── Loading ────────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="auth-page-container">
        <div className="mystic-card loading-card">
          <div className="mystic-spinner"></div>
          <p>Decoding your palm lines...</p>
        </div>
      </div>
    );
  }

  // ── Error ──────────────────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="auth-page-container">
        <div className="mystic-card detail-error-card">
          <div className="detail-error-icon">🔮</div>
          <h2>Unable to Load Reading</h2>
          <div className="alert alert-danger">{error}</div>
          <button
            id="back-to-history-btn"
            className="btn btn-secondary"
            onClick={() => navigate('/palm-history')}
          >
            ← Back to History
          </button>
        </div>
      </div>
    );
  }

  // ── Render ─────────────────────────────────────────────────────────────────────
  const landmarks = analysis?.landmarks ?? [];

  return (
    <div className="detail-page-container">

      {/* ── Back navigation ── */}
      <button
        id="back-btn"
        className="btn btn-secondary detail-back-btn"
        onClick={() => navigate('/palm-history')}
      >
        ← Back to History
      </button>

      {/* ── Page header ── */}
      <div className="detail-header">
        <div className="detail-header-icon">✋</div>
        <div>
          <h1 className="detail-title">Palm Reading Details</h1>
        </div>
      </div>

      {/* ── Analysis Information ── */}
      <div className="mystic-card detail-card">
        <h2 className="detail-section-title">ℹ️ Analysis Information</h2>
        <div className="detail-measurements-grid">
          <div className="detail-stat">
            <span className="detail-stat-label">Analysis ID</span>
            <span className="detail-stat-value id-badge">#{analysis.id}</span>
          </div>
          <div className="detail-stat">
            <span className="detail-stat-label">Image File</span>
            <span className="detail-stat-value filename-value">
              {analysis.image_filename || 'N/A'}
            </span>
          </div>
          <div className="detail-stat">
            <span className="detail-stat-label">Created Date & Time</span>
            <span className="detail-stat-value">{formatDate(analysis.created_at)}</span>
          </div>
        </div>
      </div>

      {/* ── Palm Measurements ── */}
      <div className="mystic-card detail-card">
        <h2 className="detail-section-title">📐 Palm Measurements</h2>
        <div className="detail-measurements-grid">
          <div className="detail-stat">
            <span className="detail-stat-label">Palm Width</span>
            <span className="detail-stat-value metric-value">{fmt(analysis.palm_width)}</span>
          </div>
          <div className="detail-stat">
            <span className="detail-stat-label">Palm Length</span>
            <span className="detail-stat-value metric-value">{fmt(analysis.palm_length)}</span>
          </div>
        </div>
      </div>

      {/* ── Finger Measurements ── */}
      <div className="mystic-card detail-card">
        <h2 className="detail-section-title">☝️ Finger Measurements</h2>
        <div className="detail-measurements-grid">
          <div className="detail-stat">
            <span className="detail-stat-label">Index Finger Length</span>
            <span className="detail-stat-value metric-value">{fmt(analysis.index_finger_length)}</span>
          </div>
          <div className="detail-stat">
            <span className="detail-stat-label">Middle Finger Length</span>
            <span className="detail-stat-value metric-value">{fmt(analysis.middle_finger_length)}</span>
          </div>
        </div>
      </div>

      {/* ── Landmarks card ── */}
      {landmarks.length > 0 && (
        <div className="mystic-card detail-card">
          <h2 className="detail-section-title">
            🖐 Hand Landmarks
            <span className="detail-landmark-count">{landmarks.length} points</span>
          </h2>

          <div className="landmarks-table-wrapper">
            <table className="landmarks-table">
              <thead>
                <tr>
                  <th>Point</th>
                  <th>X</th>
                  <th>Y</th>
                  <th>Z</th>
                </tr>
              </thead>
              <tbody>
                {landmarks.map((lm) => (
                  <tr key={lm.id}>
                    <td><span className="id-badge">{lm.id}</span></td>
                    <td>{lm.x}</td>
                    <td>{lm.y}</td>
                    <td>{lm.z}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {landmarks.length === 0 && (
        <div className="mystic-card detail-card detail-no-landmarks">
          <span>🤲</span>
          <p className="subtitle">No landmark data stored for this reading.</p>
        </div>
      )}

    </div>
  );
};

export default PalmAnalysisDetail;
