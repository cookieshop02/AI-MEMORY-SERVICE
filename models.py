from sqlalchemy import Column, Integer, String
from database import Base

class ChatMessage(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key =True)
    user_id = Column(Integer)
    message = Column(String)
    sentiment = Column(String)
