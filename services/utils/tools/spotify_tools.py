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
            },
            {
                "toolSpec": {
                    "name": "spotify_remove_from_playlist",
                    "description": "Remove a track from a Spotify playlist",
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
                    "description": "Search for tracks on Spotify",
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
                    "name": "spotify_get_audio_features",
                    "description": "Get audio features for a track like tempo, energy, valence",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "track_uri": {"type": "string", "description": "Spotify track URI"}
                            },
                            "required": ["track_uri"]
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
                                "artist_id": {"type": "string", "description": "Spotify artist ID"}
                            },
                            "required": ["artist_id"]
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "spotify_get_recommendations",
                    "description": "Get track recommendations based on seed tracks, artists, or genres",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "seed_tracks": {"type": "array", "items": {"type": "string"}, "description": "Seed track IDs"},
                                "seed_artists": {"type": "array", "items": {"type": "string"}, "description": "Seed artist IDs"},
                                "seed_genres": {"type": "array", "items": {"type": "string"}, "description": "Seed genres"},
                                "limit": {"type": "integer", "description": "Number of recommendations", "default": 10}
                            }
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
                                "artist_id": {"type": "string", "description": "Spotify artist ID"},
                                "market": {"type": "string", "description": "Market country code", "default": "US"}
                            },
                            "required": ["artist_id"]
                        }
                    }
                }
            }
        ]

    def call_tool(self, tool_name, tool_args, user_id):
        headers = self.get_app_headers(user_id)

        if tool_name == 'spotify_add_to_playlist':
            search_results = self.call_tool("spotify_search_tracks", {"query": tool_args['query']}, user_id)
            lines = search_results.splitlines()
            first_uri = lines[0].split(" - ")[-1]
            track_uri = first_uri.split(':')[-1]
        
            response = requests.post(
                f'https://api.spotify.com/v1/playlists/{tool_args["playlist_id"]}/tracks',
                headers=headers,
                json={'uris': [track_uri]}
            )

            return "Track added to playlist" if response.status_code == 201 else f"Error: {response.status_code}"

        elif tool_name == 'spotify_remove_from_playlist':
            search_results = self.call_tool("spotify_search_tracks", {"query": tool_args['query']}, user_id)
            lines = search_results.splitlines()
            first_uri = lines[0].split(" - ")[-1]
            track_uri = first_uri.split(':')[-1]
        
            response = requests.delete(
                f'https://api.spotify.com/v1/playlists/{tool_args["playlist_id"]}/tracks',
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
            params = {'q': tool_args['query'], 'type': 'track', 'limit': tool_args.get('limit', 10)}
            response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                tracks = data['tracks']['items']
                results = [f"{t['name']} by {t['artists'][0]['name']} - {t['uri']}" for t in tracks]
                return "\n".join(results)
            return f"Search error: {response.status_code}"

        elif tool_name == 'spotify_get_audio_features':
            search_results = self.call_tool("spotify_search_tracks", {"query": tool_args}, user_id)
            lines = search_results.splitlines()
            first_uri = lines[0].split(" - ")[-1]
            track_id = first_uri.split(':')[-1]

            response = requests.get(f'https://api.spotify.com/v1/audio-features/{track_id}', headers=headers)

            if response.status_code == 200:
                return response.json()
            return f"Audio feature error: {response.status_code}"

        elif tool_name == 'spotify_get_artist_info':
            response = requests.get(f'https://api.spotify.com/v1/artists/{tool_args["artist_id"]}', headers=headers)
            if response.status_code == 200:
                return response.json()
            return f"Artist info error: {response.status_code}"

        elif tool_name == 'spotify_get_recommendations':
            params = {
                'limit': tool_args.get('limit', 10),
                'seed_tracks': ','.join([s for s in tool_args.get('seed_tracks', []) if s]),
                'seed_artists': ','.join([s for s in tool_args.get('seed_artists', []) if s]),
                'seed_genres': ','.join([s for s in tool_args.get('seed_genres', []) if s]),
            }
            response = requests.get('https://api.spotify.com/v1/recommendations', headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                return "\n".join(f"{t['name']} by {t['artists'][0]['name']}" for t in data['tracks'])
            
            return f"Recommendation error: {response.status_code}"

        elif tool_name == 'spotify_get_artist_top_tracks':
            market = tool_args.get('market', 'US')
            response = requests.get(
                f'https://api.spotify.com/v1/artists/{tool_args["artist_id"]}/top-tracks',
                headers=headers,
                params={'market': market}
            )
            if response.status_code == 200:
                data = response.json()
                return "\n".join(f"{t['name']} by {t['artists'][0]['name']}" for t in data['tracks'])
            return f"Top track error: {response.status_code}"

        return f"Unknown tool: {tool_name}"