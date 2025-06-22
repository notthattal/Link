import pytest
import time
from unittest.mock import Mock, patch, MagicMock
import boto3
from services.utils.tools.app_tool import AppTool


class TestAppTool:
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        # Create AppTool instance
        self.app_tool = AppTool('link-connections-table')
        self.app_tool.service_name = 'spotify'
        self.app_tool.client_id = 'test_client_id'
        self.app_tool.client_secret = 'test_client_secret'
        self.app_tool.refresh_url = 'https://accounts.spotify.com/api/token'
        
        self.user_id = 'test_user_123'

    def test_init_sets_table_correctly(self):
        """Test that AppTool initializes with correct table name"""
        app_tool = AppTool('test-table')
        assert app_tool.tools == {}
        assert app_tool.client_id is None
        assert app_tool.client_secret is None
        assert app_tool.refresh_url is None
        assert app_tool.service_name is None

    def test_get_tools_returns_empty_list(self):
        """Test that get_tools returns empty list by default"""
        self.app_tool.get_tools()
        assert self.app_tool.tools == []

    def test_call_tool_returns_none(self):
        """Test that call_tool returns None by default"""
        result = self.app_tool.call_tool('test_tool', {}, 'user_123')
        assert result is None

    def test_get_app_headers_user_not_found(self):
        """Test get_app_headers when user is not found in DynamoDB"""
        mock_table = Mock()
        mock_table.get_item.return_value = {}  # No 'Item' key
        self.app_tool.table = mock_table
        
        result = self.app_tool.get_app_headers('nonexistent_user')
        assert result == "spotify is not connected"

    def test_get_app_headers_service_not_connected(self):
        """Test get_app_headers when service is not in user's appTokens"""
        mock_table = Mock()
        mock_table.get_item.return_value = {
            'Item': {
                'userId': self.user_id,
                'appTokens': {'other_service': {'access_token': 'token'}}
            }
        }
        self.app_tool.table = mock_table
        
        result = self.app_tool.get_app_headers(self.user_id)
        assert result == "spotify is not connected"

    def test_get_app_headers_valid_token_not_expired(self):
        """Test get_app_headers with valid, non-expired token"""
        future_time = int(time.time()) + 3600  # 1 hour in future
        
        mock_table = Mock()
        mock_table.get_item.return_value = {
            'Item': {
                'userId': self.user_id,
                'appTokens': {
                    'spotify': {
                        'access_token': 'valid_token',
                        'refresh_token': 'refresh_token',
                        'expires_at': future_time
                    }
                }
            }
        }
        self.app_tool.table = mock_table
        
        result = self.app_tool.get_app_headers(self.user_id)
        assert result == {'Authorization': 'Bearer valid_token'}

    @patch('services.utils.tools.app_tool.time')
    def test_get_app_headers_expired_token_refresh_success(self, mock_time):
        """Test get_app_headers with expired token that refreshes successfully"""
        mock_time.time.return_value = 1000
        
        mock_table = Mock()
        mock_table.get_item.return_value = {
            'Item': {
                'userId': self.user_id,
                'appTokens': {
                    'spotify': {
                        'access_token': 'expired_token',
                        'refresh_token': 'refresh_token',
                        'expires_at': 500  # In the past
                    }
                }
            }
        }
        self.app_tool.table = mock_table
        
        # Mock successful refresh
        with patch.object(self.app_tool, 'refresh_access_token') as mock_refresh:
            mock_refresh.return_value = {
                'access_token': 'new_token',
                'expires_in': 3600
            }
            
            result = self.app_tool.get_app_headers(self.user_id)
            
            assert result == {'Authorization': 'Bearer new_token'}
            mock_refresh.assert_called_once_with('refresh_token')

    @patch('services.utils.tools.app_tool.time')
    def test_get_app_headers_expired_token_refresh_failure(self, mock_time):
        """Test get_app_headers with expired token that fails to refresh"""
        mock_time.time.return_value = 1000
        
        mock_table = Mock()
        mock_table.get_item.return_value = {
            'Item': {
                'userId': self.user_id,
                'appTokens': {
                    'spotify': {
                        'access_token': 'expired_token',
                        'refresh_token': 'refresh_token',
                        'expires_at': 500  # In the past
                    }
                }
            }
        }
        self.app_tool.table = mock_table
        
        # Mock failed refresh
        with patch.object(self.app_tool, 'refresh_access_token') as mock_refresh:
            mock_refresh.return_value = None
            
            result = self.app_tool.get_app_headers(self.user_id)
            
            assert result == "Failed to refresh Spotify token"

    @patch('services.utils.tools.app_tool.requests')
    def test_refresh_access_token_success(self, mock_requests):
        """Test successful token refresh"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'new_access_token',
            'expires_in': 3600
        }
        mock_requests.post.return_value = mock_response
        
        result = self.app_tool.refresh_access_token('test_refresh_token')
        
        assert result == {
            'access_token': 'new_access_token',
            'expires_in': 3600
        }
        
        mock_requests.post.assert_called_once_with(
            'https://accounts.spotify.com/api/token',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': 'test_refresh_token',
                'client_id': 'test_client_id',
                'client_secret': 'test_client_secret'
            }
        )

    @patch('services.utils.tools.app_tool.requests')
    def test_refresh_access_token_failure(self, mock_requests):
        """Test failed token refresh"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Invalid refresh token'
        mock_requests.post.return_value = mock_response
        
        result = self.app_tool.refresh_access_token('invalid_refresh_token')
        
        assert result is None

    @patch('services.utils.tools.app_tool.time')
    def test_get_app_headers_updates_table_after_refresh(self, mock_time):
        """Test that table is updated with new token after successful refresh"""
        mock_time.time.return_value = 1000
        
        original_item = {
            'userId': self.user_id,
            'appTokens': {
                'spotify': {
                    'access_token': 'expired_token',
                    'refresh_token': 'refresh_token',
                    'expires_at': 500
                },
                'other_service': {
                    'access_token': 'other_token'
                }
            }
        }
        
        mock_table = Mock()
        mock_table.get_item.return_value = {'Item': original_item}
        self.app_tool.table = mock_table
        
        with patch.object(self.app_tool, 'refresh_access_token') as mock_refresh:
            mock_refresh.return_value = {
                'access_token': 'new_token',
                'expires_in': 3600,
                'refresh_token': 'new_refresh_token'
            }
            
            self.app_tool.get_app_headers(self.user_id)
            
            # Verify put_item was called with updated data
            mock_table.put_item.assert_called_once()
            call_args = mock_table.put_item.call_args[1]['Item']
            
            spotify_tokens = call_args['appTokens']['spotify']
            assert spotify_tokens['access_token'] == 'new_token'
            assert spotify_tokens['refresh_token'] == 'new_refresh_token'
            assert spotify_tokens['expires_at'] == 4600  # 1000 + 3600
            
            # Verify other services weren't affected
            assert call_args['appTokens']['other_service']['access_token'] == 'other_token'

    def test_get_app_headers_missing_expires_at(self):
        """Test get_app_headers when expires_at is missing (defaults to 0)"""
        mock_table = Mock()
        mock_table.get_item.return_value = {
            'Item': {
                'userId': self.user_id,
                'appTokens': {
                    'spotify': {
                        'access_token': 'token_without_expiry',
                        'refresh_token': 'refresh_token'
                        # Missing expires_at
                    }
                }
            }
        }
        self.app_tool.table = mock_table
        
        with patch.object(self.app_tool, 'refresh_access_token') as mock_refresh:
            mock_refresh.return_value = {
                'access_token': 'new_token',
                'expires_in': 3600
            }
            
            result = self.app_tool.get_app_headers(self.user_id)
            
            # Should trigger refresh since expires_at defaults to 0
            assert result == {'Authorization': 'Bearer new_token'}
            mock_refresh.assert_called_once()

    def test_get_app_headers_missing_refresh_token(self):
        """Test get_app_headers when refresh_token is missing"""
        past_time = int(time.time()) - 3600  # 1 hour ago
        
        mock_table = Mock()
        mock_table.get_item.return_value = {
            'Item': {
                'userId': self.user_id,
                'appTokens': {
                    'spotify': {
                        'access_token': 'expired_token',
                        'expires_at': past_time
                        # Missing refresh_token
                    }
                }
            }
        }
        self.app_tool.table = mock_table
        
        with patch.object(self.app_tool, 'refresh_access_token') as mock_refresh:
            mock_refresh.return_value = None
            
            result = self.app_tool.get_app_headers(self.user_id)
            
            # Should try to refresh with None refresh_token
            assert result == "Failed to refresh Spotify token"
            mock_refresh.assert_called_once_with(None)

    def test_get_app_headers_no_app_tokens(self):
        """Test get_app_headers when user exists but has no appTokens"""
        mock_table = Mock()
        mock_table.get_item.return_value = {
            'Item': {
                'userId': self.user_id
                # Missing appTokens key
            }
        }
        self.app_tool.table = mock_table
        
        result = self.app_tool.get_app_headers(self.user_id)
        assert result == "spotify is not connected"

    def test_get_app_headers_empty_app_tokens(self):
        """Test get_app_headers when appTokens is empty"""
        mock_table = Mock()
        mock_table.get_item.return_value = {
            'Item': {
                'userId': self.user_id,
                'appTokens': {}
            }
        }
        self.app_tool.table = mock_table
        
        result = self.app_tool.get_app_headers(self.user_id)
        assert result == "spotify is not connected"