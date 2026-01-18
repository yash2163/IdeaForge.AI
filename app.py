import streamlit as st
import pandas as pd
from src.graph import build_graph
from src.models import BattleState, BattleConfig
import src.database as db  # Import the new DB module

# --- SETUP ---
st.set_page_config(page_title="IdeaForge.AI", page_icon="🥊", layout="wide")
db.init_db()  # Initialize DB on app start

st.title("💡 IdeaForge.AI")
st.markdown("### The Autonomous Business Idea Arena")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ New Battle")
    niche_input = st.text_input("Target Niche", "AI Agents for Healthcare")
    rounds_input = st.slider("Number of Rounds", 1, 5, 2)
    iterations_input = st.slider("Iterations per Idea", 1, 5, 2)
    
    if st.button("🚀 Start Battle", type="primary"):
        st.session_state.run_battle = True
        st.session_state.view_mode = "live"

    st.divider()
    
    # --- HISTORY SECTION ---
    st.header("📜 Past Battles")
    past_sessions = db.get_all_sessions()
    
    if not past_sessions:
        st.info("No battles yet.")
    else:
        for s_id, s_niche, s_time in past_sessions:
            # Create a button for each past session
            label = f"{s_niche} ({s_time})"
            if st.button(label, key=f"hist_{s_id}"):
                st.session_state.view_mode = "history"
                st.session_state.selected_session_id = s_id
                st.rerun() # Refresh to show history

# --- MAIN LOGIC ---

# 1. RUN NEW BATTLE
if st.session_state.get("run_battle"):
    st.session_state.run_battle = False # Reset trigger
    
    with st.spinner("🤖 Agents are fighting..."):
        config = BattleConfig(niche=niche_input, max_rounds=rounds_input, max_iterations=iterations_input)
        initial_state = BattleState(config=config)
        
        app = build_graph()
        result = app.invoke(initial_state)
        
        # SAVE TO DB
        db.save_battle(niche_input, result['completed_ideas'])
        
        # Update Session State for Display
        st.session_state.display_ideas = result['completed_ideas']
        st.success("Battle Complete & Saved!")

# 2. LOAD HISTORY
if st.session_state.get("view_mode") == "history":
    s_id = st.session_state.get("selected_session_id")
    st.session_state.display_ideas = db.get_session_ideas(s_id)
    st.info(f"Viewing Historical Data: Session #{s_id}")

# --- DISPLAY LOGIC (Common for both Live and History) ---
if "display_ideas" in st.session_state:
    final_ideas = st.session_state.display_ideas
    
    # A. Leaderboard
    st.divider()
    st.subheader("🏆 Leaderboard")
    
    data = []
    for idea in final_ideas:
        data.append({
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
        st.dataframe(df, use_container_width=True)

    # B. Details (Simple view for now, as history usually just stores the final state)
    st.divider()
    st.subheader("📝 Idea Details")
    
    for idea in final_ideas:
        with st.expander(f"{idea.title} (Score: {idea.score_overall:.1f})"):
            st.write(f"**Pitch:** {idea.description}")
            st.write(f"**Latest Critique:** {idea.critique}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Feasibility", idea.score_feasibility)
            col2.metric("Moat", idea.score_moat)
            col3.metric("Market", idea.score_market)