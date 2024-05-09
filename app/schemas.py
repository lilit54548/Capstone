from pydantic import (BaseModel,
                      conint # integer constraint
                      )
from typing import Optional
from datetime import datetime 

class ProjectInit(BaseModel):
    project_description: str
    bandits_qty: conint(gt=1)

    class Config:
        from_attributes=True

class BanditsInit(BaseModel):
    bandit_id: conint(ge=1)
    project_id: conint(ge=1)
    alpha: float = 1.0
    beta: float = 1.0

    class Config:
        from_attributes=True



    
class UserEvent(BaseModel):
    project_id: int
    bandit_id: int
    event: int
    
class UpdatePriors(BaseModel):
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