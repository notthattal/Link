import json
import requests
from services.utils.tools.app_tool import AppTool
import os

class SpotifyAppTool(AppTool):
    def __init__(self, table):
        super().__init__(table)
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.refresh_url = 'https://accounts.spotify.com/api/token'
        self.service_name = 'spotify'

    def get_tools(self):
        """Get Spotify tool definitions for Bedrock"""
        return [
            {
                "toolSpec": {
                    "name": "spotify_add_to_playlist",
                    "description": (
                        "Use this to ADD a song to a playlist. Trigger this tool when the user asks to 'add', 'save', 'put', or 'include' a song in any playlist. "
                        "The playlist name and song title must be extracted from the user's request. "
                        "Do NOT use this when the user just wants to search or look up a song."
                    ),
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "The user's original query"},
                                "playlist_name": {"type": "string", "description": "Spotify playlist name"},
                                "track_name": {"type": "string", "description": "Spotify track name"}
                            },
                            "required": ["query", "playlist_name", "track_name"]
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "spotify_remove_from_playlist",
                    "description": "Remove a track from a Spotify playlist",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "The user's original query"},
                                "playlist_name": {"type": "string", "description": "Spotify playlist name"},
                                "track_name": {"type": "string", "description": "Spotify track name"}
                            },
                            "required": ["query", "playlist_name", "track_name"]
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "spotify_get_user_playlists",
                    "description": "Get user's Spotify playlists",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "spotify_search_tracks",
                    "description": "Only use when the user is explicitly asking to search or look up songs. !!!!!!!! DO NOT USE IF A USER ASKS TO ADD OR REMOVE !!!!!!!",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Search query"},
                                "limit": {"type": "integer", "description": "Number of results", "default": 10}
                            },
                            "required": ["query"]
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "spotify_get_artist_info",
                    "description": "Get metadata about an artist like genres, popularity, and followers",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "artist_name": {"type": "string", "description": "Spotify artist name"}
                            },
                            "required": ["artist_name"]
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "spotify_get_artist_top_tracks",
                    "description": "Get the top tracks for a Spotify artist",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "artist_name": {"type": "string", "description": "Spotify artist name"},
                                "market": {"type": "string", "description": "Market country code", "default": "US"}
                            },
                            "required": ["artist_name"]
                        }
                    }
                }
            }
        ]
    
    def search_tracks(self, tool_args, headers):
        params = {'q': tool_args['query'], 'type': 'track', 'limit': tool_args.get('limit', 10)}
        response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            tracks = data['tracks']['items']
            results = [f"{t['name']} by {t['artists'][0]['name']} - {t['uri']}" for t in tracks]
            return results
    
        return None
        
    def get_artist_id_from_name(self, artist_name, headers):
        search_resp = requests.get(
            'https://api.spotify.com/v1/search',
            headers=headers,
            params={'q': artist_name, 'type': 'artist', 'limit': 10}
        )
        if search_resp.status_code != 200:
            return None

        artists = search_resp.json()['artists']['items']
        for artist in artists:
            if artist['name'].lower() == artist_name.lower():
                return artist['id']

        return None
    
    def get_playlist_id_by_name(self, name, headers):
        response = requests.get('https://api.spotify.com/v1/me/playlists', headers=headers)
        if response.status_code == 200:
            data = response.json()
            for p in data['items']:
                if p['name'].lower() == name.lower():
                    return p['id']
        return None

    def call_tool(self, tool_name, tool_args, user_id):
        headers = self.get_app_headers(user_id)
        print(f'Calling: {tool_name}')

        if tool_name == 'spotify_add_to_playlist':
            search_results = self.search_tracks(tool_args, headers)            
            track_uri = search_results[0].split(" - ")[-1]
            playlist_id = self.get_playlist_id_by_name(tool_args['playlist_name'], headers)

            response = requests.post(
                f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
                headers=headers,
                json={'uris': [track_uri]}
            )

            return "Track added to playlist" if response.status_code == 201 else f"Error: {response.status_code}"

        elif tool_name == 'spotify_remove_from_playlist':
            search_results = self.search_tracks(tool_args, headers)            
            track_uri = search_results[0].split(" - ")[-1]
            playlist_id = self.get_playlist_id_by_name(tool_args['playlist_name'], headers)
        
            response = requests.delete(
                f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
                headers=headers,
                json={'tracks': [{'uri': track_uri}]}
            )

            return "Track removed from playlist" if response.status_code == 200 else f"Error: {response.status_code}"

        elif tool_name == 'spotify_get_user_playlists':
            response = requests.get('https://api.spotify.com/v1/me/playlists', headers=headers)
            if response.status_code == 200:
                data = response.json()
                playlists = [f"{p['name']}" for p in data['items']]
                return "\n".join(playlists)
            return f"Error getting playlists: {response.status_code}"

        elif tool_name == 'spotify_search_tracks':
            results = self.search_tracks(tool_args, headers)
            if results:
                return "\n".join(results)
            return f"Error searching for songs in spotify"

        elif tool_name == 'spotify_get_artist_info':
            artist_id = self.get_artist_id_from_name(tool_args['artist_name'], headers)
            
            if artist_id is None:
                return f"Failed to get artist info for {tool_args['artist_name']}"
            
            response = requests.get(f'https://api.spotify.com/v1/artists/{artist_id}', headers=headers)
            if response.status_code == 200:
                data = response.json()
                name = data.get('name', 'Unknown')
                genres = ", ".join(data.get('genres', [])) or "None"
                popularity = data.get('popularity', 'N/A')
                followers = f"{data.get('followers', {}).get('total', 0):,}"
                images = "\n\n".join(f"{img['url']} ({img['width']}x{img['height']})" for img in data.get('images', []))
                url = data.get('external_urls', {}).get('spotify', '')

                return (
                    f"Here is the artist information for {name}:\n"
                    f"Artist Name: {name}\n"
                    f"Genres: {genres}\n"
                    f"Popularity: {popularity}\n"
                    f"Followers: {followers}\n"
                    f"Images: \n\n{images}\n"
                    f"Spotify URL: {url}"
                )
            return f"Artist info error: {response.status_code}"

        elif tool_name == 'spotify_get_artist_top_tracks':
            artist_id = self.get_artist_id_from_name(tool_args['artist_name'], headers)
        
            if artist_id is None:
                return f"Failed to get top tracks for {tool_args['artist_name']}"
        
            market = tool_args.get('market', 'US')
            response = requests.get(
                f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks',
                headers=headers,
                params={'market': market}
            )
            if response.status_code == 200:
                data = response.json()
                return "\n".join(f"{t['name']} by {t['artists'][0]['name']}" for t in data['tracks'])
            return f"Top track error: {response.status_code}"

        return f"Unknown tool: {tool_name}"