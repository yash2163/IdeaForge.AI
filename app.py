import streamlit as st
import pandas as pd
from src.graph import build_graph
from src.models import BattleState, BattleConfig

# Page Config
st.set_page_config(page_title="IdeaForge.AI", page_icon="🥊", layout="wide")

# Title
st.title("🥊 IdeaForge.AI")
st.markdown("### The Autonomous Business Idea Arena")

# --- SIDEBAR: CONTROLS ---
with st.sidebar:
    st.header("⚙️ Battle Config")
    niche_input = st.text_input("Target Niche", "AI Agents for Healthcare")
    rounds_input = st.slider("Number of Rounds (Distinct Ideas)", 1, 5, 2)
    iterations_input = st.slider("Iterations per Idea (Refinements)", 1, 5, 2)
    
    start_btn = st.button("🚀 Start Battle", type="primary")

# --- SESSION STATE ---
if "battle_results" not in st.session_state:
    st.session_state.battle_results = None

# --- BATTLE LOGIC ---
if start_btn:
    with st.spinner("🤖 Agents are fighting... (This may take a moment)"):
        # 1. Init Config
        config = BattleConfig(
            niche=niche_input, 
            max_rounds=rounds_input, 
            max_iterations=iterations_input
        )
        initial_state = BattleState(config=config)
        
        # 2. Run Graph
        app = build_graph()
        result = app.invoke(initial_state)
        
        # 3. Store Results
        st.session_state.battle_results = result
        st.success("Battle Complete!")

# --- RESULTS DISPLAY ---
if st.session_state.battle_results:
    results = st.session_state.battle_results
    
    # 1. LEADERBOARD (Top Section)
    st.divider()
    st.subheader("🏆 Leaderboard")
    
    final_ideas = results['completed_ideas']
    
    # Prepare Dataframe
    data = []
    for idea in final_ideas:
        data.append({
            "Rank": 0, # Placeholder
            "Round": idea.round_id,
            "Title": idea.title,
            "Overall Score": f"{idea.score_overall:.1f}",
            "Feasibility": idea.score_feasibility,
            "Moat": idea.score_moat,
            "Market": idea.score_market,
            "Elevator Pitch": idea.description
        })
    
    df = pd.DataFrame(data)
    if not df.empty:
        df = df.sort_values(by="Overall Score", ascending=False)
        df["Rank"] = range(1, len(df) + 1)
        st.dataframe(
            df, 
            column_config={
                "Overall Score": st.column_config.ProgressColumn(
                    "Overall Score", format="%.1f", min_value=0, max_value=10
                ),
            },
            hide_index=True,
            use_container_width=True
        )

    # 2. DETAILED BATTLE TIMELINE (Bottom Section)
    st.divider()
    st.subheader("📜 Battle Timeline (All Rounds & Iterations)")
    
    all_history = results['all_iterations']
    
    # Group by Round
    round_groups = {}
    for item in all_history:
        r_id = item.round_id
        if r_id not in round_groups:
            round_groups[r_id] = []
        round_groups[r_id].append(item)
    
    # Create Tabs for each Round
    round_tabs = st.tabs([f"Round {r}" for r in sorted(round_groups.keys())])
    
    for i, tab in enumerate(round_tabs):
        round_num = i + 1
        round_data = round_groups.get(round_num, [])
        
        with tab:
            for iteration in round_data:
                # Expander for each iteration
                with st.expander(f"Iter {iteration.iteration_count}: {iteration.title} (Score: {iteration.score_overall:.1f})", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Description:** {iteration.description}")
                        st.markdown(f"**🔥 Roast / Critique:**")
                        st.info(iteration.critique)
                    
                    with col2:
                        st.metric("Feasibility", f"{iteration.score_feasibility}/10")
                        st.metric("Moat", f"{iteration.score_moat}/10")
                        st.metric("Market", f"{iteration.score_market}/10")