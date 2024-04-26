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

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    

import fastapi
import schemas
import services
import sqlalchemy.orm as orm

app = fastapi.FastAPI(title="Bandit Management API")

# Root endpoint to verify the application is running
@app.get("/")
async def root():
    return {"message": "Welcome to the Bandit Management API!"}

# Existing endpoint to create a bandit
@app.post("/api/bandits/", response_model=schemas.Bandit)
async def create_bandit(bandit: schemas.BanditCreate, db: orm.Session = fastapi.Depends(services.get_db)):
    return await services.create_bandit(bandit=bandit, db=db)



@app.post("/api/event/", response_model=schemas.UserEvent)
async def create_event(event: schemas.UserEventCreate, db: orm.Session = fastapi.Depends(services.get_db)):
    return await services.create_bandit(event=event, db=db)




# Initialize bandits on startup

# Define the startup event handler
@app.on_event("startup")
async def startup_event():
    # Create a database session
    db = SessionLocal()
    try:
        # Initialize bandits with a specified number (e.g., 10)
        services.initialize_bandits(db, n=10)
    finally:
        # Close the database session
        db.close()

# Endpoint to suggest a bandit and interact with the user
@app.post("/suggest_bandit/")
async def suggest_bandit(feedback: str = Form(...), db: Session = fastapi.Depends(services.get_db)):
    # Check if the bandits table is empty, and initialize it if needed
    if not db.query(models.Bandit).first():
        services.initialize_bandits(db)
        return {"message": "Bandits table initialized. You can now provide feedback."}
    
    # Choose a bandit using Thompson Sampling algorithm
    bandit = services.choose_bandit(db)
    print(bandit)
    
    # Parse user feedback
    feedback_lower = feedback.lower()
    if feedback_lower not in ["yes", "no"]:
        return {"message": "Invalid input. Please enter either 'yes' or 'no'."}
    
    liked = feedback_lower == "yes"
    
    # Log user event and update bandit performance for both "yes" and "no" feedback
    services.log_user_event(db, bandit.Bandit_name, liked)
    services.update_bandit_performance(db, bandit.Bandit_name, liked)  # Update for "yes" feedback
    services.update_bandit_performance(db, bandit.Bandit_name, not liked)  # Update for "no" feedback
    
    return {"message": f"Chosen bandit: {bandit.Bandit_name}, Feedback: {feedback_lower}"}



