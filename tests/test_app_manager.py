import pytest
from unittest.mock import MagicMock, patch
from services.utils.tools.app_manager import AppManager

TEST_SPOTIFY_TOOLS = [
    {
        "toolSpec": {
            "name": "spotify_add_to_playlist",
            "description": "Add a track to a Spotify playlist",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "playlist_id": {"type": "string", "description": "Spotify playlist ID"},
                        "track_uri": {"type": "string", "description": "Spotify track URI"}
                    },
                    "required": ["playlist_id", "track_uri"]
                }
            }
        }
    }
]

TEST_GMAIL_TOOLS = [
    {
        "toolSpec": {
            "name": "gmail_send_email",
            "description": "Send an email using Gmail",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email address"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body text"}
                    },
                    "required": ["to", "subject", "body"]
                }
            }
        }
    }
]

@pytest.fixture
def mock_table():
    return MagicMock()

@pytest.fixture
def mock_spotify_tool():
    return MagicMock()

@pytest.fixture
def mock_gmail_tool():
    return MagicMock()

@pytest.fixture
def patched_app_manager(mock_table, mock_spotify_tool, mock_gmail_tool):
    with patch('services.utils.tools.app_manager.SpotifyAppTool', return_value=mock_spotify_tool), \
         patch('services.utils.tools.app_manager.GmailAppTool', return_value=mock_gmail_tool):
        from services.utils.tools.app_manager import AppManager
        manager = AppManager(mock_table)
        return manager, mock_spotify_tool, mock_gmail_tool

def test_get_connected_apps_returns_list(patched_app_manager):
    manager, _, _ = patched_app_manager
    manager.table.get_item.return_value = {'Item': {'connectedApps': ['spotify']}}
    assert manager._get_connected_apps('user') == ['spotify']

def test_get_connected_apps_returns_empty(patched_app_manager):
    manager, _, _ = patched_app_manager
    manager.table.get_item.return_value = {}
    assert manager._get_connected_apps('user') == []

def test_get_user_tools_by_id(patched_app_manager):
    manager, mock_spotify_tool, _ = patched_app_manager
    manager.table.get_item.return_value = {'Item': {'connectedApps': ['spotify']}}
    mock_spotify_tool.get_tools.return_value = TEST_SPOTIFY_TOOLS
    assert manager.get_user_tools(user_id='user') == TEST_SPOTIFY_TOOLS

def test_get_user_tools_by_apps(patched_app_manager):
    manager, mock_spotify_tool, mock_gmail_tool = patched_app_manager
    mock_spotify_tool.get_tools.return_value = TEST_SPOTIFY_TOOLS
    mock_gmail_tool.get_tools.return_value = TEST_GMAIL_TOOLS
    tools = manager._get_user_tools_by_apps(['spotify', 'gmail'])
    assert TEST_SPOTIFY_TOOLS[0] in tools
    assert TEST_GMAIL_TOOLS[0] in tools

def test_get_user_tools_by_user_id(patched_app_manager):
    manager, _, mock_gmail_tool = patched_app_manager
    manager.table.get_item.return_value = {'Item': {'connectedApps': ['gmail']}}
    mock_gmail_tool.get_tools.return_value = TEST_GMAIL_TOOLS
    assert manager.get_user_tools(user_id='user') == TEST_GMAIL_TOOLS

def test_get_user_tools_by_connected_apps(patched_app_manager):
    manager, _, mock_gmail_tool = patched_app_manager
    mock_gmail_tool.get_tools.return_value = TEST_GMAIL_TOOLS
    assert manager.get_user_tools(connected_apps=['gmail']) == TEST_GMAIL_TOOLS

def test_get_user_tools_raises_error(patched_app_manager):
    manager, _, _ = patched_app_manager
    with pytest.raises(ValueError):
        manager.get_user_tools()

def test_call_app_tool_valid(patched_app_manager):
    manager, _, mock_gmail_tool = patched_app_manager
    mock_gmail_tool.call_tool.return_value = 'success'
    args = {'to': 'a@b.com', 'subject': 'Test', 'body': 'Hello'}
    result = manager.call_app_tool('gmail_send_email', args, 'user')
    assert result == 'success'

def test_call_app_tool_invalid(patched_app_manager):
    manager, _, _ = patched_app_manager
    with pytest.raises(ValueError):
        manager.call_app_tool('dropbox_send_file', {}, 'user')