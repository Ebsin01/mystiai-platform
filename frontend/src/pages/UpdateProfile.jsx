import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import authService from '../services/authService';

/**
 * Update Profile page component.
 * Allows authenticated users to change their full name.
 */
const UpdateProfile = () => {
  const navigate = useNavigate();
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Fetch current user details to pre-populate the input
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await authService.getProfile();
        setFullName(data.full_name || '');
      } catch (err) {
        console.error('Failed to load profile for edit:', err);
        setError('Failed to fetch profile details.');
        if (err.response && err.response.status === 401) {
          authService.logout();
          navigate('/login');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!fullName.trim()) {
      setError('Full Name cannot be empty.');
      return;
    }

    setSubmitting(true);
    setError('');
    setSuccess('');

    try {
      await authService.updateProfile(fullName);
      setSuccess('Profile updated successfully!');
      
      // Redirect back to profile page after a short delay
      setTimeout(() => {
        navigate('/profile');
      }, 1500);
    } catch (err) {
      console.error('Profile update failed:', err);
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Failed to update profile. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="auth-page-container">
        <div className="mystic-card loading-card">
          <div className="mystic-spinner"></div>
          <p>Consulting the archives...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page-container">
      <div className="mystic-card auth-card">
        <div className="auth-card-header">
          <div className="mystic-orb"></div>
          <h2>Edit Profile</h2>
          <p className="subtitle">Modify your digital presence</p>
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
              value={fullName}
              onChange={(e) => {
                setFullName(e.target.value);
                if (error) setError('');
              }}
              required
              disabled={submitting}
              className="mystic-input"
            />
          </div>

          <div className="update-profile-actions">
            <button
              type="submit"
              disabled={submitting}
              className="btn btn-primary"
            >
              {submitting ? 'Updating...' : 'Save Changes'}
            </button>
            <Link to="/profile" className="btn btn-secondary text-center">
              Cancel
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UpdateProfile;
