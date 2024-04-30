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
import numpy as np
from sqlalchemy.future import select


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

# def get_bandits(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Bandit).offset(skip).limit(limit).all()



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

# def get_user_events(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.UserEvent).offset(skip).limit(limit).all()




# #Bandit 

# """
# Bandit Initialization

# The code defines a function initialize_bandits that initializes a specified number of "bandits" in a database, 
# each with default parameters.
# The function initialize_bandits determines whether a bandit needs to be initialized based on whether an existing record 
# can be found in the database for each bandit name from 1 to n.  

# """
def initialize_bandits(db: Session, n: int):
    """
    Initialize a specified number of bandits in the database with default parameters.

    Args:
        db (Session): The SQLAlchemy session used to interact with the database.
        n (int): The number of bandits to initialize, each uniquely identified by an integer.
    """
    initialized_count = 0
    for i in range(1, n + 1):
        if not db.query(models.Bandit).filter_by(Bandit_name=str(i)).first():
            bandit = models.Bandit(Bandit_name=str(i), alpha=1.0, beta=1.0, n=0)
            db.add(bandit)
            initialized_count += 1
    db.commit()
    return initialized_count



# """
# getting Bandit tabel

# """


def get_bandits(db: Session, limit: int):
    """
    Retrieve a specified number of bandits from the database based on the provided limit.

    Args:
        db (Session): The SQLAlchemy session used to interact with the database.
        limit (int): The maximum number of bandits to retrieve, specified externally.

    Returns:
        List of Bandit objects: A list of bandits up to the specified limit.
    """
    # Query the database for bandits and limit the results to the specified limit
    bandits = db.query(models.Bandit).limit(limit).all()
    return bandits






# """
# Getting User_Interaction Table

# """

def get_UserEvent(db: Session, limit: int):
    """
    Retrieve a specified number of interactions from the database based on the provided limit.

    Args:
        db (Session): The SQLAlchemy session used to interact with the database.
        limit (int): The maximum number of bandits to retrieve, specified externally.

    Returns:
        List of Bandit objects: A list of bandits up to the specified limit.
    """
    # Query the database for bandits and limit the results to the specified limit
    UserEvent = db.query(models.UserEvent).limit(limit).all()
    return UserEvent




def sample(db: Session):
    # Query to fetch all Bandit records from the database
    bandits = db.query(models.Bandit).all()
    print(type(bandits), bandits)

    # Check if the list is not empty
    if bandits:
        # For demonstration, let's take the first Bandit from the list
        bandit = bandits[0]

        # Now use the alpha and beta attributes of the Bandit instance to generate a sample
        return np.random.beta(bandit.alpha, bandit.beta)
    else:
        # Handle the case where no bandits are available
        return None




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
    print("All bandits:", samples)
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






def get_bandit_parameters(db: Session):
    """
    Fetch the alpha and beta parameters for all bandits from the database.

    Args:
        db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
        List[Tuple[float, float]]: A list of tuples containing the alpha and beta parameters for each bandit.
    """
    bandits = db.query(models.Bandit).all()
    return [(bandit.alpha, bandit.beta) for bandit in bandits]





# #Checking Function

# if __name__ == "__main__":
#     db = database.SessionLocal()
#     try:
      
#         all_bandits = get_bandits(db, limit = 5)
#         print(all_bandits)
#     finally:
#         db.close()




# #Checking Function

# if __name__ == "__main__":
#     db = database.SessionLocal()
#     try:
      
#         all_events = get_UserEvent(db, limit = 5)
#         if get_UserEvent:
#             print("All evets in the database:")
#             for event in all_events:
#                 print(f"Event ID: {event.id}, Bandit Name: {event.Bandit_name}, Event ID: {event.event}, Event Time: {event.date_time}")
#         else:
#             print("No events are present in the database.")
#     finally:
#         db.close()



#Checking initalization

# if __name__ == "__main__":
#     db = database.SessionLocal()
#     try:
#         print("Starting initialization of bandits...")
#         initialize_bandits(db, 10)
#         print("Initialization process complete.")
#     finally:
#         db.close()




# if __name__ == "__main__":
#     db = database.SessionLocal()
#     try:
#         # Get samples using the 'sample' function
#         samples = sample(db)
#         # Check if samples were retrieved successfully
#         if samples is not None:
#             print("Sample from the database:")
#             print(samples)
#         else:
#             print("No sample could be retrieved.")
#     finally:
#         db.close()
        

# if __name__ == "__main__":
#     # Create a session instance
#     db = database.SessionLocal()
#     try:
#         chosen_bandit = choose_bandit(db)
#     finally:
#         db.close()

