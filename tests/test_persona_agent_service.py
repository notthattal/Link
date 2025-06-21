import pytest
import pandas as pd
from unittest.mock import Mock, patch
from services.persona_agent_service import PersonaAgent, Persona

class TestPersonaAgent:
    @pytest.fixture
    def mock_personas_df(self):
        return pd.DataFrame({
            'Name': ['Superman', 'Batman', 'Wonder Woman'],
            'Description': [
                'A noble alien with limitless power',
                'A grief-powered genius who uses fear',
                'An Amazon warrior princess'
            ]
        })

    @pytest.fixture
    def agent(self):
        agent = PersonaAgent()
        agent.client = Mock()
        return agent

    def test_init(self, agent):
        assert agent.current_persona is None
        assert agent.client is not None

    def test_set_persona_success(self, agent):
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.parsed = Persona(name="Superman", description="A noble alien with limitless power")
        mock_response.choices = [mock_choice]
        agent.client.beta.chat.completions.parse.return_value = mock_response

        agent.set_persona("I want to be Superman")

        assert agent.current_persona.name == 'Superman'

    def test_set_persona_not_found(self, agent):
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.parsed = None
        mock_response.choices = [mock_choice]
        agent.client.beta.chat.completions.parse.return_value = mock_response

        agent.set_persona("Unknown hero")

        assert agent.current_persona.name == 'Default Hero'

    def test_build_persona_prompt(self, agent):
        agent.current_persona = Persona(name='Superman', description='A noble alien with limitless power')
        prompt = agent.build_persona_prompt("Help me save the city")

        assert 'Superman' in prompt
        assert 'A noble alien with limitless power' in prompt
        assert 'Help me save the city' in prompt
        assert 'Instructions:' in prompt
        assert "Don't break character" in prompt

    @patch('services.persona_agent_service.requests.post')
    def test_call_bedrock_success(self, mock_post, agent):
        mock_response = Mock()
        mock_response.json.return_value = {'completion': 'I am Superman!'}
        mock_post.return_value = mock_response

        result = agent.call_bedrock("Test prompt")

        assert result == {'completion': 'I am Superman!'}
        mock_post.assert_called_once_with(
            'https://x2pwa5y235.execute-api.us-east-1.amazonaws.com/Prod/generate',
            json={'prompt': 'Test prompt'},
            headers={'Authorization': None}
        )

    @patch('services.persona_agent_service.requests.post')
    def test_call_bedrock_with_history(self, mock_post, agent):
        mock_response = Mock()
        mock_response.json.return_value = {'completion': 'Response with history'}
        mock_post.return_value = mock_response

        history = [
            {'user': 'Hello', 'assistant': 'Hi there'},
            {'user': 'How are you?', 'assistant': 'I am fine'}
        ]

        result = agent.call_bedrock("New message", history)

        expected_prompt = "Previous conversation:\nUser: Hello\nAssistant: Hi there\nUser: How are you?\nAssistant: I am fine\n\nCurrent message: New message"
        mock_post.assert_called_once_with(
            'https://x2pwa5y235.execute-api.us-east-1.amazonaws.com/Prod/generate',
            json={'prompt': expected_prompt},
            headers={'Authorization': None}
        )
        assert result == {'completion': 'Response with history'}

    @patch('services.persona_agent_service.requests.post')
    def test_call_bedrock_history_truncation(self, mock_post, agent):
        mock_response = Mock()
        mock_response.json.return_value = {'completion': 'Response'}
        mock_post.return_value = mock_response

        history = [{'user': f'msg{i}', 'assistant': f'resp{i}'} for i in range(10)]

        agent.call_bedrock("New message", history)

        called_prompt = mock_post.call_args[1]['json']['prompt']
        assert 'msg5' in called_prompt
        assert 'msg0' not in called_prompt

    def test_process_message_no_current_persona(self, agent):
        agent.set_persona = Mock()
        agent.set_persona.side_effect = lambda x: setattr(agent, 'current_persona', Persona(name="Superman", description="A noble alien with limitless power"))

        result = agent.process_message("Hello there")

        agent.set_persona.assert_called_once_with("Hello there")
        assert result == {'completion': 'Superman speaking'}

    @patch.object(PersonaAgent, 'call_bedrock')
    @patch.object(PersonaAgent, 'build_persona_prompt')
    def test_process_message_with_persona(self, mock_build_prompt, mock_call_bedrock, agent):
        agent.current_persona = Persona(name='Superman', description='A noble alien with limitless power')
        mock_build_prompt.return_value = "Superman prompt"
        mock_call_bedrock.return_value = {'completion': 'Superman response'}

        result = agent.process_message("Help me")

        mock_build_prompt.assert_called_once_with("Help me")
        mock_call_bedrock.assert_called_once_with("Superman prompt", None, None)
        assert result == {'completion': 'Superman response'}

    @patch.object(PersonaAgent, 'call_bedrock')
    @patch.object(PersonaAgent, 'build_persona_prompt')
    def test_process_message_with_history(self, mock_build_prompt, mock_call_bedrock, agent):
        agent.current_persona = Persona(name='Batman', description='A grief-powered genius who uses fear')
        mock_build_prompt.return_value = "Batman prompt"
        mock_call_bedrock.return_value = {'completion': 'Batman response'}
        history = [{'user': 'test', 'assistant': 'response'}]

        result = agent.process_message("Help", history, None)

        mock_call_bedrock.assert_called_once_with("Batman prompt", history, None)
        assert result == {'completion': 'Batman response'}
