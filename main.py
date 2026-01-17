from src.graph import build_graph
from src.models import BattleState

def main():
    print("🥊 Starting the Business Battle Arena (Phase 1 Test)...")
    
    # Inputs
    niche_input = "AI Agents for Legal Contracts"
    iterations_input = 2 # Will generate -> roast -> refine -> roast -> end
    
    # Initialize State
    initial_state = BattleState(niche=niche_input, max_iterations=iterations_input)
    
    # Run Graph
    app = build_graph()
    result = app.invoke(initial_state)
    
    # Display Result
    final_idea = result["current_idea"]
    print("\n" + "="*40)
    print(f"🏆 FINAL RESULT for '{niche_input}'")
    print("="*40)
    print(f"Title: {final_idea.title}")
    print(f"Description: {final_idea.description}")
    print(f"Scores -> Feasibility: {final_idea.score_feasibility}/10 | Moat: {final_idea.score_moat}/10")
    print(f"Overall Score: {final_idea.score_overall}")
    print(f"Last Critique: {final_idea.critique}")
    print("="*40)
    
    # Show History
    print("\n📜 Execution Log:")
    for msg in result['messages']:
        print(f"- {msg}")

if __name__ == "__main__":
    main()