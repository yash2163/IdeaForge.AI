from langgraph.graph import StateGraph, END
from src.models import BattleState
from src.agents import generate_node, roast_node

def should_continue(state: BattleState):
    idea = state.current_idea
    if idea.iteration_count >= state.max_iterations:
        return END
    return "roast"

def build_graph():
    workflow = StateGraph(BattleState)
    
    # Add Nodes
    workflow.add_node("generate", generate_node)
    workflow.add_node("roast", roast_node)
    
    # Set Entry Point
    workflow.set_entry_point("generate")
    
    # Add Edges
    # After generating, go to roast
    workflow.add_edge("generate", "roast")
    
    # After roasting, check if we need to refine (loop back) or end
    workflow.add_conditional_edges(
        "roast",
        should_continue,
        {
            "roast": "generate", # Actually, if we continue, we go back to generate to fix it
            END: END
        }
    )
    
    # Correction on logic above: 
    # If should_continue returns "roast" (meaning continue), we actually want to point to "generate".
    # Let's fix the Conditional Logic mapping:
    
    def router(state: BattleState):
        if state.current_idea.iteration_count >= state.max_iterations:
            return "end"
        return "refine"

    workflow.add_conditional_edges(
        "roast",
        router,
        {
            "refine": "generate",
            "end": END
        }
    )
    
    return workflow.compile()