from flask import Blueprint, request, jsonify
from utils.cognito_utils import get_user_from_token
import boto3
from botocore.exceptions import ClientError
import datetime

connections_bp = Blueprint('chat', __name__)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('link-connections-table')

@connections_bp.route('/api/user/get_connections', methods=['GET'])
def get_user_connections():
    user_id = get_user_from_token(request.headers.get('Authorization'))
    
    try:
        response = table.get_item(Key={'userId': user_id})
        connected_apps = response.get('Item', {}).get('connectedApps', [])
        return jsonify(connected_apps)
    except Exception as e:
        return jsonify([])
    
@connections_bp.route('/api/connect/<app_name>', methods=['POST'])
def connect_app(app_name):
    user_id = get_user_from_token(request.headers.get('Authorization'))
    
    # Get current connections
    response = table.get_item(Key={'userId': user_id})
    current_apps = response.get('Item', {}).get('connectedApps', [])
    
    # Add new app if not already connected
    if app_name.lower() not in current_apps:
        current_apps.append(app_name.lower())
    
    # Update DynamoDB
    table.put_item(Item={
        'userId': user_id,
        'connectedApps': current_apps,
        'updatedAt': datetime.utcnow().isoformat()
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
            'updatedAt': datetime.utcnow().isoformat()
        })
        
        return jsonify({'success': True})
        
    except ClientError as e:
        return jsonify({'error': 'Failed to disconnect'}), 500