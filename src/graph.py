from langgraph.graph import StateGraph, END
from src.models import BattleState, BusinessIdea
from src.agents import generate_node, roast_node, research_node

# --- HELPER NODES & ROUTERS ---

def roast_node_with_history(state: BattleState):
    """Wrapper to run roast_node and then save the snapshot to history"""
    result = roast_node(state)
    scored_idea = result["current_idea"]
    
    # Append to full history
    current_history = state.all_iterations + [scored_idea.model_copy()]
    
    return {
        "current_idea": scored_idea,
        "all_iterations": current_history
    }

def save_and_reset(state: BattleState):
    """Save the finished idea to the leaderboard and prepare for the next round"""
    finished_idea = state.current_idea
    print(f"✅ Idea Finalized: {finished_idea.title} (Score: {finished_idea.score_overall:.1f})")
    
    return {
        "completed_ideas": state.completed_ideas + [finished_idea],
        "current_round": state.current_round + 1,
        "current_iteration": 0, # Reset iteration for the new idea
        "current_idea": None    # Clear current idea for the new round
    }

def battle_router(state: BattleState):
    """Decides if we refine the current idea, start a new round, or end"""
    config = state.config
    
    # 1. Check Iterations (Refinement Loop)
    if state.current_iteration < config.max_iterations:
        return "refine"
    
    # 2. Check Rounds (New Idea Loop)
    else:
        if state.current_round < config.max_rounds:
            return "new_round"
        else:
            return "end_game"

def post_save_router(state: BattleState):
    """After saving, do we really end or go back to generate?"""
    if state.current_round > state.config.max_rounds:
        return END
    return "generate"

# --- MAIN GRAPH BUILDER ---

def build_graph():
    workflow = StateGraph(BattleState)
    
    # 1. Add Nodes
    workflow.add_node("generate", generate_node)
    workflow.add_node("research", research_node)
    workflow.add_node("roast", roast_node_with_history) # Uses the wrapper
    workflow.add_node("save_idea", save_and_reset)
    
    # 2. Set Entry Point
    workflow.set_entry_point("generate")
    
    # 3. Add Edges (The Flow)
    # Generate -> Research -> Roast
    workflow.add_edge("generate", "research")
    workflow.add_edge("research", "roast")
    
    # 4. Conditional Logic (After Roast)
    workflow.add_conditional_edges(
        "roast",
        battle_router,
        {
            "refine": "generate",      # Go back to fix current idea
            "new_round": "save_idea",  # Save and start fresh
            "end_game": "save_idea"    # Save and finish
        }
    )
    
    # 5. Conditional Logic (After Save)
    workflow.add_conditional_edges(
        "save_idea",
        post_save_router,
        {
            "generate": "generate",
            END: END
        }
    )
    
    return workflow.compile()