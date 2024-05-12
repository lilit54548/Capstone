from pydantic import (BaseModel,
                      conint # integer constraint
                      )
from typing import Optional
from datetime import datetime 

class ProjectInit(BaseModel):
  """
    Initialization model for creating a new project with basic details.
    
    Attributes:
        project_description (str): A brief description of the project.
        bandits_qty (conint(gt=1)): The quantity of bandits involved in the project, must be greater than 1.
    """
    project_description: str
    bandits_qty: conint(gt=1)

    class Config:
        from_attributes=True


class BanditsInit(BaseModel):
   """
    Initialization model for creating a new bandit associated with a project.
    
    Attributes:
        bandit_id (conint(ge=1)): A unique identifier for the bandit, must be greater than or equal to 1.
        project_id (conint(ge=1)): The identifier of the project this bandit is part of, must be greater than or equal to 1.
        alpha (float, default=1.0): The alpha parameter for the bandit's beta distribution.
        beta (float, default=1.0): The beta parameter for the bandit's beta distribution.
    """
    bandit_id: conint(ge=1)
    project_id: conint(ge=1)
    alpha: float = 1.0
    beta: float = 1.0

    class Config:
        from_attributes=True



    
class UserEvent(BaseModel):
    """
      Model representing an event triggered by a user in relation to a bandit within a project.
    
      Attributes:
        project_id (int): The identifier for the project this event is associated with.
        bandit_id (int): The identifier of the bandit associated with this event.
        event (int): An integer representing the type of event that occurred.
    """
    project_id: int
    bandit_id: int
    event: int
    
class UpdatePriors(BaseModel):
  """
    Model for updating the priors (alpha and beta) of a bandit based on new data.
    
    Attributes:
        alpha (float): Updated alpha value reflecting prior or accumulated knowledge of success.
        beta (float): Updated beta value reflecting prior or accumulated knowledge of failures.
        n (int): The number of additional trials or interactions since the last update.
  """
    alpha: float  
    beta: float  
    n: int 


   

# if __name__=='__main__':

#     def create_bandits_list(project_id: int, n: int, alpha: float = 1.0, beta: float = 1.0):
#         return 

#     # Example usage
#     project_id = 5  # Example project_id which is greater than 1
#     n = 2  # Create 10 bandits
#     bandits_list = create_bandits_list(project_id, n)
#     print(bandits_list)
