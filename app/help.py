


@app.post("/feedback")
def give_feedback(project_id: int, bandit_id: int, liked: bool, db: Session = Depends(get_db)):
    # Log the user event and update bandit
    new_event = models.UserEvent(
        project_id=project_id,
        bandit_id=bandit_id,
        event=int(liked),
        date_time=datetime.now()
    )
    db.add(new_event)

    # Update bandit performance based on user feedback
    bandit = db.query(models.Bandit).filter_by(id=bandit_id, project_id=project_id).first()
    if bandit:
        if liked:
            bandit.alpha += 1 
        else:
            bandit.beta += 1
        bandit.n += 1
        db.commit()
    else:
        db.rollback()

    return {"message": "Feedback received successfully"}
 

# Example usage: