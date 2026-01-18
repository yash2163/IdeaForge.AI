from langgraph.graph import StateGraph, END
from src.models import BattleState, BusinessIdea
from src.agents import generate_node, roast_node

# --- WRAPPER NODES TO HANDLE HISTORY ---

def roast_node_with_history(state: BattleState):
    # 1. Run the original roast logic
    result = roast_node(state)
    scored_idea = result["current_idea"]
    
    # 2. Append this scored idea to the history list
    # Note: We create a copy so subsequent updates don't mutate this history entry
    current_history = state.all_iterations + [scored_idea.model_copy()]
    
    return {
        "current_idea": scored_idea,
        "all_iterations": current_history
    }

# --- ROUTERS ---

def battle_router(state: BattleState):
    config = state.config
    if state.current_iteration < config.max_iterations:
        return "refine"
    else:
        if state.current_round < config.max_rounds:
            return "new_round"
        else:
            return "end_game"

def save_and_reset(state: BattleState):
    finished_idea = state.current_idea
    return {
        "completed_ideas": state.completed_ideas + [finished_idea],
        "current_round": state.current_round + 1,
        "current_iteration": 0,
        "current_idea": None
    }

def post_save_router(state: BattleState):
    if state.current_round > state.config.max_rounds:
        return END
    return "generate"

# --- GRAPH BUILDER ---

def build_graph():
    workflow = StateGraph(BattleState)
    
    workflow.add_node("generate", generate_node)
    workflow.add_node("roast", roast_node_with_history) # UPDATED NODE
    workflow.add_node("save_idea", save_and_reset)
    
    workflow.set_entry_point("generate")
    workflow.add_edge("generate", "roast")
    
    workflow.add_conditional_edges(
        "roast",
        battle_router,
        {
            "refine": "generate",
            "new_round": "save_idea",
            "end_game": "save_idea"
        }
    )
    
    workflow.add_conditional_edges(
        "save_idea",
        post_save_router,
        {
            "generate": "generate",
            END: END
        }
    )
    
    return workflow.compile()