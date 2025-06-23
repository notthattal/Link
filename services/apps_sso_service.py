from flask import Blueprint, request, jsonify, redirect
from dotenv import load_dotenv
from services.connections_db_service import connect_app
import requests
import os

load_dotenv()

sso_service_bp = Blueprint('sso_service_bp', __name__)

FRONTEND_URL = os.getenv('FRONTEND_URL')

@sso_service_bp.route('/callback/<provider>', methods=['GET'])
def redirect_to_frontend(provider):
    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        print(f'Error in redirect_to_frontend: {error}')
        return redirect(f"{FRONTEND_URL}/connect-apps?error={error}")
    
    return redirect(f"{FRONTEND_URL}/callback/{provider}?code={code}")

@sso_service_bp.route('/api/callback/<provider>', methods=['POST'])
def oauth_callback(provider):
    data = request.json
    code = data.get('code')

    if not code:
        print(f"Error: No authorization code provided for {provider}")
        return jsonify({'error': 'No authorization code'}), 400
    
    # OAuth configs for different providers
    oauth_configs = {
        'spotify': {
            'token_url': 'https://accounts.spotify.com/api/token',
            'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
            'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
        },
        'gmail': {
            'token_url': 'https://oauth2.googleapis.com/token',
            'client_id': os.getenv('GMAIL_CLIENT_ID'),
            'client_secret': os.getenv('GMAIL_CLIENT_SECRET'),
        }
    }
    
    if provider not in oauth_configs:
        print(f"Error: Unsupported provider {provider}")
        return jsonify({'error': f'Unsupported provider: {provider}'}), 400
    
    config = oauth_configs[provider]
    
    # Exchange code for token
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': f"{FRONTEND_URL}/callback/{provider}",
        'client_id': config['client_id'],
        'client_secret': config['client_secret']
    }
    
    response = requests.post(config['token_url'], data=token_data)

    if response.status_code == 200:
        tokens = response.json()
        return connect_app(provider, request.headers.get('Authorization'), tokens)
    else:
        return jsonify({'error': 'Token exchange failed'}), 400