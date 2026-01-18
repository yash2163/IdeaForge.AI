from pydantic import BaseModel, Field
from typing import List, Optional

class BusinessIdea(BaseModel):
    title: str
    description: str
    target_niche: str
    
    # NEW: Stores the raw search data found by the Researcher
    market_research: Optional[str] = Field(description="Facts about competitors and market size", default="")
    
    score_feasibility: int = 0
    score_moat: int = 0
    score_market: int = 0
    score_overall: float = 0.0
    
    critique: Optional[str] = None
    round_id: int = 0
    iteration_count: int = 0

# ... (BattleConfig and BattleState remain the same) ...
class BattleConfig(BaseModel):
    niche: str
    max_rounds: int = 2
    max_iterations: int = 2

class BattleState(BaseModel):
    config: BattleConfig
    current_round: int = 1
    current_iteration: int = 0
    current_idea: Optional[BusinessIdea] = None
    completed_ideas: List[BusinessIdea] = [] 
    all_iterations: List[BusinessIdea] = [] 
    messages: List[str] = []