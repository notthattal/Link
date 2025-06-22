import pytest
import os
import base64
from unittest.mock import Mock, patch, MagicMock
from email.mime.text import MIMEText
from services.utils.tools.gmail_tools import GmailAppTool


class TestGmailAppTool:
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        with patch.dict(os.environ, {
            'GMAIL_CLIENT_ID': 'test_client_id',
            'GMAIL_CLIENT_SECRET': 'test_client_secret'
        }):
            self.gmail_tool = GmailAppTool('link-connections-table')
        
        self.user_id = 'test_user_123'

    def test_init_sets_gmail_specific_values(self):
        """Test that GmailAppTool initializes with Gmail-specific values"""
        with patch.dict(os.environ, {
            'GMAIL_CLIENT_ID': 'gmail_client_id',
            'GMAIL_CLIENT_SECRET': 'gmail_client_secret'
        }):
            gmail_tool = GmailAppTool('test-table')
            
        assert gmail_tool.client_id == 'gmail_client_id'
        assert gmail_tool.client_secret == 'gmail_client_secret'
        assert gmail_tool.refresh_url == 'https://oauth2.googleapis.com/token'
        assert gmail_tool.service_name == 'gmail'

    def test_get_tools_returns_gmail_tools(self):
        """Test that get_tools returns correct Gmail tool definitions"""
        tools = self.gmail_tool.get_tools()
        
        assert len(tools) == 3
        
        # Test send email tool
        send_tool = tools[0]['toolSpec']
        assert send_tool['name'] == 'gmail_send_email'
        assert send_tool['description'] == 'Send an email using Gmail'
        assert 'to' in send_tool['inputSchema']['json']['properties']
        assert 'subject' in send_tool['inputSchema']['json']['properties']
        assert 'body' in send_tool['inputSchema']['json']['properties']
        
        # Test list messages tool
        list_tool = tools[1]['toolSpec']
        assert list_tool['name'] == 'gmail_list_messages'
        assert list_tool['description'] == 'List the user\'s most recent Gmail messages'
        assert 'max_results' in list_tool['inputSchema']['json']['properties']
        
        # Test get message tool
        get_tool = tools[2]['toolSpec']
        assert get_tool['name'] == 'gmail_get_message'
        assert get_tool['description'] == 'Get a specific Gmail message by ID'
        assert 'message_id' in get_tool['inputSchema']['json']['properties']

    @patch('services.utils.tools.gmail_tools.requests')
    def test_call_tool_gmail_send_email_success(self, mock_requests):
        """Test successful email sending"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.gmail_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response
        
        tool_args = {
            'to': 'test@example.com',
            'subject': 'Test Subject',
            'body': 'Test Body'
        }
        
        result = self.gmail_tool.call_tool('gmail_send_email', tool_args, self.user_id)
        
        assert result == "Email sent successfully"
        
        # Verify the request was made correctly
        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        
        assert call_args[0][0] == 'https://gmail.googleapis.com/gmail/v1/users/me/messages/send'
        assert call_args[1]['headers']['Authorization'] == 'Bearer test_token'
        assert call_args[1]['headers']['Content-Type'] == 'application/json'
        
        # Verify the email content was encoded correctly
        raw_email = call_args[1]['json']['raw']
        decoded_email = base64.urlsafe_b64decode(raw_email).decode()
        assert 'test@example.com' in decoded_email
        assert 'Test Subject' in decoded_email
        assert 'Test Body' in decoded_email

    @patch('services.utils.tools.gmail_tools.requests')
    def test_call_tool_gmail_send_email_failure(self, mock_requests):
        """Test failed email sending"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.gmail_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_requests.post.return_value = mock_response
        
        tool_args = {
            'to': 'test@example.com',
            'subject': 'Test Subject',
            'body': 'Test Body'
        }
        
        result = self.gmail_tool.call_tool('gmail_send_email', tool_args, self.user_id)
        
        assert result == "Error sending email: 400"

    @patch('services.utils.tools.gmail_tools.requests')
    def test_call_tool_gmail_list_messages_success(self, mock_requests):
        """Test successful message listing"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.gmail_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock list messages response
        mock_list_response = Mock()
        mock_list_response.status_code = 200
        mock_list_response.json.return_value = {
            'messages': [
                {'id': 'msg1'},
                {'id': 'msg2'}
            ]
        }
        
        # Mock individual message responses
        mock_msg_response1 = Mock()
        mock_msg_response1.json.return_value = {
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject 1'},
                    {'name': 'From', 'value': 'sender1@example.com'}
                ]
            }
        }
        
        mock_msg_response2 = Mock()
        mock_msg_response2.json.return_value = {
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject 2'},
                    {'name': 'From', 'value': 'sender2@example.com'}
                ]
            }
        }
        
        mock_requests.get.side_effect = [mock_list_response, mock_msg_response1, mock_msg_response2]
        
        tool_args = {'max_results': 2}
        
        result = self.gmail_tool.call_tool('gmail_list_messages', tool_args, self.user_id)
        
        expected_result = "From: sender1@example.com | Subject: Test Subject 1\nFrom: sender2@example.com | Subject: Test Subject 2"
        assert result == expected_result
        
        # Verify correct API calls were made
        assert mock_requests.get.call_count == 3  # 1 list + 2 individual messages

    @patch('services.utils.tools.gmail_tools.requests')
    def test_call_tool_gmail_list_messages_default_max_results(self, mock_requests):
        """Test message listing with default max_results"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.gmail_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock empty messages response
        mock_list_response = Mock()
        mock_list_response.status_code = 200
        mock_list_response.json.return_value = {'messages': []}
        mock_requests.get.return_value = mock_list_response
        
        tool_args = {}  # No max_results specified
        
        result = self.gmail_tool.call_tool('gmail_list_messages', tool_args, self.user_id)
        
        # Verify default max_results of 5 was used
        call_args = mock_requests.get.call_args
        assert call_args[1]['params']['maxResults'] == 5

    @patch('services.utils.tools.gmail_tools.requests')
    def test_call_tool_gmail_list_messages_failure(self, mock_requests):
        """Test failed message listing"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.gmail_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 403
        mock_requests.get.return_value = mock_response
        
        tool_args = {'max_results': 5}
        
        result = self.gmail_tool.call_tool('gmail_list_messages', tool_args, self.user_id)
        
        assert result == "Error listing messages: 403"

    @patch('services.utils.tools.gmail_tools.requests')
    def test_call_tool_gmail_list_messages_missing_headers(self, mock_requests):
        """Test message listing when some messages have missing headers"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.gmail_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock list messages response
        mock_list_response = Mock()
        mock_list_response.status_code = 200
        mock_list_response.json.return_value = {
            'messages': [{'id': 'msg1'}]
        }
        
        # Mock message response with missing headers
        mock_msg_response = Mock()
        mock_msg_response.json.return_value = {
            'payload': {
                'headers': [
                    {'name': 'Date', 'value': '2023-01-01'}
                    # Missing Subject and From headers
                ]
            }
        }
        
        mock_requests.get.side_effect = [mock_list_response, mock_msg_response]
        
        tool_args = {'max_results': 1}
        
        result = self.gmail_tool.call_tool('gmail_list_messages', tool_args, self.user_id)
        
        assert result == "From: Unknown Sender | Subject: No Subject"

    @patch('services.utils.tools.gmail_tools.requests')
    def test_call_tool_gmail_list_messages_parsing_error(self, mock_requests):
        """Test message listing when message parsing fails"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.gmail_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock list messages response
        mock_list_response = Mock()
        mock_list_response.status_code = 200
        mock_list_response.json.return_value = {
            'messages': [{'id': 'msg1'}]
        }
        
        # Mock message response that raises an exception
        mock_msg_response = Mock()
        mock_msg_response.json.side_effect = Exception("JSON parsing error")
        
        mock_requests.get.side_effect = [mock_list_response, mock_msg_response]
        
        tool_args = {'max_results': 1}
        
        result = self.gmail_tool.call_tool('gmail_list_messages', tool_args, self.user_id)
        
        assert result == "ID: msg1 (error parsing headers)"

    @patch('services.utils.tools.gmail_tools.requests')
    def test_call_tool_gmail_get_message_success(self, mock_requests):
        """Test successful message retrieval"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.gmail_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'snippet': 'This is a preview of the email content...'
        }
        mock_requests.get.return_value = mock_response
        
        tool_args = {'message_id': 'test_message_id'}
        
        result = self.gmail_tool.call_tool('gmail_get_message', tool_args, self.user_id)
        
        assert result == 'This is a preview of the email content...'
        
        # Verify correct API call was made
        expected_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages/test_message_id'
        mock_requests.get.assert_called_once_with(expected_url, headers=mock_headers)

    @patch('services.utils.tools.gmail_tools.requests')
    def test_call_tool_gmail_get_message_no_snippet(self, mock_requests):
        """Test message retrieval when snippet is not available"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.gmail_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock response without snippet
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_requests.get.return_value = mock_response
        
        tool_args = {'message_id': 'test_message_id'}
        
        result = self.gmail_tool.call_tool('gmail_get_message', tool_args, self.user_id)
        
        assert result == 'No preview available'

    @patch('services.utils.tools.gmail_tools.requests')
    def test_call_tool_gmail_get_message_failure(self, mock_requests):
        """Test failed message retrieval"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.gmail_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_requests.get.return_value = mock_response
        
        tool_args = {'message_id': 'nonexistent_message_id'}
        
        result = self.gmail_tool.call_tool('gmail_get_message', tool_args, self.user_id)
        
        assert result == "Error retrieving message: 404"

    def test_call_tool_unknown_tool(self):
        """Test calling an unknown tool"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.gmail_tool.get_app_headers = Mock(return_value=mock_headers)
        
        result = self.gmail_tool.call_tool('unknown_tool', {}, self.user_id)
        
        assert result == "Unknown tool: unknown_tool"

    def test_call_tool_when_gmail_not_connected(self):
        """Test calling tools when Gmail is not connected"""
        # Mock get_app_headers to return error message
        self.gmail_tool.get_app_headers = Mock(return_value="gmail is not connected")
        
        tool_args = {'to': 'test@example.com', 'subject': 'Test', 'body': 'Test'}
        
        # When get_app_headers returns a string, the code will fail when trying to unpack it
        # This test verifies that the TypeError is raised as expected
        with pytest.raises(TypeError, match="'str' object is not a mapping"):
            self.gmail_tool.call_tool('gmail_send_email', tool_args, self.user_id)

    @patch.dict(os.environ, {}, clear=True)
    def test_init_with_missing_env_vars(self):
        """Test initialization when environment variables are missing"""
        gmail_tool = GmailAppTool('test-table')
        
        assert gmail_tool.client_id is None
        assert gmail_tool.client_secret is None
        assert gmail_tool.refresh_url == 'https://oauth2.googleapis.com/token'
        assert gmail_tool.service_name == 'gmail'

    @patch('services.utils.tools.gmail_tools.requests')
    def test_mime_text_encoding(self, mock_requests):
        """Test that MIME text is properly encoded for email sending"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.gmail_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response
        
        tool_args = {
            'to': 'test@example.com',
            'subject': 'Test with special chars: äöü',
            'body': 'Body with unicode: 😀🎉'
        }
        
        result = self.gmail_tool.call_tool('gmail_send_email', tool_args, self.user_id)
        
        assert result == "Email sent successfully"
        
        # Verify the email structure is correct
        call_args = mock_requests.post.call_args
        raw_email = call_args[1]['json']['raw']
        decoded_email = base64.urlsafe_b64decode(raw_email).decode()
        
        # Check that the email contains the basic structure
        assert 'Content-Type: text/plain; charset="utf-8"' in decoded_email
        assert 'to: test@example.com' in decoded_email
        
        # The subject and body will be encoded, so let's verify the base64 content exists
        # The body is base64 encoded in the MIME message
        assert 'Qm9keSB3aXRoIHVuaWNvZGU6IPCfmIDwn46J' in decoded_email  # Base64 encoded body