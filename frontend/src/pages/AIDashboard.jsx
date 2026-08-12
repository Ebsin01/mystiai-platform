import React, { useEffect, useState } from 'react';
import api from '../services/api';

const AIDashboard = () => {
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchModelInfo = async () => {
      try {
        const response = await api.get('/ai/model-info');
        setModelInfo(response.data);
      } catch (err) {
        console.error('Failed to fetch model info:', err);
        setError('Unable to load the AI model dashboard right now.');
      } finally {
        setLoading(false);
      }
    };

    fetchModelInfo();
  }, []);

  const statCards = modelInfo
    ? [
        { label: 'Model Name', value: modelInfo.model_name || 'N/A' },
        { label: 'Framework', value: modelInfo.framework || 'N/A' },
        { label: 'Test Accuracy', value: `${modelInfo.test_accuracy ?? 'N/A'}%` },
        { label: 'Training Samples', value: modelInfo.training_samples?.toLocaleString() || 'N/A' },
        { label: 'Sequence Length', value: modelInfo.sequence_length || 'N/A' },
        { label: 'Vocabulary Size', value: modelInfo.tokenizer_words?.toLocaleString() || 'N/A' },
      ]
    : [];

  return (
    <div className="auth-page-container w-full px-4 py-6 md:px-6 md:py-8">
      <div className="mystic-card w-full max-w-6xl rounded-[24px] border border-white/10 bg-slate-950/70 p-6 shadow-2xl shadow-fuchsia-950/20 backdrop-blur-xl md:p-8">
        <div className="mb-6 text-center">
          <span className="mb-3 inline-flex rounded-full border border-emerald-400/30 bg-emerald-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-emerald-300">
            Deep Learning Model
          </span>
          <h1 className="history-title mb-2 text-2xl font-semibold md:text-3xl">AI Model Performance Dashboard</h1>
          <p className="subtitle text-sm md:text-base">Insights into the neural network powering the tarot experience.</p>
        </div>

        {loading && (
          <div className="py-8 text-center text-slate-300">
            <div className="mystic-spinner mx-auto mb-3" style={{ width: '28px', height: '28px', borderWidth: '2px' }}></div>
            <p>Loading model metrics...</p>
          </div>
        )}

        {error && (
          <div className="alert alert-danger rounded-xl border border-rose-400/20 bg-rose-500/10 px-4 py-3 text-sm">
            {error}
          </div>
        )}

        {!loading && !error && modelInfo && (
          <div className="space-y-5">
            <div className="row g-4">
              {statCards.map((card) => (
                <div key={card.label} className="col-12 col-md-6 col-lg-4">
                  <div className="h-100 rounded-[18px] border border-white/10 bg-white/5 p-4 shadow-lg shadow-black/20">
                    <p className="mb-2 text-[0.75rem] font-semibold uppercase tracking-[0.2em] text-slate-400">{card.label}</p>
                    <p className="m-0 text-lg font-semibold text-white">{card.value}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="row g-4">
              <div className="col-12 col-lg-6">
                <div className="card h-100 border-0 bg-slate-900/60 shadow-lg shadow-black/20">
                  <div className="card-body p-4">
                    <h2 className="mb-3 text-lg font-semibold text-white">Training Accuracy</h2>
                    <img
                      src="/accuracy.png"
                      alt="Training Accuracy"
                      className="img-fluid rounded-3 w-100"
                      style={{ objectFit: 'contain', maxHeight: '320px' }}
                    />
                  </div>
                </div>
              </div>

              <div className="col-12 col-lg-6">
                <div className="card h-100 border-0 bg-slate-900/60 shadow-lg shadow-black/20">
                  <div className="card-body p-4">
                    <h2 className="mb-3 text-lg font-semibold text-white">Training Loss</h2>
                    <img
                      src="/loss.png"
                      alt="Training Loss"
                      className="img-fluid rounded-3 w-100"
                      style={{ objectFit: 'contain', maxHeight: '320px' }}
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-[18px] border border-white/10 bg-slate-900/60 p-5 shadow-lg shadow-black/20">
              <div className="mb-3 flex items-center gap-2">
                <span className="text-xl">🧠</span>
                <h2 className="text-lg font-semibold text-white">Supported Categories</h2>
              </div>
              <div className="flex flex-wrap gap-2">
                {(modelInfo.categories || []).map((category) => (
                  <span
                    key={category}
                    className="rounded-full border border-fuchsia-400/30 bg-gradient-to-r from-fuchsia-500/20 to-violet-500/20 px-3 py-2 text-sm font-medium text-fuchsia-100"
                  >
                    {category}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIDashboard;
