import React, { createContext, useContext, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import notificationService from '../services/notificationService';

const NotificationContext = createContext(null);

export const NotificationProvider = ({ children }) => {
  const navigate = useNavigate();
  const [unreadCount, setUnreadCount] = useState(0);
  const [unreadLoading, setUnreadLoading] = useState(false);

  const refreshUnreadCount = async () => {
    if (!authService.isAuthenticated()) {
      setUnreadCount(0);
      return;
    }

    setUnreadLoading(true);
    try {
      const count = await notificationService.getUnreadCount();
      setUnreadCount(Number(count) || 0);
    } catch (err) {
      console.error('Unable to refresh unread notifications count:', err);
      if (err.response?.status === 401) {
        authService.logout();
        navigate('/login');
      }
    } finally {
      setUnreadLoading(false);
    }
  };

  useEffect(() => {
    if (authService.isAuthenticated()) {
      refreshUnreadCount();
    }
  }, []);

  return (
    <NotificationContext.Provider
      value={{ unreadCount, setUnreadCount, refreshUnreadCount, unreadLoading }}
    >
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};
