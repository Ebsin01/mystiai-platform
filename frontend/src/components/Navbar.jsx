import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import { useNotification } from '../contexts/NotificationContext';
import NotificationPanel from './NotificationPanel';

/**
 * Premium navigation bar representing the branding and navigation endpoints.
 */
const Navbar = () => {
  const navigate = useNavigate();
  const isAuthenticated = authService.isAuthenticated();
  const { unreadCount } = useNotification();
  const [notificationOpen, setNotificationOpen] = useState(false);

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  const toggleNotifications = () => setNotificationOpen((prev) => !prev);

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <span className="logo-sparkle">✨</span> Mystic Auth
        </Link>
        <div className="navbar-links">
          {isAuthenticated ? (
            <>
              <button
                type="button"
                className="notification-button"
                onClick={toggleNotifications}
                aria-label="Open notifications"
              >
                <span className="notification-bell">🔔</span>
                {unreadCount > 0 && (
                  <span className="notification-badge">{unreadCount}</span>
                )}
              </button>

              <Link to="/profile" className="nav-link">Profile</Link>
              <Link to="/update-profile" className="nav-link">Edit Profile</Link>
              <Link to="/tarot-reading" className="nav-link">Tarot Reading</Link>
              <Link to="/three-card-history" className="nav-link">Three Card History</Link>
              <Link to="/ai-dashboard" className="nav-link">AI Dashboard</Link>
              <Link to="/palm-analysis/upload" className="nav-link">Analyze Palm</Link>
              <Link to="/palm-history" className="nav-link">Palm History</Link>
              <button onClick={handleLogout} className="btn btn-secondary nav-btn">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">Login</Link>
              <Link to="/register" className="nav-link">Register</Link>
            </>
          )}
        </div>
      </div>
      {isAuthenticated && (
        <NotificationPanel
          open={notificationOpen}
          onClose={() => setNotificationOpen(false)}
        />
      )}
    </nav>
  );
};

export default Navbar;
