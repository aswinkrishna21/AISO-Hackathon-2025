"""
Call Service
Handles voice and video calls
"""

import uuid
from datetime import datetime
from typing import Dict
import os
import requests


class CallService:
    """Service for managing voice and video calls"""

    def __init__(self):
        # In-memory storage (replace with database in production)
        self.calls = {}

        # Daily.co API credentials (for WebRTC rooms)
        self.daily_api_key = os.getenv('DAILY_API_KEY', '')
        self.daily_domain = os.getenv('DAILY_DOMAIN', '')

    def create_call(self, caller: str, recipient: str, call_type: str) -> Dict:
        """Create a new call request"""
        try:
            call_id = str(uuid.uuid4())

            # Create a Daily.co room for the call
            room_url = self._create_daily_room(call_id, call_type)

            call_data = {
                'id': call_id,
                'caller': caller,
                'recipient': recipient,
                'type': call_type,  # 'voice' or 'video'
                'status': 'pending',
                'room_url': room_url,
                'created_at': datetime.now().isoformat(),
                'accepted_at': None,
                'ended_at': None
            }

            self.calls[call_id] = call_data

            return {
                'success': True,
                'call_id': call_id,
                'room_url': room_url
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def accept_call(self, call_id: str, user: str) -> Dict:
        """Accept an incoming call"""
        try:
            if call_id not in self.calls:
                return {
                    'success': False,
                    'error': 'Call not found'
                }

            call = self.calls[call_id]

            if call['recipient'] != user:
                return {
                    'success': False,
                    'error': 'Unauthorized'
                }

            if call['status'] != 'pending':
                return {
                    'success': False,
                    'error': 'Call is not pending'
                }

            call['status'] = 'active'
            call['accepted_at'] = datetime.now().isoformat()

            return {
                'success': True,
                'room_url': call['room_url']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def reject_call(self, call_id: str, user: str) -> Dict:
        """Reject an incoming call"""
        try:
            if call_id not in self.calls:
                return {
                    'success': False,
                    'error': 'Call not found'
                }

            call = self.calls[call_id]

            if call['recipient'] != user:
                return {
                    'success': False,
                    'error': 'Unauthorized'
                }

            call['status'] = 'rejected'
            call['ended_at'] = datetime.now().isoformat()

            # Delete the Daily.co room
            self._delete_daily_room(call['room_url'])

            return {
                'success': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def end_call(self, call_id: str) -> Dict:
        """End an active call"""
        try:
            if call_id not in self.calls:
                return {
                    'success': False,
                    'error': 'Call not found'
                }

            call = self.calls[call_id]
            call['status'] = 'ended'
            call['ended_at'] = datetime.now().isoformat()

            # Delete the Daily.co room
            self._delete_daily_room(call['room_url'])

            return {
                'success': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_call_info(self, call_id: str) -> Dict:
        """Get information about a call"""
        return self.calls.get(call_id, {})

    def _create_daily_room(self, call_id: str, call_type: str) -> str:
        """Create a Daily.co room for the call"""
        if not self.daily_api_key or not self.daily_domain:
            # Return a mock URL if Daily.co is not configured
            return f"https://example.daily.co/{call_id}"

        try:
            headers = {
                'Authorization': f'Bearer {self.daily_api_key}',
                'Content-Type': 'application/json'
            }

            data = {
                'name': call_id,
                'privacy': 'private',
                'properties': {
                    'enable_chat': False,
                    'enable_screenshare': call_type == 'video',
                    'start_video_off': call_type == 'voice',
                    'start_audio_off': False,
                    'max_participants': 2
                }
            }

            response = requests.post(
                'https://api.daily.co/v1/rooms',
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                room_data = response.json()
                return room_data['url']
            else:
                # Fallback to mock URL
                return f"https://{self.daily_domain}.daily.co/{call_id}"

        except Exception as e:
            print(f"Error creating Daily.co room: {e}")
            return f"https://example.daily.co/{call_id}"

    def _delete_daily_room(self, room_url: str):
        """Delete a Daily.co room"""
        if not self.daily_api_key or 'example.daily.co' in room_url:
            return

        try:
            room_name = room_url.split('/')[-1]

            headers = {
                'Authorization': f'Bearer {self.daily_api_key}'
            }

            requests.delete(
                f'https://api.daily.co/v1/rooms/{room_name}',
                headers=headers
            )
        except Exception as e:
            print(f"Error deleting Daily.co room: {e}")
