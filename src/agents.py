import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.models import BusinessIdea, BattleState
from src.tools import perform_market_research
from dotenv import load_dotenv

load_dotenv()

# Using the model you specified. If this fails, revert to "gemini-1.5-flash"
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

# ==========================================
# 1. CORE LOGIC FUNCTIONS (Reusable for Gladiator Mode)
# ==========================================

def generate_ai_idea_logic(niche, round_id, market_context=""):
    """Pure logic to generate a fresh AI idea (used by both Graph and Gladiator mode)"""
    parser = PydanticOutputParser(pydantic_object=BusinessIdea)
    
    # If no context provided, do a quick search (Self-Correction)
    if not market_context:
        print(f"--- 🌎 Scouting Trends for {niche} ---")
        market_context = perform_market_research(f"trending problems in {niche} market 2025")

    prompt = ChatPromptTemplate.from_template(
        """You are a visionary founder in {niche}.
        
        MARKET INTEL:
        {market_context}
        
        Based on this intel, find a specific unsolved problem or gap. 
        Generate a unique tech business idea to solve it.
        Do NOT propose generic ideas like "AI Chatbot" unless there is a specific twist.
        
        Round: {round}
        
        {format_instructions}"""
    )
    chain = prompt | llm | parser
    return chain.invoke({
        "niche": niche, 
        "round": round_id, 
        "market_context": market_context,
        "format_instructions": parser.get_format_instructions()
    })

def refine_idea_logic(idea):
    """Pure logic to refine an idea based on critique"""
    parser = PydanticOutputParser(pydantic_object=BusinessIdea)
    prompt = ChatPromptTemplate.from_template(
        """Refine this idea based on the critique.
        
        Original: {title}
        Description: {description}
        Critique: {critique}
        
        Pivot or patch the holes. Make it stronger. Keep the Title similar if possible.
        {format_instructions}"""
    )
    chain = prompt | llm | parser
    refined_idea = chain.invoke({
        "title": idea.title, 
        "description": idea.description, 
        "critique": idea.critique,
        "format_instructions": parser.get_format_instructions()
    })
    
    # Restore metadata that LLM might drop
    refined_idea.round_id = idea.round_id
    refined_idea.iteration_count = idea.iteration_count + 1
    refined_idea.target_niche = idea.target_niche
    return refined_idea

def roast_idea_logic(idea):
    """Pure logic to score and critique an idea"""
    parser = PydanticOutputParser(pydantic_object=BusinessIdea)
    
    # Ensure we have market data (if missing, fetch it)
    if not idea.market_research:
        idea.market_research = perform_market_research(f"{idea.target_niche} {idea.title} competitors")

    prompt = ChatPromptTemplate.from_template(
        """You are a generic VC, but you have access to REAL market data.
        
        Idea: {title}
        Description: {description}
        
        REAL WORLD DATA (READ THIS CAREFULLY):
        {market_data}
        
        Task:
        1. Roast the idea. If data shows strong competitors, be harsh.
        2. Score 'Market' low if the niche is tiny.
        3. Be specific. Quote competitors found in data.
        
        Score (1-10): Feasibility, Moat, Market.
        
        {format_instructions}"""
    )
    chain = prompt | llm | parser
    scored = chain.invoke({
        "title": idea.title, 
        "description": idea.description, 
        "market_data": idea.market_research,
        "format_instructions": parser.get_format_instructions()
    })
    
    # Restore metadata
    scored.market_research = idea.market_research
    scored.target_niche = idea.target_niche
    scored.round_id = idea.round_id
    scored.iteration_count = idea.iteration_count
    
    return scored

# ==========================================
# 2. GRAPH NODES (Used in Simulation Mode)
# ==========================================

def generate_node(state: BattleState):
    config = state.config
    current_idea = state.current_idea
    
    # CASE 1: NEW ROUND (Fresh Idea)
    if state.current_iteration == 0:
        print(f"--- 💡 Generating grounded idea (Round {state.current_round})... ---")
        # We call the shared logic function to avoid duplicate code
        # Note: We pass empty market_context so the logic function does the scouting itself
        new_idea = generate_ai_idea_logic(config.niche, state.current_round)
        
    # CASE 2: REFINEMENT (Iterating)
    else:
        print(f"--- 🔧 Refining Idea (Iter {state.current_iteration}) ---")
        new_idea = refine_idea_logic(current_idea)

    # Metadata updates
    new_iteration_count = state.current_iteration + 1  # FIX: Increment counter
    new_idea.round_id = state.current_round
    new_idea.iteration_count = new_iteration_count
    new_idea.target_niche = config.niche
    
    # --- CRITICAL FIX: Return updated iteration count to State ---
    return {
        "current_idea": new_idea,
        "current_iteration": new_iteration_count 
    }

def research_node(state: BattleState):
    idea = state.current_idea
    print(f"--- 🕵️ Researching Market for: {idea.title} ---")
    
    # 1. Search the web
    research_data = perform_market_research(idea.target_niche + " " + idea.title)
    
    # 2. Update the idea object with facts
    idea.market_research = research_data
    
    return {"current_idea": idea}

def roast_node(state: BattleState):
    print(f"--- 🔥 Roasting with Facts ---")
    # Call shared logic
    scored_idea = roast_idea_logic(state.current_idea)
    
    return {"current_idea": scored_idea}