from typing import TYPE_CHECKING, List

import database as database
import models as models

from sqlalchemy.orm import Session
import models
import schemas
import numpy as np
import datetime
import random
from datetime import datetime
from scipy.stats import beta

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def _add_tables():
    return database.Base.metadata.create_all(bind=database.engine)



def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()





async def create_bandit(
        bandit: schemas.BanditCreate, db: "Session"
) -> schemas.Bandit:
    bandit = models.Bandit(**bandit.dict())
    db.add(bandit)
    db.commit()
    db.refresh(bandit)
    return schemas.Bandit.from_orm(bandit)

def get_bandits(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Bandit).offset(skip).limit(limit).all()




def create_user_event(db: Session, event: schemas.UserEventCreate):
    """_summary_

    Args:
        db (Session): _description_
        event (schemas.UserEventCreate): _description_

    Returns:
        _type_: _description_
    """    
    db_event = models.UserEvent(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_user_events(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.UserEvent).offset(skip).limit(limit).all()




#Bandit 



def initialize_bandits(db: Session, n: int):
    """
    Initialize a specified number of bandits in the database with default parameters.

    Args:
        db (Session): The SQLAlchemy session used to interact with the database.
        n (int): The number of bandits to initialize, each uniquely identified by an integer.

    """
    # Loop over the specified range starting from 1 up to and including n
    for i in range(1, n+1):
        # Check if there is already a bandit with the current name (i) in the database
        if not db.query(models.Bandit).filter_by(Bandit_name=i).first():
            # If no such bandit exists, create a new bandit with default values
            bandit = models.Bandit(Bandit_name=i, alpha=1.0, beta=1.0, n=0)
            # Add the new bandit to the database session
            db.add(bandit)
    # Commit all changes made during the session to the database to make them permanent
    db.commit()


def sample(db: Session):
    # Perform Thompson Sampling or any other sampling technique
    # For simplicity, let's just return a random value between 0 and 1
    bandit = db.query(models.Bandit).all()
    sample = np.random.beta(bandit.alpha, bandit.beta) 
    return sample



def choose_bandit(db: Session):
    """
    Select a bandit based on Thompson Sampling.

    Args:
        db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
        The selected Bandit object after performing Thompson Sampling.
    """
    # Retrieve all bandit records from the database
    bandits = db.query(models.Bandit).all()
    
    # Thompson Sampling: sample from the posterior distribution of each bandit and select the one with the highest sample
    samples = [sample(db) for bandit in bandits]  # Corrected variable name
    chosen_bandit = bandits[np.argmax(samples)]

    # Print all bandits and the chosen one for debugging purposes
    print("All bandits:", [bandit.Bandit_name for bandit in bandits])
    print("Chosen bandit:", chosen_bandit.Bandit_name)

    return chosen_bandit




def log_user_event(db: Session, Bandit_name: int, liked: bool):
    new_event = models.UserEvent(
        Bandit_name=Bandit_name,
        event=int(liked),
        date_time=datetime.now()
    )
    db.add(new_event)
    db.commit()
    return new_event

def update_bandit_performance(db: Session, Bandit_name: int, liked: bool):
    bandit = db.query(models.Bandit).filter_by(Bandit_name=Bandit_name).first()
    if bandit:
        bandit.alpha += 1 if liked else 0
        bandit.beta += 0 if liked else 1
        bandit.n += 1
        db.commit()




# The rest of the functions remain unchanged

if __name__ == "__main__":
    # Create a session instance
    db = database.SessionLocal()
    try:
        chosen_bandit = choose_bandit(db)
        print(f"Chosen Bandit: {chosen_bandit.Bandit_name}")
    finally:
        db.close()

if __name__ == "__main__":
    # Create a session instance
    db = database.SessionLocal()
    try:
        # Check if any bandits were initialized and added to the database
        if initialize_bandits(db, 10):
            print("Bandits were initialized and added to the database.")
        else:
            print("No new bandits were added to the database.")
            
        sample =   sample(db = db)
        print(f"Chosen Bandit: {chosen_bandit.Bandit_name}")

    finally:
        db.close()


#get bandits table arandzin function
#get user_interactions