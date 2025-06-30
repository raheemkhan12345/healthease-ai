import requests
import json
from django.conf import settings
from datetime import datetime
import base64

class ZoomAPI:
    def __init__(self):
        self.client_id = settings.ZOOM_CLIENT_ID
        self.client_secret = settings.ZOOM_CLIENT_SECRET
        self.account_id = settings.ZOOM_ACCOUNT_ID
        self.token = self.get_access_token()
    
    def get_access_token(self):
        """Get OAuth access token using Server-to-Server OAuth"""
        auth_str = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_str.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'account_credentials',
            'account_id': self.account_id
        }
        
        response = requests.post(
            'https://zoom.us/oauth/token',
            headers=headers,
            data=data
        )
        
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            raise Exception(f"Zoom OAuth failed: {response.text}")
    
    def create_meeting(self, topic, start_time, duration=30, timezone='UTC'):
        """Create a new Zoom meeting"""
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'topic': topic,
            'type': 2,  # Scheduled meeting
            'start_time': start_time.isoformat(),
            'duration': duration,
            'timezone': timezone,
            'settings': {
                'host_video': True,
                'participant_video': True,
                'join_before_host': False,
                'mute_upon_entry': False,
                'waiting_room': True,
                'approval_type': 0,  # Automatically approve
                'audio': 'both',  # Both telephony and VoIP
                'auto_recording': 'cloud',
                'enforce_login': False
            }
        }
        
        response = requests.post(
            'https://api.zoom.us/v2/users/me/meetings',
            headers=headers,
            json=payload
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Zoom API error: {response.text}")