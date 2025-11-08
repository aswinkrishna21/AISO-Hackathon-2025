"""
Messaging Service
Handles sending and receiving text messages
"""

import uuid
from datetime import datetime
from typing import Dict, List
import json


class MessagingService:
    """Service for managing text messages between users"""

    def __init__(self):
        # In-memory storage (replace with database in production)
        self.messages = []

    def send_message(self, sender: str, recipient: str, message: str) -> Dict:
        """Send a message from sender to recipient"""
        try:
            message_id = str(uuid.uuid4())
            message_data = {
                'id': message_id,
                'sender': sender,
                'recipient': recipient,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'status': 'sent'
            }

            self.messages.append(message_data)

            return {
                'success': True,
                'message_id': message_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_history(self, user1: str, user2: str, limit: int = 50) -> List[Dict]:
        """Get message history between two users"""
        # Filter messages between the two users
        conversation = [
            msg for msg in self.messages
            if (msg['sender'] == user1 and msg['recipient'] == user2) or
               (msg['sender'] == user2 and msg['recipient'] == user1)
        ]

        # Sort by timestamp
        conversation.sort(key=lambda x: x['timestamp'])

        # Return last 'limit' messages
        return conversation[-limit:]

    def get_unread_messages(self, user: str) -> List[Dict]:
        """Get all unread messages for a user"""
        unread = [
            msg for msg in self.messages
            if msg['recipient'] == user and msg['status'] == 'sent'
        ]
        return unread

    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read"""
        for msg in self.messages:
            if msg['id'] == message_id:
                msg['status'] = 'read'
                return True
        return False
