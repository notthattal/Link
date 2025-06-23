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
        
        assert len(tools) == 6
        
        tool_names = [tool['toolSpec']['name'] for tool in tools]
        expected_tools = [
            'spotify_add_to_playlist',
            'spotify_remove_from_playlist',
            'spotify_get_user_playlists',
            'spotify_search_tracks',
            'spotify_get_artist_info',
            'spotify_get_artist_top_tracks'
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    @patch('services.utils.tools.spotify_tools.requests')
    def test_search_tracks_success(self, mock_requests):
        """Test successful track search helper method"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
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
        mock_requests.get.return_value = mock_response
        
        tool_args = {'query': 'test song', 'limit': 5}
        result = self.spotify_tool.search_tracks(tool_args, mock_headers)
        
        expected = ['Test Song by Test Artist - spotify:track:test123']
        assert result == expected

    @patch('services.utils.tools.spotify_tools.requests')
    def test_search_tracks_failure(self, mock_requests):
        """Test failed track search helper method"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_requests.get.return_value = mock_response
        
        tool_args = {'query': 'test song'}
        result = self.spotify_tool.search_tracks(tool_args, mock_headers)
        
        assert result is None

    @patch('services.utils.tools.spotify_tools.requests')
    def test_get_artist_id_from_name_success(self, mock_requests):
        """Test successful artist ID lookup"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'artists': {
                'items': [
                    {'name': 'Test Artist', 'id': 'artist123'},
                    {'name': 'Other Artist', 'id': 'artist456'}
                ]
            }
        }
        mock_requests.get.return_value = mock_response
        
        result = self.spotify_tool.get_artist_id_from_name('Test Artist', mock_headers)
        
        assert result == 'artist123'

    @patch('services.utils.tools.spotify_tools.requests')
    def test_get_artist_id_from_name_not_found(self, mock_requests):
        """Test artist ID lookup when artist not found"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'artists': {
                'items': [
                    {'name': 'Other Artist', 'id': 'artist456'}
                ]
            }
        }
        mock_requests.get.return_value = mock_response
        
        result = self.spotify_tool.get_artist_id_from_name('Nonexistent Artist', mock_headers)
        
        assert result is None

    @patch('services.utils.tools.spotify_tools.requests')
    def test_get_artist_id_from_name_api_failure(self, mock_requests):
        """Test artist ID lookup when API fails"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_requests.get.return_value = mock_response
        
        result = self.spotify_tool.get_artist_id_from_name('Test Artist', mock_headers)
        
        assert result is None

    @patch('services.utils.tools.spotify_tools.requests')
    def test_get_playlist_id_by_name_success(self, mock_requests):
        """Test successful playlist ID lookup"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {'name': 'My Playlist', 'id': 'playlist123'},
                {'name': 'Other Playlist', 'id': 'playlist456'}
            ]
        }
        mock_requests.get.return_value = mock_response
        
        result = self.spotify_tool.get_playlist_id_by_name('My Playlist', mock_headers)
        
        assert result == 'playlist123'

    @patch('services.utils.tools.spotify_tools.requests')
    def test_get_playlist_id_by_name_not_found(self, mock_requests):
        """Test playlist ID lookup when playlist not found"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {'name': 'Other Playlist', 'id': 'playlist456'}
            ]
        }
        mock_requests.get.return_value = mock_response
        
        result = self.spotify_tool.get_playlist_id_by_name('Nonexistent Playlist', mock_headers)
        
        assert result is None

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_add_to_playlist_success(self, mock_requests):
        """Test successful track addition to playlist"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock search response
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
        
        # Mock playlist lookup response
        playlist_response = Mock()
        playlist_response.status_code = 200
        playlist_response.json.return_value = {
            'items': [
                {'name': 'My Playlist', 'id': 'playlist123'}
            ]
        }
        
        # Mock add to playlist response
        add_response = Mock()
        add_response.status_code = 201
        
        # Set up side effects for multiple GET calls (search + playlist lookup)
        mock_requests.get.side_effect = [search_response, playlist_response]
        mock_requests.post.return_value = add_response
        
        tool_args = {
            'query': 'test song',
            'playlist_name': 'My Playlist',
            'track_name': 'Test Song'
        }
        
        result = self.spotify_tool.call_tool('spotify_add_to_playlist', tool_args, self.user_id)
        
        assert result == "Track added to playlist"

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_add_to_playlist_failure(self, mock_requests):
        """Test failed track addition to playlist"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock search response
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
        
        # Mock playlist lookup response
        playlist_response = Mock()
        playlist_response.status_code = 200
        playlist_response.json.return_value = {
            'items': [
                {'name': 'My Playlist', 'id': 'playlist123'}
            ]
        }
        
        # Mock failed add response
        add_response = Mock()
        add_response.status_code = 400
        
        mock_requests.get.side_effect = [search_response, playlist_response]
        mock_requests.post.return_value = add_response
        
        tool_args = {
            'query': 'test song',
            'playlist_name': 'My Playlist',
            'track_name': 'Test Song'
        }
        
        result = self.spotify_tool.call_tool('spotify_add_to_playlist', tool_args, self.user_id)
        
        assert result == "Error: 400"

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_remove_from_playlist_success(self, mock_requests):
        """Test successful track removal from playlist"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock search response
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
        
        # Mock playlist lookup response
        playlist_response = Mock()
        playlist_response.status_code = 200
        playlist_response.json.return_value = {
            'items': [
                {'name': 'My Playlist', 'id': 'playlist123'}
            ]
        }
        
        # Mock remove response
        remove_response = Mock()
        remove_response.status_code = 200
        remove_response.json.return_value = {}
        
        mock_requests.get.side_effect = [search_response, playlist_response]
        mock_requests.delete.return_value = remove_response
        
        tool_args = {
            'query': 'test song',
            'playlist_name': 'My Playlist',
            'track_name': 'Test Song'
        }
        
        result = self.spotify_tool.call_tool('spotify_remove_from_playlist', tool_args, self.user_id)
        
        assert result == "Track removed from playlist"

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_user_playlists_success(self, mock_requests):
        """Test successful playlist retrieval"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
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

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_user_playlists_failure(self, mock_requests):
        """Test failed playlist retrieval"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        mock_response = Mock()
        mock_response.status_code = 403
        mock_requests.get.return_value = mock_response
        
        result = self.spotify_tool.call_tool('spotify_get_user_playlists', {}, self.user_id)
        
        assert result == "Error getting playlists: 403"

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_search_tracks_success(self, mock_requests):
        """Test successful track search"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
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

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_search_tracks_failure(self, mock_requests):
        """Test failed track search"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_requests.get.return_value = mock_response
        
        tool_args = {'query': 'test search'}
        
        result = self.spotify_tool.call_tool('spotify_search_tracks', tool_args, self.user_id)
        
        assert result == "Error searching for songs in spotify"

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_artist_info_success(self, mock_requests):
        """Test successful artist info retrieval"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock artist search response
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {
            'artists': {
                'items': [
                    {'name': 'Test Artist', 'id': 'artist123'}
                ]
            }
        }
        
        # Mock artist info response
        info_response = Mock()
        info_response.status_code = 200
        info_response.json.return_value = {
            'name': 'Test Artist',
            'genres': ['pop', 'rock'],
            'popularity': 85,
            'followers': {'total': 1000000},
            'images': [
                {'url': 'http://example.com/image.jpg', 'width': 640, 'height': 640}
            ],
            'external_urls': {'spotify': 'https://open.spotify.com/artist/artist123'}
        }
        
        mock_requests.get.side_effect = [search_response, info_response]
        
        tool_args = {'artist_name': 'Test Artist'}
        
        result = self.spotify_tool.call_tool('spotify_get_artist_info', tool_args, self.user_id)
        
        expected_parts = [
            'Here is the artist information for Test Artist:',
            'Artist Name: Test Artist',
            'Genres: pop, rock',
            'Popularity: 85',
            'Followers: 1,000,000',
            'http://example.com/image.jpg (640x640)',
            'https://open.spotify.com/artist/artist123'
        ]
        
        for part in expected_parts:
            assert part in result

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_artist_info_artist_not_found(self, mock_requests):
        """Test artist info when artist not found"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock empty search response
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {
            'artists': {
                'items': []
            }
        }
        
        mock_requests.get.return_value = search_response
        
        tool_args = {'artist_name': 'Nonexistent Artist'}
        
        result = self.spotify_tool.call_tool('spotify_get_artist_info', tool_args, self.user_id)
        
        assert result == "Failed to get artist info for Nonexistent Artist"

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_artist_info_api_failure(self, mock_requests):
        """Test artist info when API fails"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock successful search but failed info retrieval
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {
            'artists': {
                'items': [
                    {'name': 'Test Artist', 'id': 'artist123'}
                ]
            }
        }
        
        info_response = Mock()
        info_response.status_code = 404
        
        mock_requests.get.side_effect = [search_response, info_response]
        
        tool_args = {'artist_name': 'Test Artist'}
        
        result = self.spotify_tool.call_tool('spotify_get_artist_info', tool_args, self.user_id)
        
        assert result == "Artist info error: 404"

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_artist_top_tracks_success(self, mock_requests):
        """Test successful artist top tracks retrieval"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock artist search response
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {
            'artists': {
                'items': [
                    {'name': 'Test Artist', 'id': 'artist123'}
                ]
            }
        }
        
        # Mock top tracks response
        tracks_response = Mock()
        tracks_response.status_code = 200
        tracks_response.json.return_value = {
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
        
        mock_requests.get.side_effect = [search_response, tracks_response]
        
        tool_args = {'artist_name': 'Test Artist', 'market': 'GB'}
        
        result = self.spotify_tool.call_tool('spotify_get_artist_top_tracks', tool_args, self.user_id)
        
        expected_result = "Top Track 1 by Test Artist\nTop Track 2 by Test Artist"
        assert result == expected_result

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_artist_top_tracks_default_market(self, mock_requests):
        """Test artist top tracks with default market"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock artist search response
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {
            'artists': {
                'items': [
                    {'name': 'Test Artist', 'id': 'artist123'}
                ]
            }
        }
        
        # Mock top tracks response
        tracks_response = Mock()
        tracks_response.status_code = 200
        tracks_response.json.return_value = {'tracks': []}
        
        mock_requests.get.side_effect = [search_response, tracks_response]
        
        tool_args = {'artist_name': 'Test Artist'}  # No market specified
        
        self.spotify_tool.call_tool('spotify_get_artist_top_tracks', tool_args, self.user_id)
        
        # Verify default market of 'US' was used
        top_tracks_call = mock_requests.get.call_args_list[1]  # Second call
        assert top_tracks_call[1]['params']['market'] == 'US'

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_artist_top_tracks_artist_not_found(self, mock_requests):
        """Test artist top tracks when artist not found"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock empty search response
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {
            'artists': {
                'items': []
            }
        }
        
        mock_requests.get.return_value = search_response
        
        tool_args = {'artist_name': 'Nonexistent Artist'}
        
        result = self.spotify_tool.call_tool('spotify_get_artist_top_tracks', tool_args, self.user_id)
        
        assert result == "Failed to get top tracks for Nonexistent Artist"

    @patch('services.utils.tools.spotify_tools.requests')
    def test_call_tool_spotify_get_artist_top_tracks_api_failure(self, mock_requests):
        """Test artist top tracks when API fails"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        # Mock successful search but failed tracks retrieval
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {
            'artists': {
                'items': [
                    {'name': 'Test Artist', 'id': 'artist123'}
                ]
            }
        }
        
        tracks_response = Mock()
        tracks_response.status_code = 404
        
        mock_requests.get.side_effect = [search_response, tracks_response]
        
        tool_args = {'artist_name': 'Test Artist'}
        
        result = self.spotify_tool.call_tool('spotify_get_artist_top_tracks', tool_args, self.user_id)
        
        assert result == "Top track error: 404"

    def test_call_tool_unknown_tool(self):
        """Test calling an unknown tool"""
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

    def test_call_tool_get_app_headers_with_user_id(self):
        """Test that get_app_headers is correctly called with user_id"""
        mock_headers = {'Authorization': 'Bearer test_token'}
        self.spotify_tool.get_app_headers = Mock(return_value=mock_headers)
        
        with patch('services.utils.tools.spotify_tools.requests') as mock_requests:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'items': []}
            mock_requests.get.return_value = mock_response
            
            self.spotify_tool.call_tool('spotify_get_user_playlists', {}, self.user_id)
            
            # Verify get_app_headers was called with user_id
            self.spotify_tool.get_app_headers.assert_called_once_with(self.user_id)