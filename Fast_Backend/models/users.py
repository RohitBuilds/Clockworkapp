from pydantic import BaseModel,Field
from typing import Union
from sqlalchemy import  Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True,index=True)
    username = Column(String,index=True)
    email = Column(String,index=True)
    password = Column(String,index=True)