import requests
import boto3
import time
import os

dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))

class AppTool():
    def __init__(self, table):
        self.table = table

        # Override in subclasses to define specific app service details
        self.tools = {}
        self.client_id = None
        self.client_secret = None
        self.refresh_url = None
        self.service_name = None

    def get_tools(self):
        """Return a list of tools for the specific app service you are implementing"""
        self.tools = []

    def call_tool(self, tool_name, tool_args, user_id):
        return None
    
    def get_app_headers(self, user_id):
        response = self.table.get_item(Key={'userId': user_id})
        item = response.get('Item')

        if not item or self.service_name not in item.get('appTokens', {}):
            return f"{self.service_name} is not connected"

        print
        app_tokens = item['appTokens'][self.service_name]
        access_token = app_tokens['access_token']
        refresh_token = app_tokens.get('refresh_token')
        expires_at = app_tokens.get('expires_at', 0)

        if time.time() > expires_at:
            print("Access token expired. Refreshing...")
            refreshed = self.refresh_access_token(refresh_token)
            if not refreshed:
                return "Failed to refresh Spotify token"
            access_token = refreshed['access_token']
            app_tokens.update(refreshed)
            app_tokens['expires_at'] = int(time.time()) + refreshed['expires_in']
            self.table.put_item(Item={
                **item,
                'appTokens': {**item['appTokens'], self.service_name: app_tokens}
            })

        return {'Authorization': f'Bearer {access_token}'}
    
    def refresh_access_token(self, refresh_token):
        response = requests.post(
            self.refresh_url,
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
        )

        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to refresh token:", response.status_code, response.text)
            return None