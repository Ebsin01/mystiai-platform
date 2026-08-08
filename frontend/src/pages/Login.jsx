import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import authService from '../services/authService';

/**
 * Premium Login Page with validation, error states, and a modern aesthetic.
 */
const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Clear error message when user modifies input
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.email || !formData.password) {
      setError('Please fill in all fields.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await authService.login(formData.email, formData.password);
      // Redirect to profile page on successful authentication
      navigate('/profile');
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Connection failed. Please ensure the backend is running.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-container">
      <div className="mystic-card auth-card">
        <div className="auth-card-header">
          <div className="mystic-orb"></div>
          <h2>Welcome Back</h2>
          <p className="subtitle">Step into your personal tarot dashboard</p>
        </div>

        {error && <div className="alert alert-danger">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              placeholder="e.g. seeker@mystic.com"
              value={formData.email}
              onChange={handleChange}
              required
              disabled={loading}
              className="mystic-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              placeholder="••••••••"
              value={formData.password}
              onChange={handleChange}
              required
              disabled={loading}
              className="mystic-input"
            />
          </div>

          <button type="submit" disabled={loading} className="btn btn-primary btn-block">
            {loading ? 'Decrypting Access...' : 'Login'}
          </button>
        </form>

        <div className="auth-card-footer">
          <p>
            New to the platform? <Link to="/register" className="mystic-link">Create Account</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
