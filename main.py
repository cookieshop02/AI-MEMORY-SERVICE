from fastapi import FastAPI, BackgroundTasks
from redis_cache import get_cached, create_cache
from database import SessionLocal, engine, Base
from celery_worker import analyze_sentiment
from models import ChatMessage
from pydantic import BaseModel
import asyncio

Base.metadata.create_all(bind=engine) #This line tells SQLAlchemy:“Take all my ORM models and physically create their tables in the database.”

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: int
    message: str

def process_sentiment(message_id, message):

    db = SessionLocal()

    sentiment = analyze_sentiment.delay(message).get()
    print(f"BACKGROUND TASK RESULT: {sentiment}")

    target_message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    target_message.sentiment = sentiment
    db.commit()
    db.close()
    return(f"UPDATED BACKGROUND TASK: {sentiment}")
    
    

@app.post("/chat")
async def chat(data: ChatRequest, background_tasks: BackgroundTasks):

    user_id = data.user_id
    message = data.message

    db = SessionLocal()

    cached = get_cached(user_id)

    if cached:
        print("Cache hit")
        previous_messages = cached
    else:
        print("Cache miss/ new")
        previous_messages = db.query(ChatMessage).filter(ChatMessage.user_id == data.user_id).all()
        create_cache(user_id, previous_messages)

    print("PREVIOUS MESSAGES")
    for msg in previous_messages:
        print(msg.message)

    if len(previous_messages) >= 3:
        bot_response = "I remember our convo!"
    else:
        bot_response = "Tell me more!"

    msg = ChatMessage(user_id=user_id, message=message, sentiment="processing")
    db.add(msg)
    db.commit()
    db.refresh(msg) #auto generate id for the new message and update the msg object with it

    background_tasks.add_task(process_sentiment,msg.id, message)

    previous_messages.append(msg)
    create_cache(user_id, previous_messages)

    response = { 
        "message": message,
        "sentiment status": "processing",
        "bot_response": bot_response
    }

    db.close()

    return response

@app.get("/messages/{user_id}")
async def get_messages(user_id: int):

    db = SessionLocal()
    messages = db.query(ChatMessage).filter(ChatMessage.user_id == user_id).all()

    result = []
    for msg in messages:
        result.append({
            "message": msg.message,
            "sentiment": msg.sentiment
        })

    db.close()
    return result

@app.get("/history/{user_id}")
async def history(user_id : int):

    user_id = user_id

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