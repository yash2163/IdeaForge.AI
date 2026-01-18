from pydantic import BaseModel, Field
from typing import List, Optional

class BusinessIdea(BaseModel):
    title: str = Field(description="Name of the project")
    description: str = Field(description="Elevator pitch")
    target_niche: str
    
    # Expanded Metrics (1-10)
    score_feasibility: int = Field(description="Technical ease (10=Easy, 1=Impossible)")
    score_moat: int = Field(description="Defensibility (10=Hard to copy, 1=Easy copy)")
    score_market: int = Field(description="Potential Revenue (10=Unicorn, 1=Hobby)")
    score_overall: float = Field(description="Weighted Average")
    
    critique: Optional[str] = None
    round_id: int = 0
    iteration_count: int = 0

class BattleConfig(BaseModel):
    """Configuration for the battle session"""
    niche: str
    max_rounds: int = Field(default=1, description="Number of distinct ideas to generate")
    max_iterations: int = Field(default=2, description="Refinements per idea")

class BattleState(BaseModel):
    """The memory of the entire session"""
    config: BattleConfig
    
    # Tracking progress
    current_round: int = 1
    current_iteration: int = 0
    
    # Data storage
    current_idea: Optional[BusinessIdea] = None
    completed_ideas: List[BusinessIdea] = []
    messages: List[str] = []