import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import authService from '../services/authService';

/**
 * Profile Page displaying JWT-protected user details.
 */
const Profile = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await authService.getProfile();
        setUser(data);
      } catch (err) {
        console.error('Profile fetch failed:', err);
        setError('Failed to load user profile. Your session may have expired.');
        // If unauthorized, clear token and redirect
        if (err.response && err.response.status === 401) {
          authService.logout();
          setTimeout(() => {
            navigate('/login');
          }, 2000);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [navigate]);

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
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
      <div className="mystic-card profile-card">
        <div className="profile-badge-icon">🔮</div>
        
        <h2>Your Mystic Profile</h2>
        <p className="subtitle">Securely decrypted intelligence profile</p>

        {error ? (
          <div className="alert alert-danger">{error}</div>
        ) : user ? (
          <div className="profile-details">
            <div className="detail-item">
              <span className="detail-label">Full Name</span>
              <span className="detail-value">{user.full_name || 'N/A'}</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Email Address</span>
              <span className="detail-value">{user.email}</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Platform Role</span>
              <span className="detail-value role-badge">{user.role || 'User'}</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">User Identifier (ID)</span>
              <span className="detail-value id-badge">#{user.id}</span>
            </div>

            <div className="profile-actions">
              <Link to="/update-profile" className="btn btn-primary">
                Edit Profile
              </Link>
              <button onClick={handleLogout} className="btn btn-secondary">
                Logout
              </button>
            </div>
          </div>
        ) : (
          <div className="alert alert-danger">No profile data available.</div>
        )}
      </div>
    </div>
  );
};

export default Profile;
