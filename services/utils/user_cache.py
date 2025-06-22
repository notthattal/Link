class UserToolsCache:
    def __init__(self):
        self.cache = {}
    
    def set_user_tools(self, user_id, tools):
        self.cache[user_id] = tools
    
    def get_user_tools(self, user_id):
        return self.cache.get(user_id, [])

user_tools_cache = UserToolsCache()