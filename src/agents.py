import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.models import BusinessIdea, BattleState
from src.tools import perform_market_research  # Import the tool
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0.7)

# --- NODE 1: UPDATED GENERATOR NODE ---
# --- UPDATED GENERATOR NODE (FIXED) ---
def generate_node(state: BattleState):
    config = state.config
    current_idea = state.current_idea
    parser = PydanticOutputParser(pydantic_object=BusinessIdea)
    
    # CASE 1: NEW ROUND (Fresh Idea)
    if state.current_iteration == 0:
        print(f"--- 🌎 Scouting Trends for Niche: {config.niche} ---")
        
        # 1. Generator does its own research first
        market_context = perform_market_research(f"trending problems and gaps in {config.niche} market 2025")
        
        print(f"--- 💡 Generating grounded idea... ---")
        prompt = ChatPromptTemplate.from_template(
            """You are a visionary founder.
            
            MARKET INTEL:
            {market_context}
            
            Based on this intel, find a specific unsolved problem or gap. 
            Generate a unique tech business idea to solve it.
            Do NOT propose generic ideas like "AI Chatbot" unless there is a specific twist.
            
            Round: {round}
            
            {format_instructions}
            """
        )
        chain = prompt | llm | parser
        new_idea = chain.invoke({
            "market_context": market_context, 
            "niche": config.niche, 
            "round": state.current_round,
            "format_instructions": parser.get_format_instructions()
        })
        
    # CASE 2: REFINEMENT (Iterating)
    else:
        print(f"--- 🔧 Refining Idea (Iter {state.current_iteration}) ---")
        prompt = ChatPromptTemplate.from_template(
            """Refine this idea based on the critique.
            
            Original: {title}
            Description: {description}
            Critique: {critique}
            
            Pivot or patch the holes. Make it stronger.
            {format_instructions}
            """
        )
        chain = prompt | llm | parser
        new_idea = chain.invoke({
            "title": current_idea.title, 
            "description": current_idea.description,
            "critique": current_idea.critique,
            "format_instructions": parser.get_format_instructions()
        })

    # Metadata updates
    new_iteration_count = state.current_iteration + 1  # Calculate next step
    new_idea.round_id = state.current_round
    new_idea.iteration_count = new_iteration_count
    new_idea.target_niche = config.niche
    
    # --- 🚨 CRITICAL FIX BELOW 🚨 ---
    # We must return BOTH the idea AND the incremented state counter
    return {
        "current_idea": new_idea,
        "current_iteration": new_iteration_count 
    }


# --- NODE 2: RESEARCHER (NEW) ---
def research_node(state: BattleState):
    idea = state.current_idea
    print(f"--- 🕵️ Researching Market for: {idea.title} ---")
    
    # 1. Search the web
    research_data = perform_market_research(idea.target_niche + " " + idea.title)
    
    # 2. Update the idea object with facts
    idea.market_research = research_data
    
    return {"current_idea": idea}

# --- NODE 3: ROASTER (Updated) ---
def roast_node(state: BattleState):
    idea = state.current_idea
    parser = PydanticOutputParser(pydantic_object=BusinessIdea)
    
    print(f"--- 🔥 Roasting with Facts ---")
    
    prompt = ChatPromptTemplate.from_template(
        """You are a generic VC, but you have access to REAL market data.
        
        Idea: {title}
        Description: {description}
        
        REAL WORLD DATA (READ THIS CAREFULLY):
        {market_data}
        
        Task:
        1. Roast the idea. If the data shows strong competitors (like Google/Microsoft), DESTROY the idea for having no moat.
        2. If the market size is small, score 'Market' low.
        3. Be specific. Quote the competitors found in the data.
        
        Score (1-10): Feasibility, Moat, Market.
        
        {format_instructions}
        """
    )
    
    chain = prompt | llm | parser
    scored_idea = chain.invoke({
        "title": idea.title, 
        "description": idea.description,
        "market_data": idea.market_research, # Injecting the research
        "format_instructions": parser.get_format_instructions()
    })
    
    # Preserve Metadata
    scored_idea.round_id = idea.round_id
    scored_idea.iteration_count = idea.iteration_count
    scored_idea.target_niche = idea.target_niche
    scored_idea.market_research = idea.market_research # Keep the data attached
    
    return {"current_idea": scored_idea}