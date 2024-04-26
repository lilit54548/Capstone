from pydantic import BaseModel
from datetime import datetime

class BanditBase(BaseModel):
    Bandit_name: str

class BanditCreate(BanditBase):
    alpha: float = 1.0
    beta: float = 1.0
    n: int = 0

class Bandit(BanditBase):
    alpha: float
    beta: float
    n: int

    class Config:
        from_attributes = True

class UserEventBase(BaseModel):
    Bandit_name: str
    event: int

class UserEventCreate(UserEventBase):
    pass

class UserEvent(UserEventBase):
    date_time: datetime

    class Config:
        from_attributes = True
