from fastapi import FastAPI
from cache import get_cached, create_cache
from database import SessionLocal, engine, Base
from queue_worker import analyze_sentiment
from models import ChatMessage
import asyncio



app = FastAPI()

@app.post("/chat")
async def chat(user_id:int , message:str):

    cached = get_cached(user_id)

    if cached:
        print("Cache hit")
        return cached
    else:
        print("Cache miss/ new")

    db = SessionLocal()
    sentiment = await analyze_sentiment(message)

    msg = ChatMessage(user_id=user_id, message=message, sentiment=sentiment)
    db.add(msg)
    db.commit()

    response = { 
        message: message,
        sentiment: sentiment
    }

    create_cache(user_id, response)

    return response


@app.get("/history/{user_id}")
async def history(user_id: int):

    db = SessionLocal()
    messages = db.query(ChatMessage).filter(ChatMessage.user_id == user_id).all()
    return messages