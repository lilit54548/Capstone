import uvicorn
from sqlalchemy.orm import Session
from scipy.stats import beta 
import models
from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List
from matplotlib import pyplot as plt
from fastapi.responses import StreamingResponse
import io
import numpy as np

# from fastapi_sqlalchemy import DBSessionMiddleware, db
#########
from database import DATABASE_URL,Base,get_db,engine
from models import Project, Bandit
from datetime import datetime 
from models import _add_tables

_add_tables()



from schemas import ( 
    ProjectInit,
    BanditsInit,
    UserEvent,
    UpdatePriors

    )
    



app=FastAPI()



@app.get("/")
def root():
    return {'message':'Hello World'}

@app.post("/create_project/",response_model=ProjectInit)
def create_project(project:ProjectInit,db:Session=Depends(get_db)):
    """
    Creates a new project and its associated bandits in the database.

    This endpoint accepts a project description and the quantity of bandits to be associated with the project,
    creates a new project record, and initializes the specified number of bandits with unique IDs and linking them to the project.

    Parameters:
    - project (ProjectInit): A model containing the project description and the quantity of bandits.

    Returns:
    - ProjectInit: A model containing the newly created project's details including its ID, description, and the quantity of bandits.
    """

    # adding new project in project table
    new_project=Project(
        project_description=project.project_description,
        bandits_qty=project.bandits_qty
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    # adding new project in bandits table
    for i in range(1, new_project.bandits_qty+1):
        bandit_schema=BanditsInit(bandit_id=i,project_id=new_project.project_id)
        new_bandit=Bandit(
            bandit_id=bandit_schema.bandit_id,
            project_id=bandit_schema.project_id
        )
        print(f'adding bandit {i} for {new_project.project_id}')
        db.add(new_bandit)
        db.commit()
        db.refresh(new_bandit)

   

    return new_project





@app.get("/sample_bandit/{project_id}", response_model=BanditsInit)
def sample_bandit(project_id: int, db: Session = Depends(get_db)):
    """
    Samples a bandit for a given project using Thompson Sampling.

    Retrieves all bandits associated with the specified project ID, applies Thompson Sampling to select one,
    and returns the chosen bandit's details.

    Parameters:
    - project_id (int): The ID of the project from which to sample a bandit.

    Returns:
    - BanditsInit: The chosen bandit's details if successful; otherwise, a message indicating no bandits were found.
    """
    # Fetch bandits associated with the given project ID
    global chosen_bandit
    
    bandits = db.query(Bandit).filter(Bandit.project_id == project_id).all()
    if not bandits:
        return {"message": "No bandits found for this project"}

    # Perform Thompson Sampling to choose a bandit
    samples = [np.random.beta(bandit.alpha, bandit.beta) for bandit in bandits]

    # Select the bandit with the highest sample
    chosen_bandit = bandits[np.argmax(samples)]

    return chosen_bandit  # Return the chosen bandit serialized by Pydantic




@app.post("/feedback/{chosen_bandit_id}")
def give_feedback( liked: bool, db: Session = Depends(get_db)):
    """
    Records user feedback for a bandit and updates its performance parameters.

    Retrieves the specified bandit by ID, logs the user's feedback, and updates the bandit's alpha or beta value based on the feedback.

    Parameters:
    - chosen_bandit_id (int): The ID of the bandit on which to give feedback.
    - liked (bool): Whether the user liked the bandit's output (True) or not (False).

    Returns:
    - dict: A message indicating that the feedback was successfully received.
    """
    global chosen_bandit
    bandit = db.query(models.Bandit).filter(models.Bandit.bandit_id == chosen_bandit.bandit_id, models.Bandit.project_id == chosen_bandit.project_id ).first()
    # Retrieve the chosen_bandit using chosen_bandit_id
    if not chosen_bandit:
        raise HTTPException(status_code=404, detail="Bandit not found")
    

    # Log the user event and update bandit
    new_event = models.UserEvent(
        project_id=chosen_bandit.project_id,
        bandit_id=chosen_bandit.bandit_id,
        event=int(liked),
        
    )
    db.add(new_event)

    # Update bandit performance based on user feedback
    if liked:
        bandit.alpha += 1 
    else:
        bandit.beta += 1
    bandit.n += 1

    db.commit()

    return {"message": "Feedback received successfully"}



@app.get("/select_bandits/{project_id}", response_model=List[BanditsInit])
def select_bandits(project_id: int, n: int = Query(1, gt=0), db: Session = Depends(get_db)):
    """
    Selects the top 'n' optimal bandits for a given project using Thompson Sampling.

    This endpoint retrieves all bandits associated with the specified project ID,
    applies Thompson Sampling to determine which bandits have the highest probabilities of success,
    and returns the selected bandits' details.

    Parameters:
    - project_id (int): The unique identifier of the project for which bandits are to be selected.
    - n (int): The number of top bandits to select.

    Returns:
    - List[BanditsInit]: A list of models containing the details of the selected bandits, including their IDs,
      project IDs, and the alpha and beta parameters used in Thompson Sampling.
    """
    # Fetch all bandit instances associated with the specified project ID from the database.
    bandits = db.query(Bandit).filter(Bandit.project_id == project_id).all()
    
    # If no bandits are found for the project, raise an HTTP 404 error to indicate "Not Found".
    if not bandits:
        raise HTTPException(status_code=404, detail="No bandits found for this project.")

    # Perform Thompson Sampling: Generate a beta-distributed random sample for each bandit based on their alpha and beta parameters.
    samples = [(np.random.beta(bandit.alpha, bandit.beta), bandit) for bandit in bandits]

    # Sort the bandits by their sample values in descending order and select the top 'n' bandits.
    top_bandits = sorted(samples, key=lambda x: x[0], reverse=True)[:n]

    # Return the selected bandits' information, formatted according to the BanditsInit response model.
    return [BanditsInit(
        bandit_id=bandit.bandit_id,
        project_id=bandit.project_id,
        alpha=bandit.alpha,
        beta=bandit.beta
    ) for _, bandit in top_bandits]




@app.get("/plot_bandits/{project_id}")
def generate_bandit_plot(project_id: int, db: Session = Depends(get_db)):
    """
    Fetches bandits for a specific project and plots their beta distributions.
    
    Parameters:
    - project_id (int): The unique identifier of the project.

    Returns:
    - StreamingResponse: A PNG image of the beta distributions.
    """
    # Fetch all bandits associated with the specified project ID from the database
    bandits = db.query(Bandit).filter(Bandit.project_id == project_id).all()

    # Check if any bandits are found
    if not bandits:
        raise HTTPException(status_code=404, detail="No bandits found for this project.")

    # Prepare to plot
    x = np.linspace(0, 1, 200)
    plt.figure(figsize=(10, 6))  # Set the figure size for better clarity

    for bandit in bandits:
        # Calculate the beta distribution for each bandit
        y = beta.pdf(x, bandit.alpha, bandit.beta)
        # Plot the beta distribution and annotate it
        plt.plot(x, y, label=f"Bandit ID: {bandit.id}, Alpha: {bandit.alpha}, Beta: {bandit.beta}")

    # Setting up the plot title and labels
    plt.title(f"Bandit distributions for project {project_id}")
    plt.xlabel("Probability")
    plt.ylabel("Density")
    plt.legend()

    # Save the plot to a BytesIO buffer and return it as a StreamingResponse
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=400)
    plt.close()
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")