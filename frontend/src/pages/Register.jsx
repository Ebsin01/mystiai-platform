import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import authService from '../services/authService';

/**
 * Register Page for setting up new user accounts on the platform.
 */
const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const { fullName, email, password, confirmPassword } = formData;

    if (!fullName || !email || !password || !confirmPassword) {
      setError('Please fill in all fields.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await authService.register(fullName, email, password);
      setSuccess('Account created successfully! Redirecting to login...');
      
      // Navigate to login after a brief delay so the user can read the success message
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Failed to create account. Please check your credentials or try again later.');
      }
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-container">
      <div className="mystic-card auth-card">
        <div className="auth-card-header">
          <div className="mystic-orb"></div>
          <h2>Join the Circle</h2>
          <p className="subtitle">Begin your palmistry and tarot intelligence journey</p>
        </div>

        {error && <div className="alert alert-danger">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="fullName">Full Name</label>
            <input
              type="text"
              id="fullName"
              name="fullName"
              placeholder="e.g. Jean-Marie"
              value={formData.fullName}
              onChange={handleChange}
              required
              disabled={loading || success !== ''}
              className="mystic-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              placeholder="seeker@mystic.com"
              value={formData.email}
              onChange={handleChange}
              required
              disabled={loading || success !== ''}
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
              disabled={loading || success !== ''}
              className="mystic-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              placeholder="••••••••"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              disabled={loading || success !== ''}
              className="mystic-input"
            />
          </div>

          <button
            type="submit"
            disabled={loading || success !== ''}
            className="btn btn-primary btn-block"
          >
            {loading ? 'Initiating...' : 'Register'}
          </button>
        </form>

        <div className="auth-card-footer">
          <p>
            Already registered? <Link to="/login" className="mystic-link">Login here</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
