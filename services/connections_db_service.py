from flask import Blueprint, request, jsonify
from services.utils.cognito_utils import get_user_from_token
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from services.utils.user_cache import user_tools_cache
from services.utils.tool_utils import get_user_tools

connections_bp = Blueprint('connections_bp', __name__)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('link-connections-table')

@connections_bp.route('/api/user/get_connections', methods=['GET'])
def get_user_connections():
    user_id = get_user_from_token(request.headers.get('Authorization'))
    try:
        response = table.get_item(Key={'userId': user_id})
        connected_apps = response.get('Item', {}).get('connectedApps', [])
        user_tools_cache.set_user_tools(user_id, get_user_tools(connected_apps))
        return jsonify(connected_apps)
    except Exception as e:
        print(e)
        return jsonify([])
    
@connections_bp.route('/api/connect/<app_name>', methods=['POST'])
def connect_app(app_name, auth_header, tokens=None):
    user_id = get_user_from_token(auth_header)

    response = table.get_item(Key={'userId': user_id})
    current_apps = response.get('Item', {}).get('connectedApps', [])
    app_tokens = response.get('Item', {}).get('appTokens', {})

    if app_name.lower() not in current_apps:
        current_apps.append(app_name.lower())

    # Store tokens if provided
    if tokens:
        app_tokens[app_name.lower()] = {
            'access_token': tokens.get('access_token'),
            'refresh_token': tokens.get('refresh_token'),
            'expires_at': int(datetime.now(timezone.utc).timestamp() + tokens.get('expires_in', 3600))
        }

    table.put_item(Item={
        'userId': user_id,
        'connectedApps': current_apps,
        'appTokens': app_tokens,
        'updatedAt': datetime.now(timezone.utc).isoformat()
    })

    return jsonify({'success': True})

@connections_bp.route('/api/remove/<app_name>', methods=['POST'])
def remove_app(app_name):
    user_id = get_user_from_token(request.headers.get('Authorization'))
    
    try:
        # Get current connections
        response = table.get_item(Key={'userId': user_id})
        current_apps = response.get('Item', {}).get('connectedApps', [])
        
        # Remove app if connected
        if app_name.lower() in current_apps:
            current_apps.remove(app_name.lower())
        
        # Update DynamoDB
        table.put_item(Item={
            'userId': user_id,
            'connectedApps': current_apps,
            'updatedAt': datetime.now(timezone.utc).isoformat()
        })
        
        return jsonify({'success': True})
    except ClientError as e:
        return jsonify({'error': 'Failed to disconnect'}), 500