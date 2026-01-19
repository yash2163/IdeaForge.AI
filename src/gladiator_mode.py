import streamlit as st
from src.models import BusinessIdea
from src.agents import generate_ai_idea_logic, refine_idea_logic, roast_idea_logic
from src.tools import perform_market_research
import src.database as db  # <--- NEW IMPORT

def run_gladiator_mode(niche_input):
    st.header(f"🥊 Gladiator Mode: You vs AI ({niche_input})")
    
    # Initialize State
    if "game_step" not in st.session_state:
        st.session_state.game_step = "IDEATION"
        st.session_state.user_idea = None
        st.session_state.ai_idea = None
        st.session_state.gladiator_saved = False # <--- NEW FLAG to prevent duplicate saves
    
    # RESET BUTTON
    if st.button("🔄 Reset Game"):
        st.session_state.game_step = "IDEATION"
        st.session_state.user_idea = None
        st.session_state.ai_idea = None
        st.session_state.gladiator_saved = False
        st.rerun()

    # --- STEP 1: IDEATION ---
    if st.session_state.game_step == "IDEATION":
        col1, col2 = st.columns(2)
        with col1:
            st.info("👤 **Your Turn**")
            user_title = st.text_input("Your Idea Title")
            user_desc = st.text_area("Your Elevator Pitch")
            
            if st.button("Submit & Fight"):
                if user_title and user_desc:
                    with st.spinner("🤖 AI is generating a counter-idea & researching..."):
                        # 1. Setup User Idea
                        st.session_state.user_idea = BusinessIdea(
                            title=user_title, description=user_desc, target_niche=niche_input
                        )
                        # 2. Setup AI Idea
                        st.session_state.ai_idea = generate_ai_idea_logic(niche_input, 1, "")
                        st.session_state.ai_idea.target_niche = niche_input
                        
                        # 3. Research & Roast (Round 1)
                        st.session_state.user_idea.market_research = perform_market_research(f"{niche_input} {user_title}")
                        st.session_state.user_idea = roast_idea_logic(st.session_state.user_idea)
                        
                        st.session_state.ai_idea.market_research = perform_market_research(f"{niche_input} {st.session_state.ai_idea.title}")
                        st.session_state.ai_idea = roast_idea_logic(st.session_state.ai_idea)
                        
                        st.session_state.game_step = "REFINEMENT"
                        st.rerun()

    # --- STEP 2: REFINEMENT ---
    elif st.session_state.game_step == "REFINEMENT":
        u_idea = st.session_state.user_idea
        a_idea = st.session_state.ai_idea
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### 👤 You: {u_idea.title}")
            st.write(u_idea.description)
            st.warning(f"**🔥 Roast:** {u_idea.critique}")
            st.metric("Round 1 Score", f"{u_idea.score_overall:.1f}")
        with col2:
            st.markdown(f"### 🤖 AI: {a_idea.title}")
            st.write(a_idea.description)
            st.warning(f"**🔥 Roast:** {a_idea.critique}")
            st.metric("Round 1 Score", f"{a_idea.score_overall:.1f}")

        st.divider()
        st.subheader("🔧 Phase 2: Fix your flaws")
        
        with st.form("refine_form"):
            new_user_desc = st.text_area("Refine your pitch based on the roast:", value=u_idea.description)
            
            if st.form_submit_button("Submit Refinement"):
                with st.spinner("🔄 Both sides are refining..."):
                    # 1. Update User
                    st.session_state.user_idea.description = new_user_desc
                    st.session_state.user_idea = roast_idea_logic(st.session_state.user_idea) 
                    
                    # 2. Update AI
                    st.session_state.ai_idea = refine_idea_logic(st.session_state.ai_idea)
                    st.session_state.ai_idea = roast_idea_logic(st.session_state.ai_idea)
                    
                    st.session_state.game_step = "FINAL"
                    st.rerun()

    # --- STEP 3: FINAL RESULTS ---
    elif st.session_state.game_step == "FINAL":
        u_idea = st.session_state.user_idea
        a_idea = st.session_state.ai_idea
        
        # Winner Logic
        if u_idea.score_overall >= a_idea.score_overall:
            st.balloons()
            winner_txt = "🎉 YOU WIN!"
            color = "green"
        else:
            winner_txt = "🤖 AI WINS!"
            color = "red"
            
        st.markdown(f"<h1 style='text-align: center; color: {color};'>{winner_txt}</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### 👤 Final Pitch: {u_idea.title}")
            st.info(u_idea.description)
            st.markdown("**Final Critique:**")
            st.error(u_idea.critique) 
            st.metric("Final Score", f"{u_idea.score_overall:.1f}")
            
        with col2:
            st.markdown(f"### 🤖 Final Pitch: {a_idea.title}")
            st.info(a_idea.description)
            st.markdown("**Final Critique:**")
            st.error(a_idea.critique)
            st.metric("Final Score", f"{a_idea.score_overall:.1f}")
        
        # --- NEW: SAVE TO DATABASE ---
        if not st.session_state.gladiator_saved:
            # We save the session with a special tag so we know it was Human vs AI
            session_name = f"{niche_input}"
            
            # Tag the ideas so we know who made what in the history
            u_idea.title = f"[USER] {u_idea.title}"
            a_idea.title = f"[AI] {a_idea.title}"

            db.save_battle(session_name, [u_idea, a_idea], mode="Gladiator")

            st.session_state.gladiator_saved = True
            st.success("✅ Match Results Saved to History!")