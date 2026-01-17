from pydantic import BaseModel, Field
from typing import List, Optional

class BusinessIdea(BaseModel):
    title: str = Field(description="Catchy name of the business/project")
    description: str = Field(description="2-3 sentence elevator pitch")
    target_niche: str = Field(description="The specific niche this serves")
    
    # Metrics (Simple 1-10 for Phase 1)
    score_feasibility: int = Field(description="Technical feasibility (1-10)")
    score_moat: int = Field(description="Competitive advantage (1-10)")
    score_overall: float = Field(description="Average of all scores")
    
    # The critique received
    critique: Optional[str] = Field(description="The roaster's feedback", default=None)
    iteration_count: int = Field(default=0)

class BattleState(BaseModel):
    """The state of the graph passed between agents."""
    niche: str
    max_iterations: int
    current_idea: Optional[BusinessIdea] = None
    messages: List[str] = [] # Log for debugging