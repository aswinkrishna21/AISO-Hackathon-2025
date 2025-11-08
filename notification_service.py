"""
Notification Service
Handles notifications for new messages and incoming calls
"""

from typing import Dict, List
from datetime import datetime
import uuid


class NotificationService:
    """Service for managing notifications"""

    def __init__(self):
        # In-memory storage (replace with database in production)
        self.notifications = []

    def create_notification(
        self, 
        user_id: str, 
        notification_type: str, 
        title: str, 
        message: str, 
        data: Dict = None
    ) -> Dict:
        """Create a new notification"""
        try:
            notification_id = str(uuid.uuid4())
            notification = {
                'id': notification_id,
                'user_id': user_id,
                'type': notification_type,  # 'message', 'call', 'system'
                'title': title,
                'message': message,
                'data': data or {},
                'read': False,
                'created_at': datetime.now().isoformat()
            }

            self.notifications.append(notification)

            return {
                'success': True,
                'notification_id': notification_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_notifications(self, user_id: str, unread_only: bool = False) -> List[Dict]:
        """Get notifications for a user"""
        user_notifications = [
            notif for notif in self.notifications
            if notif['user_id'] == user_id
        ]

        if unread_only:
            user_notifications = [
                notif for notif in user_notifications
                if not notif['read']
            ]

        # Sort by creation time (newest first)
        user_notifications.sort(key=lambda x: x['created_at'], reverse=True)

        return user_notifications

    def mark_as_read(self, notification_id: str) -> bool:
        """Mark a notification as read"""
        for notif in self.notifications:
            if notif['id'] == notification_id:
                notif['read'] = True
                return True
        return False

    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        count = 0
        for notif in self.notifications:
            if notif['user_id'] == user_id and not notif['read']:
                notif['read'] = True
                count += 1
        return count

    def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification"""
        for i, notif in enumerate(self.notifications):
            if notif['id'] == notification_id:
                del self.notifications[i]
                return True
        return False
