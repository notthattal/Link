import pytest
import json
from unittest.mock import patch
from server import app, agent

class TestFlaskServer:    
    def test_options_request(self, client):
        response = client.options('/generate')
        
        assert response.status_code == 200
        assert response.headers['Access-Control-Allow-Origin'] == '*'
        assert 'Content-Type' in response.headers['Access-Control-Allow-Headers']
        assert 'POST' in response.headers['Access-Control-Allow-Methods']
    
    @patch('server.get_user_from_token')
    @patch.object(agent, 'call_bedrock')
    def test_generate_success(self, mock_bedrock, mock_get_user, client):
        mock_get_user.return_value = 'test_user_id'
        mock_bedrock.return_value = {'completion': 'Test response'}
        
        response = client.post('/generate', 
                             json={'prompt': 'Hello'},
                             headers={'Authorization': 'Bearer testtoken'},
                             content_type='application/json')
        
        assert response.status_code == 200
        assert response.headers['Access-Control-Allow-Origin'] == '*'
        
        data = json.loads(response.data)
        assert data == {'completion': 'Test response'}
        
        mock_bedrock.assert_called_once_with('Hello', [], 'Bearer testtoken', [])
    
    @patch('server.get_user_from_token')
    @patch.object(agent, 'call_bedrock')
    def test_generate_with_history(self, mock_bedrock, mock_get_user, client):
        mock_get_user.return_value = 'test_user_id'
        mock_bedrock.return_value = {'completion': 'Response with history'}
        history = [{'user': 'Hi', 'assistant': 'Hello'}]
        
        response = client.post('/generate',
                             json={'prompt': 'How are you?', 'history': history},
                             headers={'Authorization': 'Bearer testtoken'},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == {'completion': 'Response with history'}
        
        mock_bedrock.assert_called_once_with('How are you?', history, 'Bearer testtoken', [])
    
    @patch('server.get_user_from_token')
    @patch.object(agent, 'call_bedrock')
    def test_generate_empty_prompt(self, mock_bedrock, mock_get_user, client):
        mock_get_user.return_value = 'test_user_id'
        mock_bedrock.return_value = {'completion': 'Empty response'}
        
        response = client.post('/generate',
                             json={},
                             headers={'Authorization': 'Bearer testtoken'},
                             content_type='application/json')
        
        assert response.status_code == 200
        mock_bedrock.assert_called_once_with('', [], 'Bearer testtoken', [])
    
    @patch('server.get_user_from_token')
    @patch.object(agent, 'call_bedrock')
    def test_generate_agent_exception(self, mock_bedrock, mock_get_user, client):
        mock_get_user.return_value = 'test_user_id'
        mock_bedrock.side_effect = Exception("Agent error")
        response = client.post('/generate', json={'prompt': 'Hello'}, headers={'Authorization': 'Bearer testtoken'})
        assert response.status_code == 500
    
    def test_generate_no_content_type(self, client):
        response = client.post('/generate', data=json.dumps({'prompt': 'Hello'}), headers={'Authorization': 'Bearer testtoken'})
        assert response.status_code == 415