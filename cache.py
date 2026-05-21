chat_cache = {}

def get_cached(user_id):
    return chat_cache.get(user_id)

def create_cache(user_id, data):
    chat_cache[user_id]= data