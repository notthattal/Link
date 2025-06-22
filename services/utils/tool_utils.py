from services.utils.tools.spotify_tools import SpotifyAppTool
from services.utils.tools.gmail_tools import GmailAppTool
import boto3
import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('link-connections-table')

def get_user_tools(connected_apps):
    tools = []
    
    if 'spotify' in connected_apps:
        spotify_app_tool = SpotifyAppTool(table)
        tools.extend(spotify_app_tool.get_tools())
    
    if 'gmail' in connected_apps:
        gmail_app_tool = GmailAppTool(table)
        tools.extend(gmail_app_tool.get_tools())
    
    return tools