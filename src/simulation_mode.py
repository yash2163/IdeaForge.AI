import streamlit as st
import pandas as pd
from src.graph import build_graph
from src.models import BattleState, BattleConfig
import src.database as db
from src.report_generator import generate_csv_report

def run_simulation_mode(niche_input):
    st.header("🤖 Spectator Mode (AI vs AI)")
    st.markdown("_Two autonomous agents generate ideas, research the market, and fight to the death._")
    
    # --- CONTROLS ---
    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            rounds = st.slider("New Ideas (Rounds)", 1, 3, 1)
        with col2:
            iterations = st.slider("Refinements per Idea", 1, 3, 2)
        with col3:
            st.write("") # Spacing
            start_btn = st.button("🚀 Start Simulation", type="primary", use_container_width=True)

    # --- EXECUTION LOGIC ---
    if start_btn:
        with st.status("🏗️ Simulation Running...", expanded=True) as status:
            config = BattleConfig(niche=niche_input, max_rounds=rounds, max_iterations=iterations)
            initial_state = BattleState(config=config)
            
            # Run the LangGraph
            app = build_graph()
            result = app.invoke(initial_state)
            
            status.update(label="✅ Complete!", state="complete", expanded=False)
            
            # Save to DB & Session State
            # db.save_battle(niche_input, result['completed_ideas'])
            db.save_battle(niche_input, result['completed_ideas'], mode="Spectator")
            st.session_state.spectator_results = result['completed_ideas']

    # --- DISPLAY LOGIC ---
    # We check if results exist (either from a fresh run OR loaded history)
    if "spectator_results" in st.session_state:
        final_ideas = st.session_state.spectator_results
        
        st.divider()
        
        # 1. HEADER & DOWNLOAD
        c1, c2 = st.columns([3, 1])
        with c1:
            st.subheader("🏆 Battle Results")
        with c2:
            # Add the CSV Download feature from Phase 6
            csv_data = generate_csv_report(final_ideas)
            st.download_button(
                label="📥 Download Report",
                data=csv_data,
                file_name="ideaforge_report.csv",
                mime="text/csv",
                use_container_width=True
            )

        # 2. LEADERBOARD (DataFrame View)
        data = []
        for idea in final_ideas:
            data.append({
                "Rank": 0, # Placeholder
                "Title": idea.title,
                "Overall": f"{idea.score_overall:.1f}",
                "Feasibility": idea.score_feasibility,
                "Moat": idea.score_moat,
                "Market": idea.score_market,
                "Pitch": idea.description
            })
        
        df = pd.DataFrame(data)
        if not df.empty:
            df = df.sort_values(by="Overall", ascending=False)
            df["Rank"] = range(1, len(df) + 1)
            
            st.dataframe(
                df, 
                column_config={
                    "Overall": st.column_config.ProgressColumn(
                        "Overall Score", format="%s", min_value=0, max_value=10
                    ),
                },
                use_container_width=True,
                hide_index=True
            )
        
        # 3. DETAILED VIEW (Card Style)
        st.markdown("### 📝 Detailed Analysis")
        
        for idea in final_ideas:
            with st.container(border=True):
                # Header Row
                head_c1, head_c2 = st.columns([3, 1])
                with head_c1:
                    st.markdown(f"#### {idea.title}")
                    st.markdown(f"_{idea.description}_")
                with head_c2:
                    st.metric("Overall Score", f"{idea.score_overall:.1f}")

                # Metrics Row (From your reference code)
                m1, m2, m3 = st.columns(3)
                m1.metric("Feasibility", f"{idea.score_feasibility}/10")
                m2.metric("Moat", f"{idea.score_moat}/10")
                m3.metric("Market", f"{idea.score_market}/10")
                
                # Expanders (Research & Critique)
                with st.expander("🕵️ Market Research Data"):
                    if idea.market_research:
                        st.info(idea.market_research)
                    else:
                        st.caption("No research data available.")
                        
                with st.expander("🔥 Final Critique"):
                    st.warning(idea.critique)