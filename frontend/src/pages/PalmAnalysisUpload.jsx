import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import palmService from '../services/palmService';

/**
 * PalmAnalysisUpload Component
 * Connects to POST /palm/analyze API using FormData.
 * Renders classification results and extracted measurements directly below the upload UI.
 */
const PalmAnalysisUpload = () => {
  const navigate = useNavigate();

  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [interpretationLoading, setInterpretationLoading] = useState(false);
  const [error, setError] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [interpretationResult, setInterpretationResult] = useState(null);
  const [downloadLoading, setDownloadLoading] = useState(false);

  const fileInputRef = useRef(null);

  const formatConfidence = (confidence) => {
    if (confidence == null || Number.isNaN(Number(confidence))) {
      return 'N/A';
    }
    return `${(Number(confidence) * 100).toFixed(2)}%`;
  };

  const formatValue = (value) => value ?? 'N/A';

  const hasValue = (value) => {
    if (value == null) return false;
    const s = String(value).trim();
    if (!s) return false;
    if (s.toLowerCase() === 'n/a') return false;
    return true;
  };

  // ── Drag & Drop Handlers ──────────────────────────────────────────────────────────
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleFileSelection = (file) => {
    setError('');

    const isValidImageType = ['image/jpeg', 'image/png'].includes(file.type) || /\.(jpe?g|png)$/i.test(file.name);

    // Validate file type
    if (!isValidImageType) {
      setError('Please select a valid JPG or PNG image file.');
      setSelectedFile(null);
      setPreviewUrl(null);
      return;
    }

    // Validate file size (Max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('File size exceeds the 5MB limit. Please upload a smaller image.');
      setSelectedFile(null);
      setPreviewUrl(null);
      return;
    }

    setSelectedFile(file);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewUrl(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const triggerFileSelect = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // ── Form Submission ──────────────────────────────────────────────────────────────
  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('Please select or drop an image file first.');
      return;
    }

    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    if (!token) {
      setError('Please log in before analyzing your palm.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await palmService.analyzePalm(selectedFile);
      console.log('Palm analysis response:', result);

      if (!result) {
        throw new Error('No analysis data received from server.');
      }

      setAnalysisResult(result);
    } catch (err) {
      console.error('Failed to analyze palm:', err);

      if (err.response?.status === 401) {
        authService.logout();
        navigate('/login');
        return;
      }

      const detail = err.response?.data?.detail;
      const responseMessage = err.response?.data?.message;

      if (err.response?.status === 422) {
        if (Array.isArray(detail)) {
          const msgs = detail.map((d) => `${d.loc ? d.loc.join('.') + ': ' : ''}${d.msg}`).join(', ');
          setError(`Validation Error: ${msgs}`);
        } else if (typeof detail === 'string') {
          setError(`Validation Error: ${detail}`);
        } else {
          setError('Invalid data submitted. Please ensure you are uploading a valid image.');
        }
        return;
      }

      if (typeof detail === 'string') {
        setError(detail);
      } else if (typeof responseMessage === 'string') {
        setError(responseMessage);
      } else if (err.message) {
        setError(`Error: ${err.message}`);
      } else if (err.response?.status === 400) {
        setError('No hand detected in the image. Please upload a clearer photo with a visible palm.');
      } else {
        setError('Failed to analyze the palm. Please ensure the image is clear and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const resetUpload = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setError('');
    setAnalysisResult(null);
    setInterpretationResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleGenerateInterpretation = async () => {
    if (!analysisResult?.analysis_id) {
      setError('Palm analysis is not available yet. Please analyze an image first.');
      return;
    }

    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    if (!token) {
      setError('Please log in before generating a palm interpretation.');
      return;
    }

    setInterpretationLoading(true);
    setError('');

    try {
      const result = await palmService.generateInterpretation(analysisResult.analysis_id);
      setInterpretationResult(result);
    } catch (err) {
      console.error('Failed to generate palm interpretation:', err);

      if (err.response?.status === 401) {
        authService.logout();
        navigate('/login');
        return;
      }

      const detail = err.response?.data?.detail;
      const responseMessage = err.response?.data?.message;

      if (typeof detail === 'string') {
        setError(detail);
      } else if (typeof responseMessage === 'string') {
        setError(responseMessage);
      } else if (err.message) {
        setError(`Error: ${err.message}`);
      } else {
        setError('Unable to generate a palm interpretation right now. Please try again.');
      }
    } finally {
      setInterpretationLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!analysisResult?.analysis_id) {
      setError('Palm analysis is not available yet. Please analyze an image first.');
      return;
    }

    setDownloadLoading(true);
    setError('');

    try {
      const blob = await palmService.downloadReportPdf(analysisResult.analysis_id);
      const url = window.URL.createObjectURL(new Blob([blob], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `AI_Report_${analysisResult.analysis_id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download PDF:', err);
      if (err.response?.status === 401) {
        authService.logout();
        navigate('/login');
        return;
      }
      if (err.response?.status === 404) {
        setError('PDF not found. It may not be generated yet.');
      } else {
        setError(err.response?.data?.detail || 'Failed to download PDF.');
      }
    } finally {
      setDownloadLoading(false);
    }
  };

  // ── Render ───────────────────────────────────────────────────────────────────────
  const palmShape = analysisResult?.classification?.palm_shape;
  const heartLine = analysisResult?.classification?.heart_line;
  const headLine = analysisResult?.classification?.head_line;
  const lifeLine = analysisResult?.classification?.life_line;
  const measurements = analysisResult?.classification?.measurements;
  const palmFeatures = analysisResult?.palm_features;
  const landmarks = Array.isArray(analysisResult?.landmarks) ? analysisResult.landmarks : [];

  return (
    <div className="auth-page-container" style={{ padding: '2rem', flexDirection: 'column', alignItems: 'center' }}>
      
      {/* ── Upload View ── */}
      <div className="mystic-card" style={{ maxWidth: '600px', width: '100%' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div className="detail-header-icon" style={{ fontSize: '3rem', marginBottom: '1rem' }}>✋</div>
          <h1 className="detail-title">Palm Analysis</h1>
          <p className="subtitle">Upload a clear photo of your palm for AI reading.</p>
        </div>

        {error && (
          <div className="alert alert-danger" style={{ marginBottom: '1.5rem' }}>
            {error}
          </div>
        )}

        <div 
          className={`upload-drop-zone ${dragActive ? 'drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={triggerFileSelect}
          style={{
            border: '2px dashed rgba(255,255,255,0.2)',
            borderRadius: 'var(--border-radius)',
            padding: '3rem 2rem',
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            backgroundColor: dragActive ? 'rgba(255, 255, 255, 0.05)' : 'transparent',
            marginBottom: '1.5rem',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '250px'
          }}
        >
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            accept="image/jpeg,image/png"
            style={{ display: 'none' }} 
          />

          {previewUrl ? (
            <img 
              src={previewUrl} 
              alt="Palm Preview" 
              style={{ 
                maxWidth: '100%', 
                maxHeight: '300px', 
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.5)'
              }} 
            />
          ) : (
            <>
              <div style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.7 }}>📸</div>
              <h3>Drag &amp; Drop your palm image here</h3>
              <p style={{ opacity: 0.7, marginTop: '0.5rem', fontSize: '0.9rem' }}>or click to browse from your device</p>
              <p style={{ opacity: 0.5, marginTop: '1rem', fontSize: '0.8rem' }}>Supports JPG, PNG (Max 5MB)</p>
            </>
          )}
        </div>

        {previewUrl && !loading && (
          <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
            <p style={{ opacity: 0.7, fontSize: '0.9rem' }}>{selectedFile?.name}</p>
            <button 
              style={{ background: 'transparent', border: 'none', color: '#ff6b6b', cursor: 'pointer', marginTop: '0.5rem', textDecoration: 'underline' }}
              onClick={(e) => {
                e.stopPropagation();
                resetUpload();
              }}
            >
              Remove Image
            </button>
          </div>
        )}

        <button 
          className="btn btn-primary" 
          style={{ width: '100%', padding: '1rem', fontSize: '1.1rem', marginTop: '1rem' }}
          onClick={handleAnalyze}
          disabled={!selectedFile || loading}
        >
          {loading ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
              <span className="mystic-spinner" style={{ width: '20px', height: '20px', borderWidth: '2px', margin: 0 }}></span>
              <span>Analyzing your palm...</span>
            </div>
          ) : (
            'Analyze Palm ✨'
          )}
        </button>
      </div>

      {/* ── Results View ── */}
      {analysisResult && (
        <div className="mystic-card" style={{ maxWidth: '900px', width: '100%', marginTop: '2rem', animation: 'fadeInOverlay 0.4s ease' }}>
          <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🔮</div>
            <h2 className="detail-title" style={{ fontSize: '1.75rem', margin: 0 }}>PALM ANALYSIS RESULTS</h2>
            <p style={{ opacity: 0.7, marginTop: '0.5rem' }}>
              Analysis ID: {formatValue(analysisResult.analysis_id)}
              {analysisResult.image_filename ? ` • ${analysisResult.image_filename}` : ''}
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div className="detail-stat" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '6px', padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px' }}>
              <span className="detail-stat-label" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Palm Shape</span>
              <span className="detail-stat-value" style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>
                {formatValue(palmShape?.value)}
              </span>
              <span style={{ fontSize: '0.85rem', color: 'var(--accent-gold)' }}>
                {palmShape?.confidence != null ? `${formatConfidence(palmShape.confidence)} confidence` : 'Confidence: N/A'}
              </span>
            </div>

            <div className="detail-stat" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '6px', padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px' }}>
              <span className="detail-stat-label" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Heart Line</span>
              <span className="detail-stat-value" style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>
                {formatValue(heartLine?.classification)}
              </span>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Length: {formatValue(heartLine?.length)}
              </span>
              <span style={{ fontSize: '0.85rem', color: 'var(--accent-gold)' }}>
                {heartLine?.confidence != null ? `${formatConfidence(heartLine.confidence)} confidence` : 'Confidence: N/A'}
              </span>
            </div>

            <div className="detail-stat" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '6px', padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px' }}>
              <span className="detail-stat-label" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Head Line</span>
              <span className="detail-stat-value" style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>
                {formatValue(headLine?.classification)}
              </span>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Length: {formatValue(headLine?.length)}
              </span>
              <span style={{ fontSize: '0.85rem', color: 'var(--accent-gold)' }}>
                {headLine?.confidence != null ? `${formatConfidence(headLine.confidence)} confidence` : 'Confidence: N/A'}
              </span>
            </div>

            <div className="detail-stat" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '6px', padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px' }}>
              <span className="detail-stat-label" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Life Line</span>
              <span className="detail-stat-value" style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>
                {formatValue(lifeLine?.classification)}
              </span>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Length: {formatValue(lifeLine?.length)}
              </span>
              <span style={{ fontSize: '0.85rem', color: 'var(--accent-gold)' }}>
                {lifeLine?.confidence != null ? `${formatConfidence(lifeLine.confidence)} confidence` : 'Confidence: N/A'}
              </span>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div className="detail-stat" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '6px', padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px' }}>
              <span className="detail-stat-label" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Palm Measurements</span>
              <span style={{ fontSize: '0.95rem', color: 'var(--text-secondary)' }}>Image Width: {formatValue(measurements?.image_width)}</span>
              <span style={{ fontSize: '0.95rem', color: 'var(--text-secondary)' }}>Image Height: {formatValue(measurements?.image_height)}</span>
              <span style={{ fontSize: '0.95rem', color: 'var(--text-secondary)' }}>Palm Width: {formatValue(measurements?.palm_width)}</span>
              <span style={{ fontSize: '0.95rem', color: 'var(--text-secondary)' }}>Palm Length: {formatValue(measurements?.palm_length)}</span>
            </div>

            <div className="detail-stat" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '6px', padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px' }}>
              <span className="detail-stat-label" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Palm Features</span>
              <span style={{ fontSize: '0.95rem', color: 'var(--text-secondary)' }}>Index Finger Length: {formatValue(palmFeatures?.index_finger_length)}</span>
              <span style={{ fontSize: '0.95rem', color: 'var(--text-secondary)' }}>Middle Finger Length: {formatValue(palmFeatures?.middle_finger_length)}</span>
              <span style={{ fontSize: '0.95rem', color: 'var(--text-secondary)' }}>Palm Width: {formatValue(palmFeatures?.palm_width)}</span>
              <span style={{ fontSize: '0.95rem', color: 'var(--text-secondary)' }}>Palm Length: {formatValue(palmFeatures?.palm_length)}</span>
            </div>
          </div>

          <div className="detail-stat" style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
              <span className="detail-stat-label" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Hand Landmarks</span>
              <span style={{ fontSize: '0.95rem', color: 'var(--text-secondary)' }}>Detected: {landmarks.length}</span>
            </div>
            <details style={{ color: 'var(--text-secondary)' }}>
              <summary style={{ cursor: 'pointer', fontWeight: '600' }}>View landmark table</summary>
              <div style={{ marginTop: '0.75rem', overflowX: 'auto' }}>
                {landmarks.length > 0 ? (
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.12)' }}>
                        <th style={{ textAlign: 'left', padding: '0.5rem' }}>ID</th>
                        <th style={{ textAlign: 'left', padding: '0.5rem' }}>X</th>
                        <th style={{ textAlign: 'left', padding: '0.5rem' }}>Y</th>
                        <th style={{ textAlign: 'left', padding: '0.5rem' }}>Z</th>
                      </tr>
                    </thead>
                    <tbody>
                      {landmarks.map((landmark, index) => (
                        <tr key={`${landmark.id ?? index}-${index}`} style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                          <td style={{ padding: '0.5rem' }}>{formatValue(landmark.id)}</td>
                          <td style={{ padding: '0.5rem' }}>{formatValue(landmark.x)}</td>
                          <td style={{ padding: '0.5rem' }}>{formatValue(landmark.y)}</td>
                          <td style={{ padding: '0.5rem' }}>{formatValue(landmark.z)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <p style={{ margin: 0, opacity: 0.7 }}>No landmarks were returned by the backend.</p>
                )}
              </div>
            </details>
          </div>

          <button
            className="btn btn-primary"
            style={{ width: '100%', padding: '0.9rem', fontSize: '1.05rem', marginBottom: '0.75rem' }}
            onClick={handleGenerateInterpretation}
            disabled={interpretationLoading}
          >
            {interpretationLoading ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                <span className="mystic-spinner" style={{ width: '20px', height: '20px', borderWidth: '2px', margin: 0 }}></span>
                <span>Generating your personalized palm interpretation...</span>
              </div>
            ) : (
              'Generate Palm Interpretation ✨'
            )}
          </button>

          {interpretationResult && (
            <div style={{ marginTop: '1.5rem', textAlign: 'left' }}>
              <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
                <h3 className="detail-title" style={{ fontSize: '1.35rem', margin: 0 }}>YOUR PALM INTERPRETATION ✨</h3>
              </div>

              {/* Personality report detailed fields returned by POST /reports/{analysis_id} */}
              <div style={{ marginTop: '1rem', display: 'grid', gap: '0.75rem' }}>
                <div className="detail-stat" style={{ padding: '1rem', borderRadius: '10px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <span className="detail-stat-label">Personality Type</span>
                  <div className="detail-stat-value">{formatValue(interpretationResult.personality_type)}</div>
                  <div style={{ marginTop: '0.5rem' }}>{formatValue(interpretationResult.summary)}</div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px,1fr))', gap: '0.5rem' }}>
                  {['optimism','leadership','confidence','creativity','communication','decision_making','emotional_intelligence','stress_management','adaptability','risk_taking','emotional_balance'].map((k) => (
                    <div key={k} className="detail-stat" style={{ padding: '0.85rem', borderRadius: '8px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)' }}>
                      <span className="detail-stat-label" style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>{k.replace(/_/g,' ')}</span>
                      <div style={{ marginTop: '0.35rem', color: 'var(--text-primary)' }}>{formatValue(interpretationResult[k])}</div>
                    </div>
                  ))}
                </div>

                <div style={{ display: 'grid', gap: '0.5rem' }}>
                  <div className="detail-stat" style={{ padding: '0.85rem', borderRadius: '8px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)' }}>
                    <span className="detail-stat-label">Strengths</span>
                    <div style={{ marginTop: '0.35rem' }}>{Array.isArray(interpretationResult.strengths) ? interpretationResult.strengths.join(', ') : formatValue(interpretationResult.strengths)}</div>
                  </div>

                  <div className="detail-stat" style={{ padding: '0.85rem', borderRadius: '8px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)' }}>
                    <span className="detail-stat-label">Weaknesses</span>
                    <div style={{ marginTop: '0.35rem' }}>{Array.isArray(interpretationResult.weaknesses) ? interpretationResult.weaknesses.join(', ') : formatValue(interpretationResult.weaknesses)}</div>
                  </div>

                  <div className="detail-stat" style={{ padding: '0.85rem', borderRadius: '8px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)' }}>
                    <span className="detail-stat-label">Career</span>
                    <div style={{ marginTop: '0.35rem' }}>{formatValue(interpretationResult.career)}</div>
                  </div>

                  <div className="detail-stat" style={{ padding: '0.85rem', borderRadius: '8px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)' }}>
                    <span className="detail-stat-label">Relationship</span>
                    <div style={{ marginTop: '0.35rem' }}>{formatValue(interpretationResult.relationship)}</div>
                  </div>

                  <div className="detail-stat" style={{ padding: '0.85rem', borderRadius: '8px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)' }}>
                    <span className="detail-stat-label">Health</span>
                    <div style={{ marginTop: '0.35rem' }}>{formatValue(interpretationResult.health)}</div>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                  <button
                    className="btn btn-primary"
                    onClick={handleDownloadPdf}
                    disabled={downloadLoading}
                    style={{ padding: '0.8rem', flex: 1 }}
                  >
                    {downloadLoading ? 'Preparing PDF…' : 'Download PDF'}
                  </button>
                </div>
              </div>

              <div style={{ display: 'grid', gap: '1rem' }}>
                {hasValue(interpretationResult.overall_interpretation) && (
                  <div className="detail-stat" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '6px', padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px' }}>
                    <span className="detail-stat-label" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Overall Interpretation</span>
                    <span style={{ fontSize: '0.95rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>{interpretationResult.overall_interpretation}</span>
                  </div>
                )}

                {hasValue(interpretationResult.personality_interpretation) && (
                  <div className="detail-stat" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '6px', padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px' }}>
                    <span className="detail-stat-label" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Personality</span>
                    <span style={{ fontSize: '0.95rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>{interpretationResult.personality_interpretation}</span>
                  </div>
                )}

                {hasValue(interpretationResult.career_interpretation) && (
                  <div className="detail-stat" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '6px', padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px' }}>
                    <span className="detail-stat-label" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Career</span>
                    <span style={{ fontSize: '0.95rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>{interpretationResult.career_interpretation}</span>
                  </div>
                )}

                {hasValue(interpretationResult.relationship_interpretation) && (
                  <div className="detail-stat" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '6px', padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px' }}>
                    <span className="detail-stat-label" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Relationships</span>
                    <span style={{ fontSize: '0.95rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>{interpretationResult.relationship_interpretation}</span>
                  </div>
                )}

                {hasValue(interpretationResult.life_interpretation) && (
                  <div className="detail-stat" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '6px', padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px' }}>
                    <span className="detail-stat-label" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Life</span>
                    <span style={{ fontSize: '0.95rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>{interpretationResult.life_interpretation}</span>
                  </div>
                )}

                {hasValue(interpretationResult.palm_shape) && (
                  <div className="detail-stat" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '6px', padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px' }}>
                    <span className="detail-stat-label" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Palm Shape</span>
                    <span style={{ fontSize: '0.95rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>{interpretationResult.palm_shape}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          <button
            className="btn btn-secondary"
            style={{ width: '100%', padding: '0.9rem', fontSize: '1.05rem', marginTop: '1rem' }}
            onClick={resetUpload}
          >
            Analyze Another Palm ✨
          </button>
        </div>
      )}
    </div>
  );
};

export default PalmAnalysisUpload;
