import { useState, useEffect, useCallback } from 'react';
import { Notification } from '@/components/ui/notification-bell';
import apiClient from '@/lib/api-client';

interface UseNotificationsOptions {
  pollingInterval?: number;
  initialFetch?: boolean;
}

export function useNotifications(options: UseNotificationsOptions = {}) {
  const { pollingInterval = 30000, initialFetch = true } = options;
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchNotifications = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.getNotifications();
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      if (response.data) {
        setNotifications(response.data.notifications);
        setUnreadCount(response.data.unread_count);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching notifications:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const markAsRead = useCallback(async (id: string) => {
    try {
      const response = await apiClient.markNotificationAsRead(id);
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      setNotifications((prev) =>
        prev.map((notification) =>
          notification.id === id ? { ...notification, isRead: true } : notification
        )
      );
      
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Error marking notification as read:', err);
    }
  }, []);

  const markAllAsRead = useCallback(async () => {
    try {
      const response = await apiClient.markAllNotificationsAsRead();
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      setNotifications((prev) =>
        prev.map((notification) => ({ ...notification, isRead: true }))
      );
      
      setUnreadCount(0);
    } catch (err) {
      console.error('Error marking all notifications as read:', err);
    }
  }, []);

  useEffect(() => {
    if (initialFetch) {
      fetchNotifications();
    }
    
    const intervalId = setInterval(fetchNotifications, pollingInterval);
    
    return () => {
      clearInterval(intervalId);
    };
  }, [fetchNotifications, initialFetch, pollingInterval]);

  return {
    notifications,
    unreadCount,
    isLoading,
    error,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
  };
} 