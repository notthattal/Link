from flask import Flask, request, jsonify, abort, make_response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from services.utils.user_cache import user_tools_cache
from services.utils.cognito_utils import get_user_from_token
from services.utils.tools.app_manager import AppManager
from services.bedrock_agent_service import BedrockAgent
from services.connections_db_service import connections_bp
from services.apps_sso_service import sso_service_bp
import boto3
import os

app = Flask(__name__)

# Register blueprints for different services
app.register_blueprint(connections_bp)
app.register_blueprint(sso_service_bp)

CORS(app, supports_credentials=True, origins='*', allow_headers=["Content-Type", "Authorization"])

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["25 per minute"]
)

dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))
table = dynamodb.Table('link-connections-table')

app_manager = AppManager(table)
agent = BedrockAgent(app_manager)

@app.errorhandler(429)
def ratelimit_handler(e):
    return make_response(jsonify({
        "error": "Rate limit exceeded. Please wait and try again."
    }), 429)

@app.before_request
def check_auth():
    if request.path == '/generate' and request.method == 'POST':
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith('Bearer '):
            abort(401, 'Missing or invalid Authorization header')

@limiter.limit("25 per minute")
@app.route('/generate', methods=['POST', 'OPTIONS'])
def generate():
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    data = request.json
    
    if data.get("reset"):
        agent.current_persona = None
        return jsonify({"message": "Persona reset"})

    user_message = data.get('prompt', '')
    conversation_history = data.get('history', [])
    auth_header = request.headers.get('Authorization')

    user_id = get_user_from_token(auth_header)
    tools = user_tools_cache.get_user_tools(user_id)
    if not tools:
        tools = app_manager.get_user_tools(user_id)
        user_tools_cache.set_user_tools(user_id, tools)

    try:
        result = agent.call_bedrock(user_message, conversation_history, auth_header, tools)
        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"Error in generate endpoint: {e}")
        return jsonify({'error': str(e)}), 500