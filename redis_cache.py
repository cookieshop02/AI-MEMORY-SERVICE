import redis
import json

r = redis.Redis(host ="localhost", port = 6380, decode_responses = True)

#store cache
def create_cache(user_id, messages):
    
    serialized = []
    for msg in serialized:
        serialized.append({
            "message": msg.message,
            "sentiment": msg.sentiment
        })

    r.set(
        f"user:{user_id}",
        json.dumps(serialized)
        ex = 60
    )

#retreive cache
def get_cached(user_id):

    data = r.get(f"user:{user_id}")

    if data:
        return json.loads(data)
    
    return None