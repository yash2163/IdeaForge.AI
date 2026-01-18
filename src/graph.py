from langgraph.graph import StateGraph, END
from src.models import BattleState, BusinessIdea
from src.agents import generate_node, roast_node

def battle_router(state: BattleState):
    config = state.config
    
    # Check if current idea needs more refinement
    if state.current_iteration < config.max_iterations:
        return "refine"
    
    # If Idea is done (max iterations reached)
    else:
        # Check if we have more Rounds (new ideas) to play
        if state.current_round < config.max_rounds:
            return "new_round"
        else:
            return "end_game"

def save_and_reset(state: BattleState):
    """Node that saves the finished idea and resets counters for next round"""
    finished_idea = state.current_idea
    print(f"✅ Idea Finalized: {finished_idea.title} (Score: {finished_idea.score_overall:.1f})")
    
    return {
        "completed_ideas": [finished_idea], # Appends to list
        "current_round": state.current_round + 1,
        "current_iteration": 0, # Reset for next idea
        "current_idea": None
    }

def build_graph():
    workflow = StateGraph(BattleState)
    
    workflow.add_node("generate", generate_node)
    workflow.add_node("roast", roast_node)
    workflow.add_node("save_idea", save_and_reset)
    
    workflow.set_entry_point("generate")
    
    workflow.add_edge("generate", "roast")
    
    workflow.add_conditional_edges(
        "roast",
        battle_router,
        {
            "refine": "generate",      # Go back to fix current idea
            "new_round": "save_idea",  # Save and start fresh
            "end_game": "save_idea"    # Save and finish
        }
    )
    
    # After saving, check if we really ended or just started a new round
    def post_save_router(state: BattleState):
        if state.current_round > state.config.max_rounds:
            return END
        return "generate"

    workflow.add_conditional_edges(
        "save_idea",
        post_save_router,
        {
            "generate": "generate",
            END: END
        }
    )
    
    return workflow.compile()