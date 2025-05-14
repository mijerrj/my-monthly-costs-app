from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CostCreate(BaseModel):
    name: str
    amount: float
    merchant_name: Optional[str] = None
    description: Optional[str] = None

class CostResponse(BaseModel):
    id: int
    name: str
    amount: float
    merchant_name: Optional[str]
    description: Optional[str]
    timestamp: datetime

    class Config:
        orm_mode = True
