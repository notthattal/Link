import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from services.utils.tools.spotify_tools import SpotifyAppTool


class TestSpotifyAppTool:
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        with patch.dict(os.environ, {
            'SPOTIFY_CLIENT_ID': 'test_spotify_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_spotify_client_secret'
        }):
            self.spotify_tool = SpotifyAppTool('link-connections-table')
        
        self.user_id = 'test_user_123'

    def test_init_sets_spotify_specific_values(self):
        """Test that SpotifyAppTool initializes with Spotify-specific values"""
        with patch.dict(os.environ, {
            'SPOTIFY_CLIENT_ID': 'spotify_client_id',
            'SPOTIFY_CLIENT_SECRET': 'spotify_client_secret'
        }):
            spotify_tool = SpotifyAppTool('test-table')
            
        assert spotify_tool.client_id == 'spotify_client_id'
        assert spotify_tool.client_secret == 'spotify_client_secret'
        assert spotify_tool.refresh_url == 'https://accounts.spotify.com/api/token'
        assert spotify_tool.service_name == 'spotify'

    def test_get_tools_returns_spotify_tools(self):
        """Test that get_tools returns correct Spotify tool definitions"""
        tools = self.spotify_tool.get_tools()
        
        assert len(tools) == 8
        
        tool_names = [tool['toolSpec']['name'] for tool in tools]
        expected_tools = [
            'spotify_add_to_playlist',
            'spotify_remove_from_playlist',
            'spotify_get_user_playlists',
            'spotify_search_tracks',
            'spotify_get_audio_features',
            'spotify_get_artist_info',
            'spotify_get_recommendations',
            'spotify_get_artist_top_tracks'
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_add_to_playlist_success(self, mock_requests):
        """Test successful track addition to playlist"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock search results
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {
            'tracks': {
                'items': [
                    {
                        'name': 'Test Song',
                        'artists': [{'name': 'Test Artist'}],
                        'uri': 'spotify:track:test123'
                    }
                ]
            }
        }
        
        # Mock add to playlist response
        add_response = Mock()
        add_response.status_code = 201
        
        mock_requests.get.return_value = search_response
        mock_requests.post.return_value = add_response
        
        tool_args = {
            'playlist_id': 'test_playlist',
            'query': 'test song'
        }
        
        result = self.spotify_tool.call_tool('spotify_add_to_playlist', tool_args, self.user_id)
        
        assert result == "Track added to playlist"
        
        # Verify search was called
        mock_requests.get.assert_called_once()
        # Verify add to playlist was called
        mock_requests.post.assert_called_once()

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_add_to_playlist_failure(self, mock_requests):
        """Test failed track addition to playlist"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock search results
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {
            'tracks': {
                'items': [
                    {
                        'name': 'Test Song',
                        'artists': [{'name': 'Test Artist'}],
                        'uri': 'spotify:track:test123'
                    }
                ]
            }
        }
        
        # Mock failed add to playlist response
        add_response = Mock()
        add_response.status_code = 400
        
        mock_requests.get.return_value = search_response
        mock_requests.post.return_value = add_response
        
        tool_args = {
            'playlist_id': 'test_playlist',
            'query': 'test song'
        }
        
        result = self.spotify_tool.call_tool('spotify_add_to_playlist', tool_args, self.user_id)
        
        assert result == "Error: 400"

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_remove_from_playlist_success(self, mock_requests):
        """Test successful track removal from playlist"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock search results
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {
            'tracks': {
                'items': [
                    {
                        'name': 'Test Song',
                        'artists': [{'name': 'Test Artist'}],
                        'uri': 'spotify:track:test123'
                    }
                ]
            }
        }
        
        # Mock remove from playlist response
        remove_response = Mock()
        remove_response.status_code = 200
        
        mock_requests.get.return_value = search_response
        mock_requests.delete.return_value = remove_response
        
        tool_args = {
            'playlist_id': 'test_playlist',
            'query': 'test song'
        }
        
        result = self.spotify_tool.call_tool('spotify_remove_from_playlist', tool_args, self.user_id)
        
        assert result == "Track removed from playlist"

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_user_playlists_success(self, mock_requests):
        """Test successful playlist retrieval"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock playlists response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {'name': 'My Playlist 1'},
                {'name': 'My Playlist 2'},
                {'name': 'Liked Songs'}
            ]
        }
        mock_requests.get.return_value = mock_response
        
        result = self.spotify_tool.call_tool('spotify_get_user_playlists', {}, self.user_id)
        
        expected_result = "My Playlist 1\nMy Playlist 2\nLiked Songs"
        assert result == expected_result
        
        mock_requests.get.assert_called_once_with(
            'https://api.spotify.com/v1/me/playlists',
            headers=mock_headers
        )

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_user_playlists_failure(self, mock_requests):
        """Test failed playlist retrieval"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 403
        mock_requests.get.return_value = mock_response
        
        result = self.spotify_tool.call_tool('spotify_get_user_playlists', {}, self.user_id)
        
        assert result == "Error getting playlists: 403"

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_search_tracks_success(self, mock_requests):
        """Test successful track search"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock search response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'tracks': {
                'items': [
                    {
                        'name': 'Song 1',
                        'artists': [{'name': 'Artist 1'}],
                        'uri': 'spotify:track:song1'
                    },
                    {
                        'name': 'Song 2',
                        'artists': [{'name': 'Artist 2'}],
                        'uri': 'spotify:track:song2'
                    }
                ]
            }
        }
        mock_requests.get.return_value = mock_response
        
        tool_args = {'query': 'test search', 'limit': 5}
        
        result = self.spotify_tool.call_tool('spotify_search_tracks', tool_args, self.user_id)
        
        expected_result = "Song 1 by Artist 1 - spotify:track:song1\nSong 2 by Artist 2 - spotify:track:song2"
        assert result == expected_result
        
        # Verify correct API call
        mock_requests.get.assert_called_once_with(
            'https://api.spotify.com/v1/search',
            headers=mock_headers,
            params={'q': 'test search', 'type': 'track', 'limit': 5}
        )

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_search_tracks_default_limit(self, mock_requests):
        """Test track search with default limit"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock search response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'tracks': {'items': []}}
        mock_requests.get.return_value = mock_response
        
        tool_args = {'query': 'test search'}  # No limit specified
        
        self.spotify_tool.call_tool('spotify_search_tracks', tool_args, self.user_id)
        
        # Verify default limit of 10 was used
        call_args = mock_requests.get.call_args
        assert call_args[1]['params']['limit'] == 10

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_search_tracks_failure(self, mock_requests):
        """Test failed track search"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_requests.get.return_value = mock_response
        
        tool_args = {'query': 'test search'}
        
        result = self.spotify_tool.call_tool('spotify_search_tracks', tool_args, self.user_id)
        
        assert result == "Search error: 400"

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_audio_features_success(self, mock_requests):
        """Test successful audio features retrieval"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock search response first (since audio features searches for track)
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {
            'tracks': {
                'items': [
                    {
                        'name': 'Test Song',
                        'artists': [{'name': 'Test Artist'}],
                        'uri': 'spotify:track:test123'
                    }
                ]
            }
        }
        
        # Mock audio features response
        audio_features_response = Mock()
        audio_features_response.status_code = 200
        audio_features_data = {
            'danceability': 0.8,
            'energy': 0.9,
            'valence': 0.7,
            'tempo': 120.0
        }
        audio_features_response.json.return_value = audio_features_data
        
        # Set up side_effect for multiple calls
        mock_requests.get.side_effect = [search_response, audio_features_response]
        
        tool_args = {'track_uri': 'test song'}
        
        result = self.spotify_tool.call_tool('spotify_get_audio_features', tool_args, self.user_id)
        
        assert result == audio_features_data

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_audio_features_failure(self, mock_requests):
        """Test failed audio features retrieval"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock search response first
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {
            'tracks': {
                'items': [
                    {
                        'name': 'Test Song',
                        'artists': [{'name': 'Test Artist'}],
                        'uri': 'spotify:track:test123'
                    }
                ]
            }
        }
        
        # Mock failed audio features response
        audio_features_response = Mock()
        audio_features_response.status_code = 404
        
        mock_requests.get.side_effect = [search_response, audio_features_response]
        
        tool_args = {'track_uri': 'test song'}
        
        result = self.spotify_tool.call_tool('spotify_get_audio_features', tool_args, self.user_id)
        
        assert result == "Audio feature error: 404"

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_artist_info_success(self, mock_requests):
        """Test successful artist info retrieval"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock artist info response
        mock_response = Mock()
        mock_response.status_code = 200
        artist_data = {
            'name': 'Test Artist',
            'genres': ['pop', 'rock'],
            'popularity': 85,
            'followers': {'total': 1000000}
        }
        mock_response.json.return_value = artist_data
        mock_requests.get.return_value = mock_response
        
        tool_args = {'artist_id': 'test_artist_id'}
        
        result = self.spotify_tool.call_tool('spotify_get_artist_info', tool_args, self.user_id)
        
        assert result == artist_data
        
        mock_requests.get.assert_called_once_with(
            'https://api.spotify.com/v1/artists/test_artist_id',
            headers=mock_headers
        )

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_artist_info_failure(self, mock_requests):
        """Test failed artist info retrieval"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_requests.get.return_value = mock_response
        
        tool_args = {'artist_id': 'nonexistent_artist'}
        
        result = self.spotify_tool.call_tool('spotify_get_artist_info', tool_args, self.user_id)
        
        assert result == "Artist info error: 404"

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_recommendations_success(self, mock_requests):
        """Test successful recommendations retrieval"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock recommendations response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'tracks': [
                {
                    'name': 'Recommended Song 1',
                    'artists': [{'name': 'Artist 1'}]
                },
                {
                    'name': 'Recommended Song 2',
                    'artists': [{'name': 'Artist 2'}]
                }
            ]
        }
        mock_requests.get.return_value = mock_response
        
        tool_args = {
            'seed_tracks': ['track1', 'track2'],
            'seed_artists': ['artist1'],
            'seed_genres': ['pop', 'rock'],
            'limit': 5
        }
        
        result = self.spotify_tool.call_tool('spotify_get_recommendations', tool_args, self.user_id)
        
        expected_result = "Recommended Song 1 by Artist 1\nRecommended Song 2 by Artist 2"
        assert result == expected_result
        
        # Verify correct API call
        call_args = mock_requests.get.call_args
        expected_params = {
            'limit': 5,
            'seed_tracks': 'track1,track2',
            'seed_artists': 'artist1',
            'seed_genres': 'pop,rock'
        }
        assert call_args[1]['params'] == expected_params

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_recommendations_default_limit(self, mock_requests):
        """Test recommendations with default limit"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock recommendations response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'tracks': []}
        mock_requests.get.return_value = mock_response
        
        tool_args = {'seed_genres': ['pop']}  # No limit specified
        
        self.spotify_tool.call_tool('spotify_get_recommendations', tool_args, self.user_id)
        
        # Verify default limit of 10 was used
        call_args = mock_requests.get.call_args
        assert call_args[1]['params']['limit'] == 10

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_recommendations_filters_empty_seeds(self, mock_requests):
        """Test that empty seeds are filtered out"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock recommendations response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'tracks': []}
        mock_requests.get.return_value = mock_response
        
        tool_args = {
            'seed_tracks': ['track1', '', 'track2'],  # Contains empty string
            'seed_artists': ['', 'artist1'],  # Contains empty string
            'seed_genres': ['pop', '']  # Contains empty string
        }
        
        self.spotify_tool.call_tool('spotify_get_recommendations', tool_args, self.user_id)
        
        # Verify empty strings were filtered out
        call_args = mock_requests.get.call_args
        expected_params = {
            'limit': 10,
            'seed_tracks': 'track1,track2',  # Empty string filtered out
            'seed_artists': 'artist1',  # Empty string filtered out
            'seed_genres': 'pop'  # Empty string filtered out
        }
        assert call_args[1]['params'] == expected_params

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_recommendations_failure(self, mock_requests):
        """Test failed recommendations retrieval"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_requests.get.return_value = mock_response
        
        tool_args = {'seed_genres': ['pop']}
        
        result = self.spotify_tool.call_tool('spotify_get_recommendations', tool_args, self.user_id)
        
        assert result == "Recommendation error: 400"

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_artist_top_tracks_success(self, mock_requests):
        """Test successful artist top tracks retrieval"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock top tracks response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'tracks': [
                {
                    'name': 'Top Track 1',
                    'artists': [{'name': 'Test Artist'}]
                },
                {
                    'name': 'Top Track 2',
                    'artists': [{'name': 'Test Artist'}]
                }
            ]
        }
        mock_requests.get.return_value = mock_response
        
        tool_args = {'artist_id': 'test_artist_id', 'market': 'GB'}
        
        result = self.spotify_tool.call_tool('spotify_get_artist_top_tracks', tool_args, self.user_id)
        
        expected_result = "Top Track 1 by Test Artist\nTop Track 2 by Test Artist"
        assert result == expected_result
        
        # Verify correct API call
        mock_requests.get.assert_called_once_with(
            'https://api.spotify.com/v1/artists/test_artist_id/top-tracks',
            headers=mock_headers,
            params={'market': 'GB'}
        )

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_artist_top_tracks_default_market(self, mock_requests):
        """Test artist top tracks with default market"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock top tracks response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'tracks': []}
        mock_requests.get.return_value = mock_response
        
        tool_args = {'artist_id': 'test_artist_id'}  # No market specified
        
        self.spotify_tool.call_tool('spotify_get_artist_top_tracks', tool_args, self.user_id)
        
        # Verify default market of 'US' was used
        call_args = mock_requests.get.call_args
        assert call_args[1]['params']['market'] == 'US'

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_artist_top_tracks_failure(self, mock_requests):
        """Test failed artist top tracks retrieval"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_requests.get.return_value = mock_response
        
        tool_args = {'artist_id': 'nonexistent_artist'}
        
        result = self.spotify_tool.call_tool('spotify_get_artist_top_tracks', tool_args, self.user_id)
        
        assert result == "Top track error: 404"

    def test_call_tool_unknown_tool(self):
        """Test calling an unknown tool"""
        # Mock get_app_headers
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        result = self.spotify_tool.call_tool('unknown_tool', {}, self.user_id)
        
        assert result == "Unknown tool: unknown_tool"

    @patch.dict(os.environ, {}, clear=True)
    def test_init_with_missing_env_vars(self):
        """Test initialization when environment variables are missing"""
        spotify_tool = SpotifyAppTool('test-table')
        
        assert spotify_tool.client_id is None
        assert spotify_tool.client_secret is None
        assert spotify_tool.refresh_url == 'https://accounts.spotify.com/api/token'
        assert spotify_tool.service_name == 'spotify'

    def test_call_tool_get_app_headers_without_user_id(self):
        """Test that get_app_headers is called without user_id in some methods"""
        # Note: The actual code has a bug where get_app_headers() is called without user_id
        # This test documents the current behavior
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        with patch('services.utils.tools.spotify_tools.requests') as mock_requests:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'items': []}
            mock_requests.get.return_value = mock_response
            
            self.spotify_tool.call_tool('spotify_get_user_playlists', {}, self.user_id)
            
            # Verify get_app_headers was called without arguments (which is a bug in the actual code)
            self.spotify_tool.get_app_headers.assert_called_once_with()