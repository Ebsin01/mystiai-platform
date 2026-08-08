import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import authService from '../services/authService';

const positionOrder = [
  { key: 'past', label: 'Past Card' },
  { key: 'present', label: 'Present Card' },
  { key: 'future', label: 'Future Card' },
];

const ThreeCardHistory = () => {
  const navigate = useNavigate();
  const [readings, setReadings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const formatDateTime = (value) => {
    if (!value) return 'Unknown';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleString([], {
      dateStyle: 'medium',
      timeStyle: 'short',
    });
  };

  const fetchHistory = async () => {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');

    if (!token) {
      setReadings([]);
      setError('');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.get('http://127.0.0.1:8000/tarot/three-card-readings', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const rawReadings = Array.isArray(response?.data?.readings) ? response.data.readings : [];

      const groupedReadings = rawReadings.reduce((acc, item) => {
        const questionText = item.question?.trim() || 'Untitled Question';
        const createdAt = item.created_at || '';
        const groupKey = `${questionText}::${createdAt}`;

        if (!acc[groupKey]) {
          acc[groupKey] = {
            question: questionText,
            createdAt,
            cards: {},
          };
        }

        const normalizedPosition = (item.position || '').toLowerCase();
        acc[groupKey].cards[normalizedPosition] = item;
        return acc;
      }, {});

      const groupedArray = Object.values(groupedReadings)
        .map((group) => ({
          ...group,
          cards: positionOrder
            .map(({ key }) => group.cards[key])
            .filter(Boolean),
        }))
        .sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0));

      setReadings(groupedArray);
    } catch (err) {
      console.error('Failed to load three-card history:', err);

      if (err.response?.status === 401) {
        authService.logout();
        navigate('/login');
        return;
      }

      setError(err.response?.data?.detail || 'Unable to load your three-card readings right now.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [navigate]);

  if (loading) {
    return (
      <div className="auth-page-container">
        <div className="mystic-card loading-card">
          <div className="mystic-spinner"></div>
          <p>Gathering your three-card reading history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="history-page-container">
      <div className="history-header">
        <div className="history-header-icon">🎴</div>
        <h1 className="history-title">Three Card Reading History</h1>
        <p className="subtitle">Your past, present, and future spreads in one place</p>
      </div>

      {error && (
        <div className="alert alert-danger history-alert">
          <span>{error}</span>
          <button className="btn btn-secondary history-retry-btn" onClick={fetchHistory}>
            Retry
          </button>
        </div>
      )}

      {!error && readings.length === 0 && (
        <div className="mystic-card history-empty-card">
          <div className="history-empty-icon">🔮</div>
          <h3>No Three Card Readings Found</h3>
          <p className="subtitle">Your saved spreads will appear here once you draw a three-card reading.</p>
        </div>
      )}

      {!error && readings.length > 0 && (
        <div className="three-card-history-grid">
          {readings.map((group, index) => (
            <article key={`${group.question}-${group.createdAt}-${index}`} className="mystic-card three-card-history-card">
              <div className="three-card-history-card-top">
                <div>
                  <h3 className="three-card-history-question">{group.question}</h3>
                  <p className="three-card-history-date">{formatDateTime(group.createdAt)}</p>
                </div>
                <span className="history-id-badge">#{index + 1}</span>
              </div>

              <div className="three-card-history-stack">
                {positionOrder.map(({ key, label }) => {
                  const card = group.cards.find((item) => (item.position || '').toLowerCase() === key);
                  if (!card) return null;

                  return (
                    <div key={`${group.question}-${key}`} className="three-card-history-position-card">
                      <div className="three-card-history-position-label">{label}</div>
                      <h4 className="three-card-history-card-name">{card.card_name || 'Unknown Card'}</h4>
                      <div className="three-card-history-meta-grid">
                        <div className="three-card-history-meta-item">
                          <span>Arcana</span>
                          <strong>{card.arcana || 'N/A'}</strong>
                        </div>
                        <div className="three-card-history-meta-item">
                          <span>Suit</span>
                          <strong>{card.suit || 'N/A'}</strong>
                        </div>
                        <div className="three-card-history-meta-item">
                          <span>Orientation</span>
                          <strong>{card.orientation || 'N/A'}</strong>
                        </div>
                      </div>
                      <div className="three-card-history-meaning">
                        <span>Meaning</span>
                        <p>{card.meaning || 'No meaning provided.'}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
};

export default ThreeCardHistory;
