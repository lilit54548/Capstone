import uvicorn
from sqlalchemy.orm import Session
from scipy.stats import beta as beta_distribution
import models
from fastapi import FastAPI, Depends, HTTPException
import numpy as np
# from fastapi_sqlalchemy import DBSessionMiddleware, db
#########
from database import DATABASE_URL,Base,get_db,engine
from models import Project, Bandit
from datetime import datetime 




from schemas import ( 
    ProjectInit,
    BanditsInit,
    CombinedRequest,
    BanditResponse
    )
    



app=FastAPI()
# app.add_middleware(DBSessionMiddleware, DATABASE_URL)


@app.get("/")
async def root():
    return {'message':'Hello World'}

@app.post("/create_project/",response_model=ProjectInit)
def create_project(project:ProjectInit,db:Session=Depends(get_db)):

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

# #suggest
# @app.get("/sample_bandit/{project_id}", response_model=BanditsInit)
# def sample_bandit(project_id: int, db: Session = Depends(get_db)):
#     # Fetch bandits associated with the given project ID
#     bandits = db.query(Bandit).filter(Bandit.project_id == project_id).all()
#     if not bandits:
#         return {"message": "No bandits found for this project"}

#     # Perform Thompson Sampling to choose a bandit
#     samples = [np.random.beta(bandit.alpha, bandit.beta) for bandit in bandits]

#     # Select the bandit with the highest sample
#     chosen_bandit = bandits[np.argmax(samples)]

#     return chosen_bandit  # Return the chosen bandit serialized by Pydantic



@app.get("/select_bandit/{project_id}", response_model=BanditsInit)
def select_bandit(project_id: int, db: Session = Depends(get_db)):
    # Fetch bandits associated with the given project ID
    bandits = db.query(Bandit).filter(Bandit.project_id == project_id).all()
    if not bandits:
        raise HTTPException(status_code=404, detail="No bandits found for this project.")

    # Generate samples using Thompson Sampling
    samples = [np.random.beta(bandit.alpha, bandit.beta) for bandit in bandits]

    # Use argmax to find the index of the bandit with the highest sample
    best_bandit_index = np.argmax(samples)

    # Select the bandit based on the index
    chosen_bandit = bandits[best_bandit_index]

    # Return the chosen bandit serialized as per the BanditResponse model
    return BanditsInit(
        bandit_id=chosen_bandit.id,
        project_id=chosen_bandit.project_id,
        alpha=chosen_bandit.alpha,
        beta=chosen_bandit.beta
    )



#suggest N best


#suggest
@app.get("/sample_bandit/{project_id}", response_model=BanditsInit)
def sample_bandit(project_id: int, db: Session = Depends(get_db)):
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





# @app.post("/feedback/{chosen_bandit_id}")
# def give_feedback(chosen_bandit_id: int, project_id: int, liked: bool, db: Session = Depends(get_db)):
#     # Retrieve the chosen_bandit using chosen_bandit_id
#     chosen_bandit = db.query(models.Bandit).filter(models.Bandit.bandit_id == chosen_bandit_id, models.Bandit.project_id == project_id ).first()
#     if not chosen_bandit:
#         raise HTTPException(status_code=404, detail="Bandit not found")
    
#     # Check if the chosen bandit belongs to the provided project_id
#     if chosen_bandit.project_id != project_id:
#         raise HTTPException(status_code=400, detail="Bandit does not belong to the provided project")

#     # Log the user event and update bandit
#     new_event = models.UserEvent(
#         project_id=project_id,
#         bandit_id=chosen_bandit_id,
#         event=int(liked),
        
#     )
#     db.add(new_event)

#     # Update bandit performance based on user feedback
#     if liked:
#         chosen_bandit.alpha += 1 
#     else:
#         chosen_bandit.beta += 1
#     chosen_bandit.n += 1

#     db.commit()

#     return {"message": "Feedback received successfully"}



@app.post("/feedback/{chosen_bandit_id}")
def give_feedback( liked: bool, db: Session = Depends(get_db)):
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

