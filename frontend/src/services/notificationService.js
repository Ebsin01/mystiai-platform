import api from './api';

/**
 * Notification service for fetching and mutating user notifications.
 */
const notificationService = {
  getNotifications: async () => {
    const response = await api.get('/notifications/');
    return Array.isArray(response.data)
      ? response.data
      : response.data.notifications ?? [];
  },

  getUnreadCount: async () => {
    const response = await api.get('/notifications/unread-count');
    return response.data?.unread_count ?? 0;
  },

  markAsRead: async (notificationId) => {
    const response = await api.put(`/notifications/${notificationId}/read`);
    return response.data;
  },

  markAllAsRead: async () => {
    const response = await api.put('/notifications/read-all');
    return response.data;
  },

  deleteNotification: async (notificationId) => {
    const response = await api.delete(`/notifications/${notificationId}`);
    return response.data;
  },
};

export default notificationService;
