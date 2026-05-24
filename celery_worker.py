from celery import Celery
import time


celery_app = Celery("worker", broker = "redis://localhost:6380/0", backend="redis://localhost:6380/0")

@celery_app.task
def analyze_sentiment(message):

    print("PROCESSING TASK...")

    time.sleep(5)


    if "anxious" in message.lower():
        return "anxious"
    elif "sad" in message.lower():
        return "sad"
    elif "happy" in message.lower():
        return "happy"
    elif "excited" in message.lower():
        return "excited"
    
    return "neutral"


    

    
