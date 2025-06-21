import boto3
from flask import abort
from botocore.exceptions import ClientError

def get_user_from_token(auth_header):
    """Get user from Cognito using the access token"""
    if not auth_header or not auth_header.startswith('Bearer '):
        abort(401, description="Missing token")
    
    access_token = auth_header.replace('Bearer ', '')
    
    try:
        cognito = boto3.client('cognito-idp', region_name='us-east-1')
        
        # Cognito validates the token and returns user info
        response = cognito.get_user(AccessToken=access_token)
        
        # Get the user ID from the response
        user_id = response['Username']  # This is the Cognito user ID
        return user_id
        
    except ClientError as e:
        abort(401, description="Invalid token")