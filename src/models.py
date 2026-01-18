from pydantic import BaseModel, Field
from typing import List, Optional

class BusinessIdea(BaseModel):
    title: str = Field(description="Name of the project")
    description: str = Field(description="Elevator pitch")
    target_niche: str
    
    # Metrics
    score_feasibility: int = Field(description="Technical ease (1-10)")
    score_moat: int = Field(description="Defensibility (1-10)")
    score_market: int = Field(description="Revenue potential (1-10)")
    score_overall: float = Field(description="Average score")
    
    critique: Optional[str] = None
    round_id: int = 0
    iteration_count: int = 0

class BattleConfig(BaseModel):
    niche: str
    max_rounds: int = 2
    max_iterations: int = 2

class BattleState(BaseModel):
    config: BattleConfig
    current_round: int = 1
    current_iteration: int = 0
    
    current_idea: Optional[BusinessIdea] = None
    
    # NEW: Stores the final "Winner" of each round
    completed_ideas: List[BusinessIdea] = [] 
    
    # NEW: Stores EVERY version (Iter 1, Iter 2...) for review
    all_iterations: List[BusinessIdea] = [] 
    
    messages: List[str] = []