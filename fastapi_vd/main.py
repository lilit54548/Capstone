from sqlalchemy.orm import Session

# Assuming these modules are set up correctly in your project.
from database import SessionLocal
import models
import schemas
import services
import  sqlalchemy.orm as orm
from typing import TYPE_CHECKING, List
import fastapi
from fastapi import Form 
from scipy.stats import beta


if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    

import fastapi
import schemas
import services
import sqlalchemy.orm as orm

from fastapi.responses import StreamingResponse
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

import io

app = fastapi.FastAPI(title="Bandit Management API")


@app.get("/")
async def root():
    return {"message": "Welcome to the Bandit Management API"}



@app.post("/api/bandits/", response_model=schemas.Bandit)
async def create_bandit(bandit: schemas.BanditCreate, db: orm.Session = fastapi.Depends(services.get_db)):
    # Ensure all internal handling of Bandit_name now expects an integer
    return await services.create_bandit(bandit=bandit, db=db)

@app.post("/api/event/", response_model=schemas.UserEvent)
async def create_user_event(event: schemas.UserEventCreate, db: orm.Session = fastapi.Depends(services.get_db)):
    return  services.create_user_event(event=event, db=db)


@app.get("/bandits/", response_model=List[schemas.Bandit])
def read_bandits(limit: int = 5, db: Session = fastapi.Depends(services.get_db)):
    """
    Retrieve a list of bandits from the database.
    Args:
        limit (int): The maximum number of bandits to return.
        db (Session): Dependency injection of the database session.

    Returns:
        List of Bandit objects: The retrieved bandits up to the specified limit.
    """
    bandits = services.get_bandits(db, limit)
    return bandits



@app.get("/user_events/", response_model=List[schemas.UserEvent])
def read_user_events(limit: int = 5, db: Session = fastapi.Depends(services.get_db)):
    """
    Retrieve a list of user events from the database.

    Args:
        limit (int): The maximum number of user events to return.
        db (Session): Dependency injection of the database session.

    Returns:
        List[schemas.UserEvent]: A list of user event objects up to the specified limit.
    """
    user_events = services.get_UserEvent(db, limit)
    return user_events





# Initialize bandits on startup


@app.post("/initialize_bandits/")
def initialize_bandits_api(n: int, db: Session = fastapi.Depends(services.get_db)):
    """
    Endpoint to initialize a specified number of bandits in the database.

    Args:
        n (int): The number of bandits to initialize.
        db (Session): Dependency injection of the database session.

    Returns:
        str: Confirmation message indicating the number of bandits initialized.
    """
    services.initialize_bandits(db, n)
    return {"message": f"{n} bandits initialized successfully."}

# # Define the startup event handler
# @app.on_event("startup")
# async def startup_event():
#     # Create a database session
#     db = SessionLocal()
#     try:
#         # Initialize bandits with a specified number (e.g., 10)
#         services.initialize_bandits(db, n=10)
#     finally:
#         # Close the database session
#         db.close()


@app.post("/suggest_bandit/")
async def suggest_bandit(feedback: str = Form(...), db: Session = fastapi.Depends(services.get_db)):
    # Ensure there is at least one bandit in the database
    if not db.query(models.Bandit).first():
        services.initialize_bandits(db)
        return {"message": "Bandits table initialized. You can now provide feedback."}

    # Choose a bandit using the choose_bandit function
    bandit = services.choose_bandit(db)
    if bandit is None:
        return {"message": "No available bandit to choose from."}
    
    # Process feedback
    feedback_lower = feedback.lower()
    if feedback_lower not in ["yes", "no"]:
        return {"message": "Invalid input. Please enter either 'yes' or 'no'."}
    
    # Assuming log_user_event and update_bandit_performance need feedback to be in specific format
    feedback_int = 1 if feedback_lower == "yes" else 0
    
    # Log the user event and update the bandit performance based on the feedback
    services.log_user_event(db, bandit.Bandit_name, feedback_int)
    services.update_bandit_performance(db, bandit.Bandit_name, feedback_int)

    # Return a message with the chosen bandit and the feedback received
    return {"message": f"Chosen bandit: {bandit.Bandit_name}, Feedback: {feedback_lower}"}


@app.get("/plot_bandits/")
def plot_bandits(db: Session = fastapi.Depends(services.get_db)):
    """
    Generate a plot showing the beta distributions of bandits based on their alpha and beta parameters.

    Args:
        db (Session): Dependency injection of the database session.

    Returns:
        StreamingResponse: Returns an image stream of the plot.
    """
    params = services.get_bandit_parameters(db)
    plt.figure(figsize=(10, 6))
    x = [i / 1000.0 for i in range(1001)]  # Generate x values from 0 to 1

    # Plot beta distributions for each bandit
    for alpha, beta_params in params:
        y = [beta.pdf(xi, alpha, beta_params) for xi in x]
        plt.plot(x, y, label=f'a={alpha}, b={beta_params}')

    plt.title("Beta Distributions of Bandits")
    plt.xlabel("Value")
    plt.ylabel("Probability Density")
    plt.legend()

    # Save plot to a BytesIO buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    # Return plot as a streaming response
    return StreamingResponse(buf, media_type="image/png")