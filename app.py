import streamlit as st
import pandas as pd
import src.database as db
from src.simulation_mode import run_simulation_mode
from src.gladiator_mode import run_gladiator_mode
from src.report_generator import generate_csv_report

# --- SETUP ---
st.set_page_config(page_title="IdeaForge.AI", page_icon="⚔️", layout="wide")
db.init_db()

# Custom CSS
st.markdown("""<style>.main-header { font-size: 2.5rem; color: #FF4B4B; font-weight: 800; }</style>""", unsafe_allow_html=True)
st.markdown('<div class="main-header">⚔️ IdeaForge.AI</div>', unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎮 Game Mode")
    # We use a Session State variable to track the active mode so it persists
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "Spectator (AI vs AI)"
    
    # Mode Selector
    selected_mode = st.radio(
        "Select Mode", 
        ["Spectator (AI vs AI)", "Gladiator (You vs AI)"],
        index=0 if st.session_state.app_mode == "Spectator (AI vs AI)" else 1
    )
    
    # If mode changes, reset view to "Live"
    if selected_mode != st.session_state.app_mode:
        st.session_state.app_mode = selected_mode
        st.session_state.view_mode = "live"
        st.rerun()

    st.divider()
    
    # --- GLOBAL SETTINGS ---
    if st.session_state.app_mode == "Spectator (AI vs AI)":
        st.header("⚙️ Simulation Config")
    else:
        st.header("⚙️ Gladiator Config")
        
    niche_input = st.text_input("Target Niche", "AI for Education")

    st.divider()

    # --- HISTORY SECTION (FILTERED) ---
    st.header("📜 Battle History")
    
    # Determine the tag based on current mode so we show relevant history only
    current_mode_tag = "Spectator" if st.session_state.app_mode == "Spectator (AI vs AI)" else "Gladiator"
    
    # Fetch filtered sessions using the new DB function
    past_sessions = db.get_sessions_by_mode(current_mode_tag)
    
    if not past_sessions:
        st.caption(f"No {current_mode_tag} battles recorded yet.")
    else:
        for s_id, s_niche, s_time in past_sessions:
            # Clean up timestamp for display
            short_time = s_time.split(" ")[0] 
            label = f"#{s_id} {s_niche}"
            
            if st.button(label, key=f"hist_{s_id}", use_container_width=True):
                st.session_state.view_mode = "history"
                st.session_state.selected_session_id = s_id
                st.session_state.selected_session_name = s_niche
                st.rerun()
                
    if st.button("⬅️ Back to Live Game", use_container_width=True):
        st.session_state.view_mode = "live"
        st.rerun()

# ==========================================
# MAIN ROUTER LOGIC
# ==========================================

# CASE 1: HISTORY VIEW
if st.session_state.get("view_mode") == "history":
    s_id = st.session_state.get("selected_session_id")
    s_name = st.session_state.get("selected_session_name")
    
    st.info(f"📂 Viewing Archived Session #{s_id}: {s_name}")
    
    # Load Data
    history_ideas = db.get_session_ideas(s_id)
    
    if history_ideas:
        # 1. Download Button
        csv_data = generate_csv_report(history_ideas)
        st.download_button("📥 Download This Report", csv_data, "history_report.csv", "text/csv")
        
        # 2. Leaderboard
        st.subheader("🏆 Final Standings")
        data = []
        for idea in history_ideas:
            data.append({
                "Title": idea.title,
                "Score": f"{idea.score_overall:.1f}",
                "Feasibility": idea.score_feasibility,
                "Moat": idea.score_moat,
                "Market": idea.score_market,
                "Pitch": idea.description
            })
        st.dataframe(pd.DataFrame(data), use_container_width=True)
        
        # 3. Details
        st.markdown("### 📝 Detailed Records")
        for idea in history_ideas:
            with st.expander(f"{idea.title} (Score: {idea.score_overall:.1f})"):
                st.write(f"**Pitch:** {idea.description}")
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Research:**\n{idea.market_research}")
                with col2:
                    st.warning(f"**Critique:**\n{idea.critique}")

# CASE 2: LIVE GAME MODES
else:
    # Only run the game logic if we are NOT in history mode
    if st.session_state.app_mode == "Spectator (AI vs AI)":
        run_simulation_mode(niche_input)
        
    elif st.session_state.app_mode == "Gladiator (You vs AI)":
        run_gladiator_mode(niche_input)