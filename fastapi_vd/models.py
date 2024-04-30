import datetime as dt
import sqlalchemy as sql
import database

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class Bandit(Base):
    __tablename__ = "bandits"

    Bandit_name = Column(Integer, primary_key=True, index=True)
    alpha = Column(Float, default=1.0)
    beta = Column(Float, default=1.0)
    n = Column(Integer, default=0)

    
    def __repr__(self):
        return f"<Bandit(Bandit_name={self.Bandit_name}, alpha={self.alpha}, beta={self.beta}, n={self.n})>"

       


class UserEvent(Base):
    __tablename__ = "user_events"

    id = Column(Integer, primary_key=True, index=True)
    Bandit_name = Column(Integer, index=True)
    event = Column(Integer)
    date_time = Column(DateTime(timezone=True), server_default=func.now())
