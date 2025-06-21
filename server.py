from flask import Flask, request, jsonify, abort, make_response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from services.persona_agent_service import PersonaAgent
from services.connections_db_service import connections_bp

app = Flask(__name__)
app.register_blueprint(connections_bp)

CORS(app, supports_credentials=True, origins=["http://localhost:5173"], allow_headers=["Content-Type", "Authorization"])

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["25 per minute"]
)

agent = PersonaAgent()

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

    try:
        result = agent.process_message(user_message, conversation_history, auth_header)
        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
   app.run(debug=True, port=5050)