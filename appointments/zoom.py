import requests
import json
from django.conf import settings
from datetime import datetime, timedelta

class ZoomAPI:
    def __init__(self):
        self.client_id = settings.ZOOM_CLIENT_ID
        self.client_secret = settings.ZOOM_CLIENT_SECRET
        self.account_id = settings.ZOOM_ACCOUNT_ID
        self.token_url = "https://zoom.us/oauth/token"
        self.api_base_url = "https://api.zoom.us/v2"
        self.access_token = self.get_access_token()
    
    def get_access_token(self):
        auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'account_credentials',
            'account_id': self.account_id
        }
        response = requests.post(self.token_url, auth=auth, headers=headers, data=data)
        return response.json().get('access_token')
    
    def create_meeting(self, topic, start_time, duration=30):
        url = f"{self.api_base_url}/users/me/meetings"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        payload = {
            "topic": topic,
            "type": 2,  # Scheduled meeting
            "start_time": start_time.isoformat(),
            "duration": duration,
            "settings": {
                "host_video": True,
                "participant_video": True,
                "join_before_host": False,
                "mute_upon_entry": True,
                "waiting_room": True,
                "approval_type": 0  # Automatically approve
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.json()