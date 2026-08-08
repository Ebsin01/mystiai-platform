import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import palmService from '../services/palmService';

/**
 * PalmAnalysisHistory
 * Fetches the logged-in user's palm readings from GET /palm/history.
 * Token is injected automatically via the axios interceptor in api.js.
 */
const PalmAnalysisHistory = () => {
  const navigate = useNavigate();

  const [analyses, setAnalyses]         = useState([]);
  const [loading, setLoading]           = useState(true);
  const [error, setError]               = useState('');

  // Confirmation dialog state
  const [confirmId, setConfirmId]       = useState(null);   // ID pending deletion
  const [deleting, setDeleting]         = useState(false);
  const [deleteError, setDeleteError]   = useState('');

  // ── Fetch history ────────────────────────────────────────────────────────────
  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await palmService.getHistory();
      setAnalyses(data);
    } catch (err) {
      console.error('Failed to load palm history:', err);
      if (err.response?.status === 401) {
        authService.logout();
        navigate('/login');
        return;
      }
      setError(
        err.response?.data?.detail ||
          'Failed to load palm history. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  // ── Delete flow ───────────────────────────────────────────────────────────────
  const handleDeleteConfirm = async () => {
    if (!confirmId) return;
    setDeleting(true);
    setDeleteError('');
    try {
      await palmService.deleteAnalysis(confirmId);
      setAnalyses((prev) => prev.filter((a) => a.id !== confirmId));
      setConfirmId(null);
    } catch (err) {
      setDeleteError(
        err.response?.data?.detail || 'Failed to delete analysis. Please try again.'
      );
    } finally {
      setDeleting(false);
    }
  };

  // ── Helpers ───────────────────────────────────────────────────────────────────
  const formatDate = (iso) => {
    if (!iso) return 'N/A';
    return new Date(iso).toLocaleString(undefined, {
      year: 'numeric', month: 'short', day: '2-digit',
      hour: '2-digit', minute: '2-digit',
    });
  };

  const fmt = (val) =>
    val !== null && val !== undefined ? Number(val).toFixed(4) : 'N/A';

  // ── Loading ───────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="auth-page-container">
        <div className="mystic-card loading-card">
          <div className="mystic-spinner"></div>
          <p>Reading the lines of your past analyses...</p>
        </div>
      </div>
    );
  }

  // ── Render ────────────────────────────────────────────────────────────────────
  return (
    <div className="history-page-container">

      {/* ── Page Header ── */}
      <div className="history-header">
        <div className="history-header-icon">✋</div>
        <h1 className="history-title">Palm Analysis History</h1>
        <p className="subtitle">Your saved palmistry readings from the AI oracle</p>
      </div>

      {/* ── Fetch Error ── */}
      {error && (
        <div className="alert alert-danger history-alert">
          <span>{error}</span>
          <button className="btn btn-secondary history-retry-btn" onClick={fetchHistory}>
            Retry
          </button>
        </div>
      )}

      {/* ── Empty State ── */}
      {!error && analyses.length === 0 && (
        <div className="mystic-card history-empty-card">
          <div className="history-empty-icon">🔮</div>
          <h3>No Palm Analyses Found</h3>
          <p className="subtitle">
            Submit your first palm image to begin building your reading history.
          </p>
        </div>
      )}

      {/* ── Cards Grid ── */}
      {!error && analyses.length > 0 && (
        <>
          <p className="history-count-label">
            {analyses.length} reading{analyses.length !== 1 ? 's' : ''} on record
          </p>

          <div className="history-grid">
            {analyses.map((analysis) => (
              <div key={analysis.id} className="history-card mystic-card">

                {/* Card top row: ID badge + date */}
                <div className="history-card-top">
                  <span className="history-id-badge">#{analysis.id}</span>
                  <span className="history-date">{formatDate(analysis.created_at)}</span>
                </div>

                {/* Image filename */}
                <div className="history-filename">
                  <span className="detail-label">Image File</span>
                  <span className="history-filename-value">
                    {analysis.image_filename || 'N/A'}
                  </span>
                </div>

                {/* 2×2 measurement grid */}
                <div className="history-metrics">
                  <div className="history-metric">
                    <span className="metric-label">Palm Width</span>
                    <span className="metric-value">{fmt(analysis.palm_width)}</span>
                  </div>
                  <div className="history-metric">
                    <span className="metric-label">Palm Length</span>
                    <span className="metric-value">{fmt(analysis.palm_length)}</span>
                  </div>
                  <div className="history-metric">
                    <span className="metric-label">Index Finger</span>
                    <span className="metric-value">{fmt(analysis.index_finger_length)}</span>
                  </div>
                  <div className="history-metric">
                    <span className="metric-label">Middle Finger</span>
                    <span className="metric-value">{fmt(analysis.middle_finger_length)}</span>
                  </div>
                </div>

                {/* Action buttons */}
                <div className="history-card-actions">
                  <button
                    id={`view-details-${analysis.id}`}
                    className="btn btn-primary history-action-btn"
                    onClick={() => navigate(`/palm-analysis/${analysis.id}`)}
                  >
                    View Details
                  </button>
                  <button
                    id={`delete-analysis-${analysis.id}`}
                    className="btn btn-danger history-action-btn"
                    onClick={() => { setConfirmId(analysis.id); setDeleteError(''); }}
                  >
                    Delete
                  </button>
                </div>

              </div>
            ))}
          </div>
        </>
      )}

      {/* ── Delete Confirmation Dialog ── */}
      {confirmId !== null && (
        <div
          className="history-modal-overlay"
          onClick={() => !deleting && setConfirmId(null)}
          role="dialog"
          aria-modal="true"
          aria-label="Confirm deletion"
        >
          <div
            className="history-modal confirm-dialog"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="confirm-icon">⚠️</div>
            <h2 className="confirm-title">Delete Analysis #{confirmId}?</h2>
            <p className="confirm-body">
              This will permanently remove this palm reading from your history.
              This action <strong>cannot be undone</strong>.
            </p>

            {deleteError && (
              <div className="alert alert-danger">{deleteError}</div>
            )}

            <div className="confirm-actions">
              <button
                id="cancel-delete-btn"
                className="btn btn-secondary"
                onClick={() => setConfirmId(null)}
                disabled={deleting}
              >
                Cancel
              </button>
              <button
                id="confirm-delete-btn"
                className="btn btn-danger"
                onClick={handleDeleteConfirm}
                disabled={deleting}
              >
                {deleting ? 'Deleting…' : 'Yes, Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default PalmAnalysisHistory;
