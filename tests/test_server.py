import pytest
import json
from unittest.mock import patch
from server import app, agent

class TestFlaskServer:
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_options_request(self, client):
        response = client.options('/generate')
        
        assert response.status_code == 200
        assert response.headers['Access-Control-Allow-Origin'] == '*'
        assert 'Content-Type' in response.headers['Access-Control-Allow-Headers']
        assert 'POST' in response.headers['Access-Control-Allow-Methods']
    
    @patch.object(agent, 'process_message')
    def test_generate_success(self, mock_process, client):
        mock_process.return_value = {'completion': 'Test response'}
        
        response = client.post('/generate', 
                             json={'prompt': 'Hello'},
                             headers={'Authorization': 'Bearer testtoken'},
                             content_type='application/json')
        
        assert response.status_code == 200
        assert response.headers['Access-Control-Allow-Origin'] == '*'
        
        data = json.loads(response.data)
        assert data == {'completion': 'Test response'}
        
        mock_process.assert_called_once_with('Hello', [], 'Bearer testtoken')
    
    @patch.object(agent, 'process_message')
    def test_generate_with_history(self, mock_process, client):
        mock_process.return_value = {'completion': 'Response with history'}
        history = [{'user': 'Hi', 'assistant': 'Hello'}]
        
        response = client.post('/generate',
                             json={'prompt': 'How are you?', 'history': history},
                             headers={'Authorization': 'Bearer testtoken'},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == {'completion': 'Response with history'}
        
        mock_process.assert_called_once_with('How are you?', history, 'Bearer testtoken')
    
    @patch.object(agent, 'process_message')
    def test_generate_empty_prompt(self, mock_process, client):
        mock_process.return_value = {'completion': 'Empty response'}
        
        response = client.post('/generate',
                             json={},
                             headers={'Authorization': 'Bearer testtoken'},
                             content_type='application/json')
        
        assert response.status_code == 200
        mock_process.assert_called_once_with('', [], 'Bearer testtoken')
    
    @patch.object(agent, 'process_message')
    def test_generate_agent_exception(self, mock_process, client):
        mock_process.side_effect = Exception("Agent error")
        response = client.post('/generate', json={'prompt': 'Hello'}, headers={'Authorization': 'Bearer testtoken'})
        assert response.status_code == 500
    
    def test_generate_no_content_type(self, client):
        response = client.post('/generate', data=json.dumps({'prompt': 'Hello'}), headers={'Authorization': 'Bearer testtoken'})
        assert response.status_code == 415 