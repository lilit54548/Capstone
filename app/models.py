from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import datetime as dt

# Local Imports

from database import Base, engine


class Project(Base):
    """
    Represents a project in the database.

    Attributes:
        project_id (int): Unique identifier for the project, automatically generated.
        project_description (str): A brief description of the project.
        bandits_qty (int): Quantity of bandits involved in the project.
        start_date (datetime): The date and time when the project starts, set to the current time by default.
    """
    __tablename__ = "projects"
    project_id = Column(Integer, primary_key=True, index=True)
    project_description = Column(String)
    bandits_qty = Column(Integer)
    start_date = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Project(Project Id={self.project_id}, ProjectDescription={self.project_description}, NumberOfBandits={self.bandits_qty})>"

class Bandit(Base):
    __tablename__ = "bandits"
    id = Column(Integer, primary_key=True, index=True)
    bandit_id = Column(Integer, nullable=False)
    project_id = Column(Integer, ForeignKey('projects.project_id'), nullable=False)
    alpha = Column(Float, default=1.0)
    beta = Column(Float, default=1.0)
    n = Column(Integer, default=0)
    updated_date = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Bandit(Bandit Id={self.bandit_id}, Project Id={self.project_id}, Alpha={self.alpha}, Beta={self.beta}, N={self.n})>"

class UserEvent(Base):
    __tablename__ = "user_events"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.project_id'), nullable=False)
    bandit_id = Column(Integer)
    event = Column(Integer)
    event_date = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<UserEvent(ID={self.id}, Project ID={self.project_id}, Bandit ID={self.bandit_id}, Event={self.event}, Event Date={self.event_date})>"

# Drop and recreate schema if necessary
recreate = False

if recreate:
    Base.metadata.drop_all(engine)
    print('The Schema is deleted')
    print('new schema us created')

   
Base.metadata.create_all(bind=engine) 

