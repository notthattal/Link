from services.utils.tools.spotify_tools import SpotifyAppTool
from services.utils.tools.gmail_tools import GmailAppTool

class AppManager():
    def __init__(self, table):
        self.table = table
        self.app_tools = {
            'spotify': SpotifyAppTool(table),
            'gmail': GmailAppTool(table)
        }

    def _get_connected_apps(self, user_id):
        response = self.table.get_item(Key={'userId': user_id})
        return response.get('Item', {}).get('connectedApps', [])
    
    def _get_user_tools_by_id(self, user_id):
        connected_apps = self._get_connected_apps(user_id)
        return self._get_user_tools_by_apps(connected_apps)

    def _get_user_tools_by_apps(self, connected_apps):
        tools = []

        for app_name, app_tool in self.app_tools.items():
            if app_name in connected_apps:
                tools.extend(app_tool.get_tools())
        
        return tools

    def get_user_tools(self, user_id=None, connected_apps=None):
        """Get tools for a user by user ID or connected apps"""
        if user_id:
            return self._get_user_tools_by_id(user_id)
        elif connected_apps:
            return self._get_user_tools_by_apps(connected_apps)
        else:
            raise ValueError("Must provide either user_id or connected_apps")

    def call_app_tool(self, tool_name, tool_args, user_id):
        service_name = tool_name.split('_')[0]
        if service_name not in self.app_tools:
            raise ValueError(f"{service_name} is not a supported app")
        
        service_tool = self.app_tools[service_name]
        return service_tool.call_tool(tool_name, tool_args, user_id)