import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import notificationService from '../services/notificationService';
import { useNotification } from '../contexts/NotificationContext';

const typeIcons = {
  analysis: '🔍',
  report: '📄',
  system: '⚙️',
};

const NotificationPanel = ({ open, onClose }) => {
  const { unreadCount, setUnreadCount, refreshUnreadCount } = useNotification();
  const navigate = useNavigate();
  const panelRef = useRef(null);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [processingIds, setProcessingIds] = useState([]);

  const formatDate = (value) => {
    if (!value) return 'Unknown';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;

    const now = new Date();
    const today = now.toDateString();
    const yesterday = new Date(now);
    yesterday.setDate(now.getDate() - 1);

    const timeString = date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });

    if (date.toDateString() === today) {
      return `Today, ${timeString}`;
    }

    if (date.toDateString() === yesterday.toDateString()) {
      return `Yesterday, ${timeString}`;
    }

    return date.toLocaleString([], {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const loadNotifications = async () => {
    setLoading(true);
    setError('');

    try {
      const data = await notificationService.getNotifications();
      setNotifications(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Unable to load notifications:', err);
      if (err.response?.status === 401) {
        onClose?.();
        authService.logout();
        navigate('/login');
        return;
      }
      setError('Unable to load notifications.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!open) return;
    loadNotifications();
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const handleClickOutside = (event) => {
      if (panelRef.current && !panelRef.current.contains(event.target)) {
        onClose?.();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [open, onClose]);

  const startProcessing = (id) => setProcessingIds((prev) => [...prev, id]);
  const stopProcessing = (id) => setProcessingIds((prev) => prev.filter((item) => item !== id));

  const handleMarkAsRead = async (notification) => {
    if (notification.read) return;
    startProcessing(notification.id);
    setError('');

    try {
      await notificationService.markAsRead(notification.id);
      setNotifications((prev) =>
        prev.map((item) =>
          item.id === notification.id ? { ...item, read: true } : item
        )
      );
      setUnreadCount((count) => Math.max(0, count - 1));
    } catch (err) {
      console.error('Unable to mark notification as read:', err);
      setError('Unable to update this notification.');
    } finally {
      stopProcessing(notification.id);
    }
  };

  const handleMarkAllAsRead = async () => {
    setError('');
    const unreadExists = notifications.some((notification) => !notification.read);
    if (!unreadExists) return;

    try {
      await notificationService.markAllAsRead();
      setNotifications((prev) => prev.map((item) => ({ ...item, read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error('Unable to mark all notifications as read:', err);
      setError('Unable to mark all notifications as read.');
    }
  };

  const handleDelete = async (notificationId, isUnread) => {
    startProcessing(notificationId);
    setError('');

    try {
      await notificationService.deleteNotification(notificationId);
      setNotifications((prev) => prev.filter((item) => item.id !== notificationId));
      if (isUnread) {
        setUnreadCount((count) => Math.max(0, count - 1));
      }
    } catch (err) {
      console.error('Unable to delete notification:', err);
      setError('Unable to delete this notification.');
    } finally {
      stopProcessing(notificationId);
    }
  };

  return (
    <div className={`notification-panel ${open ? 'notification-panel-open' : ''}`} ref={panelRef}>
      <div className="notification-panel-header">
        <div>
          <h4>Notifications</h4>
          <p className="notification-panel-subtitle">Recent activity and system updates.</p>
        </div>
        <button
          type="button"
          className="btn btn-secondary btn-sm"
          onClick={handleMarkAllAsRead}
          disabled={notifications.every((item) => item.read) || loading}
        >
          Mark all as read
        </button>
      </div>

      {error && <div className="alert alert-danger notification-alert">{error}</div>}

      {loading ? (
        <div className="notification-loading">
          <div className="mystic-spinner" style={{ width: '34px', height: '34px', borderWidth: '3px' }}></div>
          <p>Loading your notifications...</p>
        </div>
      ) : notifications.length === 0 ? (
        <div className="notification-empty-state">
          <div className="notification-empty-icon">🔔</div>
          <p>No notifications yet</p>
        </div>
      ) : (
        <div className="notification-list">
          {notifications.map((notification) => {
            const isUnread = !notification.read;
            const isProcessing = processingIds.includes(notification.id);
            return (
              <div
                key={notification.id}
                className={`notification-item ${isUnread ? 'notification-item-unread' : ''}`}
                onClick={() => handleMarkAsRead(notification)}
              >
                <div className="notification-item-main">
                  <div className="notification-type-icon">{typeIcons[notification.type] || '🔔'}</div>
                  <div className="notification-item-content">
                    <div className="notification-item-title">{notification.title || 'Notification'}</div>
                    <div className="notification-item-message">{notification.message || 'No details available.'}</div>
                    <div className="notification-item-meta">
                      <span className="notification-type-badge">{notification.type || 'system'}</span>
                      <span className="notification-date">{formatDate(notification.created_at)}</span>
                    </div>
                  </div>
                </div>
                <div className="notification-item-actions">
                  <button
                    type="button"
                    className="notification-delete-btn"
                    onClick={(event) => {
                      event.stopPropagation();
                      handleDelete(notification.id, isUnread);
                    }}
                    disabled={isProcessing}
                    aria-label="Delete notification"
                  >
                    ✕
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default NotificationPanel;
