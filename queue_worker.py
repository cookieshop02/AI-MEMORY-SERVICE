import asyncio

async def analyze_sentiment(message):

    await asyncio.sleep(3)

    if "anxious" in message.lower():
        return "anxious"
    elif "sad" in message.lower():
        return "sad"
    elif "happy" in message.lower():
        return "happy"
    elif "excited" in message.lower():
        return "excited"
    
    return "neutral"