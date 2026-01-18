from src.graph import build_graph
from src.models import BattleState, BattleConfig
import pandas as pd

def main():
    print("🥊 IdeaForge.AI: Phase 2 Test")
    print("=============================")
    
    # Configuration
    niche = "AI Tools for Construction Industry"
    rounds = 2        # We want 2 distinct ideas
    iterations = 2    # Each idea gets 1 refine loop (Gen -> Roast -> Refine -> Roast)
    
    config = BattleConfig(niche=niche, max_rounds=rounds, max_iterations=iterations)
    initial_state = BattleState(config=config)
    
    # Execution
    app = build_graph()
    result = app.invoke(initial_state)
    
    # ---------------- LEADERBOARD DISPLAY ----------------
    print("\n🏆 FINAL LEADERBOARD")
    print("====================")
    
    ideas = result['completed_ideas']
    
    # Sort by Overall Score (Descending)
    ideas.sort(key=lambda x: x.score_overall, reverse=True)
    
    # Create simple dataframe for view
    data = []
    for i, idea in enumerate(ideas):
        data.append([
            i+1, 
            idea.title, 
            f"{idea.score_overall:.1f}", 
            idea.score_feasibility, 
            idea.score_moat, 
            idea.score_market
        ])
        
    df = pd.DataFrame(data, columns=["Rank", "Title", "Overall", "Feas.", "Moat", "Mkt"])
    print(df.to_string(index=False))
    
    print("\n📝 Top Idea Details:")
    top_idea = ideas[0]
    print(f"Title: {top_idea.title}")
    print(f"Pitch: {top_idea.description}")
    print(f"Killer Constraint (Moat): {top_idea.score_moat}/10")

if __name__ == "__main__":
    main()