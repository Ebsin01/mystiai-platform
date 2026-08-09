
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import tarotService from '../services/tarotService';
import authService from '../services/authService';
import { useNotification } from '../contexts/NotificationContext';



/**
 * TarotReading Component
 * Connects to the existing FastAPI three-card tarot endpoint.
 */
const TarotReading = () => {
  const navigate = useNavigate();
  const [question, setQuestion] = useState('What does my future look like?');
  const [reading, setReading] = useState(null);
  const [loading, setLoading] = useState(false);
  const { refreshUnreadCount } = useNotification();
  const [error, setError] = useState('');
  const [historyGroups, setHistoryGroups] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState('');
  const [expandedGroupKey, setExpandedGroupKey] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState('');
  const [detailEntry, setDetailEntry] = useState(null);

  const formatDateTime = (value) => {
    if (!value) return 'Unknown';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
  };

  const loadHistory = async () => {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    if (!token) {
      setHistoryGroups([]);
      setHistoryError('');
      return;
    }

    setHistoryLoading(true);
    setHistoryError('');

    try {
      const data = await tarotService.getThreeCardHistory();
      const rawReadings = Array.isArray(data?.readings) ? data.readings : [];

      const groupedByQuestion = rawReadings.reduce((acc, item) => {
        const questionText = item.question?.trim() || 'Untitled Question';
        if (!acc[questionText]) {
          acc[questionText] = {
            question: questionText,
            createdAt: item.created_at,
            cards: {},
            firstReadingId: item.id,
          };
        }

        const currentTime = item.created_at ? new Date(item.created_at).getTime() : 0;
        const storedTime = acc[questionText].createdAt ? new Date(acc[questionText].createdAt).getTime() : 0;
        if (currentTime > storedTime) {
          acc[questionText].createdAt = item.created_at;
        }

        acc[questionText].cards[item.position] = item;
        return acc;
      }, {});

      const groupedArray = Object.values(groupedByQuestion)
        .map((group) => ({
          ...group,
          groupKey: `${group.question}-${group.createdAt || 'unknown'}`,
          cards: ['Past', 'Present', 'Future']
            .map((position) => group.cards[position])
            .filter(Boolean),
        }))
        .sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0));

      setHistoryGroups(groupedArray);
    } catch (err) {
      console.error('Failed to load tarot history:', err);
      setHistoryError('Unable to load your reading history right now.');
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleGenerateReading = async (e) => {
    if (e) e.preventDefault();

    if (!question.trim()) {
      setError('Please enter a question for your reading.');
      return;
    }

    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    if (!token) {
      setError('Please log in to generate a tarot reading.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const data = await tarotService.generateThreeCardReading(question.trim());

      if (!data || !Array.isArray(data.cards) || data.cards.length === 0) {
        throw new Error('No cards were returned by the server.');
      }

      setReading(data);
      await loadHistory();
      refreshUnreadCount();
    } catch (err) {
      console.error('Failed to generate three-card reading:', err);

      if (err.response?.status === 401) {
        authService.logout();
        navigate('/login');
        return;
      }

      const errorDetail = err.response?.data?.detail;
      const responseMessage = err.response?.data?.message;

      if (typeof errorDetail === 'string') {
        setError(errorDetail);
      } else if (typeof responseMessage === 'string') {
        setError(responseMessage);
      } else if (err.message) {
        setError(`Error: ${err.message}`);
      } else {
        setError('Failed to generate the three-card reading. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (group) => {
    if (expandedGroupKey === group.groupKey) {
      setExpandedGroupKey(null);
      setDetailEntry(null);
      return;
    }

    setExpandedGroupKey(group.groupKey);
    setDetailError('');
    setDetailLoading(true);

    try {
      if (group.firstReadingId) {
        const detail = await tarotService.getThreeCardReadingDetail(group.firstReadingId);
        setDetailEntry(detail);
      } else {
        setDetailEntry(null);
      }
    } catch (err) {
      console.error('Failed to load tarot reading detail:', err);
      setDetailError('Unable to load the selected reading details right now.');
    } finally {
      setDetailLoading(false);
    }
  };

  const getCardAccent = (position) => {
    switch (position?.toLowerCase()) {
      case 'past':
        return { border: '1px solid rgba(255, 107, 107, 0.35)', background: 'linear-gradient(135deg, rgba(255,107,107,0.15), rgba(255,153,102,0.08))', shadow: '0 12px 30px rgba(255,107,107,0.15)' };
      case 'present':
        return { border: '1px solid rgba(46, 213, 115, 0.35)', background: 'linear-gradient(135deg, rgba(46,213,115,0.16), rgba(82, 183, 136, 0.08))', shadow: '0 12px 30px rgba(46,213,115,0.15)' };
      case 'future':
        return { border: '1px solid rgba(120, 119, 255, 0.35)', background: 'linear-gradient(135deg, rgba(120,119,255,0.16), rgba(138, 109, 255, 0.08))', shadow: '0 12px 30px rgba(120,119,255,0.16)' };
      default:
        return { border: '1px solid rgba(255,255,255,0.12)', background: 'rgba(255,255,255,0.04)', shadow: '0 8px 20px rgba(0,0,0,0.18)' };
    }
  };

  const personalityData = reading?.personality || {};
  const personalityStrengths = Array.isArray(personalityData?.strengths)
    ? personalityData.strengths.filter((item) => item && String(item).trim())
    : [];
  const personalityChallenges = Array.isArray(personalityData?.challenges)
    ? personalityData.challenges.filter((item) => item && String(item).trim())
    : [];
  const personalityAdvice = typeof personalityData?.advice === 'string' ? personalityData.advice : '';

  const lifeTrendsData = reading?.life_trends || {};
  const lifeTrendCards = [
    { key: 'career', label: 'Career', value: lifeTrendsData?.career || 'No trend data available yet.' },
    { key: 'love', label: 'Love', value: lifeTrendsData?.love || 'No trend data available yet.' },
    { key: 'finance', label: 'Finance', value: lifeTrendsData?.finance || 'No trend data available yet.' },
    { key: 'health', label: 'Health', value: lifeTrendsData?.health || 'No trend data available yet.' },
  ];

  const predictionCategory = reading?.predicted_category || 'Pending';
  const predictionConfidenceValue = Number(reading?.prediction_confidence);
  const predictionConfidence = Number.isFinite(predictionConfidenceValue)
    ? `${(predictionConfidenceValue * 100).toFixed(1)}%`
    : 'Pending';

  const recommendations = Array.isArray(reading?.recommendations)
    ? reading.recommendations.filter((item) => item && String(item).trim())
    : [];

  return (
    <div className="auth-page-container tarot-reading-shell w-full px-4 py-6 md:px-6 md:py-8">
      <div className="mystic-card tarot-page-card w-full max-w-6xl rounded-[24px] border border-white/10 bg-slate-950/70 p-6 shadow-2xl shadow-fuchsia-950/20 backdrop-blur-xl md:p-8">
        <div className="mystic-orb"></div>
        <div className="mb-6 text-center">
          <div className="mb-3 text-4xl md:text-5xl" style={{ animation: 'float 3s ease-in-out infinite' }}>🎴</div>
          <h1 className="history-title mb-2 text-2xl font-semibold md:text-3xl">Three-Card Tarot Reading</h1>
          <p className="subtitle text-sm md:text-base">Ask your question and receive guidance from the Past, Present, and Future.</p>
        </div>

        {error && (
          <div className="alert alert-danger mb-6 rounded-xl border border-rose-400/20 bg-rose-500/10 px-4 py-3 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleGenerateReading} className="mb-6 space-y-4">
          <label htmlFor="tarot-question" className="block text-sm font-semibold uppercase tracking-[0.2em] text-slate-300">
            Your Question
          </label>
          <input
            id="tarot-question"
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What does my future look like?"
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-100 shadow-inner outline-none transition focus:border-fuchsia-400 focus:bg-white/10"
          />

          <button
            type="submit"
            className="btn btn-primary w-full rounded-2xl px-4 py-3 text-base shadow-lg shadow-fuchsia-950/30"
            disabled={loading}
          >
            {loading ? (
              <div className="flex items-center justify-center gap-2">
                <span className="mystic-spinner" style={{ width: '20px', height: '20px', borderWidth: '2px', margin: 0 }}></span>
                <span>Generating your three-card reading...</span>
              </div>
            ) : (
              'Generate Three-Card Reading ✨'
            )}
          </button>
        </form>

        {loading && (
          <div className="py-8 text-center">
            <div className="relative mb-4 inline-flex">
              <div className="mystic-spinner" style={{ width: '34px', height: '34px', borderWidth: '3px' }}></div>
              <div className="absolute inset-0 rounded-full border border-white/15"></div>
            </div>
            <p className="text-sm text-amber-300">Shuffling the deck and drawing your spread...</p>
          </div>
        )}

        {!loading && reading && (
          <div className="tarot-result-shell mt-4 rounded-[20px] border border-white/10 bg-slate-900/60 p-4 shadow-lg shadow-black/20 md:p-6">
            <div className="mb-5 text-center">
              <h2 className="text-xl font-semibold text-white">{reading.reading_type || 'Three Card Spread'}</h2>
              <p className="mt-1 text-sm text-slate-400">{reading.question || question}</p>
            </div>

            <div className="row g-4">
              {reading.cards.map((card, index) => {
                const cardStyle = getCardAccent(card.position);
                return (
                  <div key={`${card.position || 'card'}-${index}`} className="col-12 col-md-6 col-xl-4 d-flex tarot-card-column">
                    <div
                      className="card tarot-result-card tarot-surface-card h-100 w-100 border-0 overflow-hidden"
                      style={{
                        ...cardStyle,
                        boxShadow: cardStyle.shadow,
                        transform: 'translateY(-2px)'
                      }}
                    >
                      <div className="card-body tarot-card-body d-flex flex-column gap-3 p-4">
                        <div className="d-flex align-items-center justify-content-between gap-2">
                          <span className="text-[0.8rem] font-bold uppercase tracking-[0.6px] text-amber-300">
                            {card.position || 'Card'}
                          </span>
                          <div className="text-[1.15rem]">{index === 0 ? '🕊️' : index === 1 ? '✨' : '🔮'}</div>
                        </div>
                        <div className="rounded-[12px] border border-white/10 bg-white/5 p-3">
                          <h3 className="m-0 text-lg font-semibold text-white">{card.card_name || 'Unknown Card'}</h3>
                        </div>
                        <div className="text-sm leading-6 text-slate-300 tarot-text-block">
                          <div><strong>Arcana:</strong> {card.arcana || 'N/A'}</div>
                          <div><strong>Suit:</strong> {card.suit || 'N/A'}</div>
                          <div><strong>Orientation:</strong> {card.orientation || 'N/A'}</div>
                        </div>
                        <div className="border-t border-white/10 pt-3 mt-auto">
                          <h4 className="mb-1 text-[0.8rem] font-semibold uppercase tracking-[0.5px] text-slate-400">Meaning</h4>
                          <div className="tarot-scroll-panel tarot-card-meaning mt-2">
                            <p className="m-0 text-sm leading-6 text-slate-100 tarot-text-block">{card.meaning || 'No meaning provided.'}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="mt-6 row g-4">
              <div className="col-12 d-flex">
                <div className="card tarot-section-card tarot-surface-card h-100 w-100 border-0 bg-slate-950/70 shadow-lg shadow-black/20">
                  <div className="card-body tarot-section-body p-4 p-md-5">
                    <div className="mb-4 d-flex flex-wrap align-items-center justify-content-between gap-3">
                      <div className="d-flex align-items-center gap-2">
                        <span className="text-xl">🤖</span>
                        <h3 className="text-lg font-semibold text-white">AI Prediction</h3>
                      </div>
                      <span className="badge rounded-pill border border-fuchsia-400/30 bg-fuchsia-500/10 px-3 py-2 text-[0.72rem] font-semibold uppercase tracking-[0.25em] text-fuchsia-200">
                        Powered by TensorFlow LSTM
                      </span>
                    </div>
                    <div className="row g-3">
                      <div className="col-12 col-md-6">
                        <div className="rounded-2xl border border-white/10 bg-white/5 p-4 h-100">
                          <p className="mb-2 text-[0.75rem] font-semibold uppercase tracking-[0.2em] text-slate-400">Predicted Category</p>
                          <p className="m-0 text-xl font-semibold text-white tarot-text-block">{predictionCategory}</p>
                        </div>
                      </div>
                      <div className="col-12 col-md-6">
                        <div className="rounded-2xl border border-white/10 bg-white/5 p-4 h-100">
                          <p className="mb-2 text-[0.75rem] font-semibold uppercase tracking-[0.2em] text-slate-400">Prediction Confidence</p>
                          <p className="m-0 text-xl font-semibold text-white tarot-text-block">{predictionConfidence}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="col-12 d-flex">
                <div className="card tarot-section-card tarot-surface-card h-100 w-100 border-0 bg-slate-950/70 shadow-lg shadow-black/20">
                  <div className="card-body tarot-section-body p-4 p-md-5">
                    <div className="mb-3 d-flex align-items-center gap-2">
                      <span className="text-xl">🪄</span>
                      <h3 className="text-lg font-semibold text-white">AI Interpretation</h3>
                    </div>
                    <div className="tarot-scroll-panel tarot-section-content rounded-2xl border border-white/10 bg-white/5 p-4 text-sm leading-7 text-slate-200 tarot-text-block">
                      {reading.ai_interpretation || 'The deck is still preparing a deeper interpretation for you.'}
                    </div>
                  </div>
                </div>
              </div>

              <div className="col-12 d-flex">
                <div className="card tarot-section-card tarot-surface-card h-100 w-100 border-0 bg-slate-950/70 shadow-lg shadow-black/20">
                  <div className="card-body tarot-section-body p-4 p-md-5">
                    <div className="mb-4 d-flex align-items-center gap-2">
                      <span className="text-xl">🌿</span>
                      <h3 className="text-lg font-semibold text-white">Personality Analysis</h3>
                    </div>
                    <div className="row g-4">
                      <div className="col-12 col-lg-6">
                        <div className="rounded-2xl border border-emerald-400/20 bg-emerald-500/10 p-4 h-100">
                          <h4 className="mb-2 text-sm font-semibold uppercase tracking-[0.2em] text-emerald-300">Strengths</h4>
                          {personalityStrengths.length > 0 ? (
                            <ul className="space-y-2 text-sm text-slate-200">
                              {personalityStrengths.map((item, index) => (
                                <li key={`strength-${index}`} className="tarot-list-item d-flex align-items-start gap-2">
                                  <span className="mt-1 text-emerald-300">•</span>
                                  <span>{item}</span>
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <p className="text-sm text-slate-400">No strengths were returned for this reading.</p>
                          )}
                        </div>
                      </div>
                      <div className="col-12 col-lg-6">
                        <div className="rounded-2xl border border-amber-400/20 bg-amber-500/10 p-4 h-100">
                          <h4 className="mb-2 text-sm font-semibold uppercase tracking-[0.2em] text-amber-300">Challenges</h4>
                          {personalityChallenges.length > 0 ? (
                            <ul className="space-y-2 text-sm text-slate-200">
                              {personalityChallenges.map((item, index) => (
                                <li key={`challenge-${index}`} className="tarot-list-item d-flex align-items-start gap-2">
                                  <span className="mt-1 text-amber-300">•</span>
                                  <span>{item}</span>
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <p className="text-sm text-slate-400">No challenges were returned for this reading.</p>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="mt-4 rounded-2xl border border-fuchsia-400/20 bg-fuchsia-500/10 p-4">
                      <h4 className="mb-2 text-sm font-semibold uppercase tracking-[0.2em] text-fuchsia-300">Advice</h4>
                      <p className="text-sm leading-7 text-slate-200 tarot-text-block">
                        {personalityAdvice || 'Stay grounded, trust your instincts, and keep moving with patience.'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="col-12 d-flex">
                <div className="card tarot-section-card tarot-surface-card h-100 w-100 border-0 bg-slate-950/70 shadow-lg shadow-black/20">
                  <div className="card-body tarot-section-body p-4 p-md-5">
                    <div className="mb-4 d-flex align-items-center gap-2">
                      <span className="text-xl">📈</span>
                      <h3 className="text-lg font-semibold text-white">Life Trends</h3>
                    </div>
                    <div className="row g-3">
                      {lifeTrendCards.map((trend) => (
                        <div key={trend.key} className="col-12 col-md-6 col-xl-3">
                          <div className="rounded-2xl border border-white/10 bg-white/5 p-4 h-100 tarot-text-block">
                            <h4 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">{trend.label}</h4>
                            <p className="mt-2 text-sm leading-6 text-slate-200 tarot-text-block">{trend.value}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div className="col-12 d-flex">
                <div className="card tarot-section-card tarot-surface-card h-100 w-100 border-0 bg-slate-950/70 shadow-lg shadow-black/20">
                  <div className="card-body tarot-section-body p-4 p-md-5">
                    <div className="mb-4 d-flex align-items-center gap-2">
                      <span className="text-xl">✨</span>
                      <h3 className="text-lg font-semibold text-white">Recommendations</h3>
                    </div>
                    {recommendations.length > 0 ? (
                      <ul className="space-y-3 text-sm text-slate-200">
                        {recommendations.map((item, index) => (
                          <li key={`recommendation-${index}`} className="tarot-list-item d-flex align-items-start gap-2 rounded-2xl border border-white/10 bg-white/5 px-3 py-3">
                            <span className="mt-0.5 text-lg">✓</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-slate-400">No recommendations were provided for this spread.</p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <button
              type="button"
              className="btn btn-secondary mt-6 w-full rounded-2xl px-4 py-3 text-base"
              onClick={() => handleGenerateReading()}
              disabled={loading}
            >
              Draw Again ✨
            </button>
          </div>
        )}

        <div className="mt-8 border-t border-white/10 pt-6">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-xl font-semibold text-white">Reading History</h2>
            <button
              type="button"
              className="btn btn-secondary rounded-2xl px-4 py-2 text-sm"
              onClick={loadHistory}
              disabled={historyLoading}
            >
              {historyLoading ? 'Refreshing...' : 'Refresh History'}
            </button>
          </div>

          {historyLoading && (
            <div className="py-4 text-center">
              <div className="mystic-spinner mx-auto mb-2" style={{ width: '24px', height: '24px', borderWidth: '2px' }}></div>
              <p className="text-sm text-slate-400">Loading your reading history...</p>
            </div>
          )}

          {!historyLoading && historyError && (
            <div className="alert alert-danger rounded-xl border border-rose-400/20 bg-rose-500/10 px-4 py-3 text-sm">{historyError}</div>
          )}

          {!historyLoading && !historyError && historyGroups.length === 0 && (
            <p className="text-sm text-slate-400">Your saved three-card readings will appear here.</p>
          )}

          <div className="grid gap-4">
            {historyGroups.map((group) => (
              <div
                key={group.groupKey}
                className="tarot-history-card rounded-[16px] border border-white/10 bg-white/5 p-4"
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h3 className="text-base font-semibold text-white">{group.question}</h3>
                    <p className="mt-1 text-sm text-slate-400">{formatDateTime(group.createdAt)}</p>
                  </div>
                  <button
                    type="button"
                    className="btn btn-secondary rounded-2xl px-3 py-2 text-sm"
                    onClick={() => handleViewDetails(group)}
                  >
                    {expandedGroupKey === group.groupKey ? 'Hide Details' : 'View Details'}
                  </button>
                </div>

                <div className="mt-3 grid gap-3 md:grid-cols-3">
                  {group.cards.map((card) => (
                    <div
                      key={`${group.groupKey}-${card.position}`}
                      className="rounded-[12px] border border-white/10 bg-slate-900/60 p-3"
                    >
                      <div className="text-[0.78rem] font-bold uppercase tracking-[0.5px] text-amber-300">
                        {card.position}
                      </div>
                      <div className="mt-1 font-semibold text-white">{card.card_name || 'Unknown Card'}</div>
                      <div className="mt-1 text-sm text-slate-400">{card.orientation || 'N/A'}</div>
                    </div>
                  ))}
                </div>

                {expandedGroupKey === group.groupKey && (
                  <div className="mt-4 rounded-[12px] border border-white/10 bg-slate-900/50 p-3">
                    {detailLoading ? (
                      <p className="m-0 text-sm text-slate-400">Loading details...</p>
                    ) : detailError ? (
                      <p className="m-0 text-sm text-rose-400">{detailError}</p>
                    ) : (
                      <>
                        {detailEntry && (
                          <div className="mb-3">
                            <div className="text-[0.8rem] font-bold uppercase tracking-[0.5px] text-amber-300">Selected Detail</div>
                            <div className="mt-1 font-semibold text-white">{detailEntry.card_name || 'Unknown Card'}</div>
                            <div className="mt-1 text-sm text-slate-400">
                              {detailEntry.position} • {detailEntry.orientation || 'N/A'}
                            </div>
                          </div>
                        )}
                        <div className="grid gap-2 text-sm text-slate-200">
                          {group.cards.map((card) => (
                            <div key={`${group.groupKey}-detail-${card.position}`}>
                              <strong>{card.position}</strong>: {card.card_name || 'Unknown'} — {card.orientation || 'N/A'}
                            </div>
                          ))}
                        </div>
                      </>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TarotReading;
