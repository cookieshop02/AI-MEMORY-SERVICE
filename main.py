from fastapi import FastAPI
from cache import get_cached, create_cache
from database import SessionLocal, engine, Base
from queue_worker import analyze_sentiment
from models import ChatMessage
import asyncio

Base.metadata.create_all(bind=engine) #This line tells SQLAlchemy:“Take all my ORM models and physically create their tables in the database.”

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

@app.get("/stats")
async def stats():

    db = SessionLocal()
    total_chats = db.query(ChatMessage).count()
    total_users = db.query(ChatMessage.user_id).distinct().count()
    anxiety_detection = db.query(ChatMessage).filter(ChatMessage.sentiment == "anxious").count()
    sad_detection = db.query(ChatMessage).filter(ChatMessage.sentiment == "sad").count()
    happy_detection = db.query(ChatMessage).filter(ChatMessage.sentiment == "happy").count
    excited_detection = db.query(ChatMessage).filter(ChatMessage.sentiment == "excited").count()

    return {
        "total_chats": total_chats,
        "total_users": total_users, 
        "anxiety_detection": anxiety_detection,
        "sad_detection": sad_detection,
        "happy_detection": happy_detection,
        "excited_detection": excited_detection
        }