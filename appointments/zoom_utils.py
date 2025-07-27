import jwt
import requests
from datetime import datetime, timedelta
from django.conf import settings

class ZoomAPI:
    def __init__(self):
        self.account_id = settings.ZOOM_ACCOUNT_ID
        self.client_id = settings.ZOOM_CLIENT_ID
        self.client_secret = settings.ZOOM_CLIENT_SECRET
        self.base_url = "https://api.zoom.us/v2"

    def get_access_token(self):
        url = "https://zoom.us/oauth/token"
        payload = {
            'grant_type': 'account_credentials',
            'account_id': self.account_id
        }
        response = requests.post(
            url,
            headers={
                "Authorization": f"Basic {self._encode_credentials()}",
            },
            params=payload
        )
        if response.status_code != 200:
            raise Exception(f"Failed to get Zoom access token: {response.text}")
        return response.json()['access_token']

    def _encode_credentials(self):
        import base64
        creds = f"{self.client_id}:{self.client_secret}"
        return base64.b64encode(creds.encode()).decode()

    def create_meeting(self, topic, start_time, duration=30):
        access_token = self.get_access_token()
        url = f"{self.base_url}/users/me/meetings"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        meeting_details = {
            "topic": topic,
            "type": 2,  # Scheduled meeting
            "start_time": start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),  # Must be UTC
            "duration": duration,
            "timezone": "UTC",
            "settings": {
                "join_before_host": True,
                "waiting_room": True,
                "approval_type": 0
            }
        }

        response = requests.post(url, headers=headers, json=meeting_details)
        if response.status_code != 201:
            raise Exception(f"Zoom meeting creation failed: {response.text}")

        return response.json()
