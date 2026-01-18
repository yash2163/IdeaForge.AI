import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.models import BusinessIdea, BattleState
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

# --- AGENT 1: THE GENERATOR ---
def generate_node(state: BattleState):
    config = state.config
    current_idea = state.current_idea
    
    parser = PydanticOutputParser(pydantic_object=BusinessIdea)
    
    # LOGIC: If iteration is 0, we need a NEW idea. If > 0, we REFINE.
    if state.current_iteration == 0:
        print(f"--- 💡 Round {state.current_round}: Generating Fresh Idea ---")
        prompt = ChatPromptTemplate.from_template(
            """You are an innovative startup founder in the {niche} space.
            Generate a completely new, unique tech business idea.
            Round: {round}
            
            {format_instructions}
            """
        )
        chain = prompt | llm | parser
        new_idea = chain.invoke({
            "niche": config.niche, 
            "round": state.current_round,
            "format_instructions": parser.get_format_instructions()
        })
        
    else:
        print(f"--- 🔧 Refining Idea (Iter {state.current_iteration}) ---")
        prompt = ChatPromptTemplate.from_template(
            """Your idea was critiqued. Pivot or patch the holes.
            Original: {title}
            Critique: {critique}
            
            Keep the core vision but fix the flaws.
            {format_instructions}
            """
        )
        chain = prompt | llm | parser
        new_idea = chain.invoke({
            "title": current_idea.title,
            "critique": current_idea.critique,
            "format_instructions": parser.get_format_instructions()
        })

    # Update State Metadata
    new_idea.round_id = state.current_round
    new_idea.iteration_count = state.current_iteration + 1
    new_idea.target_niche = config.niche # Persist niche
    
    return {
        "current_idea": new_idea, 
        "current_iteration": state.current_iteration + 1,
        "messages": [f"Generator: Proposed {new_idea.title}"]
    }

# --- AGENT 2: THE ROASTER ---
def roast_node(state: BattleState):
    idea = state.current_idea
    parser = PydanticOutputParser(pydantic_object=BusinessIdea)
    
    print(f"--- 🔥 Roasting '{idea.title}' ---")
    
    prompt = ChatPromptTemplate.from_template(
        """You are a harsh VC. Analyze '{title}'.
        Desc: {description}
        
        1. Critique it ruthlessly.
        2. Score (1-10):
           - Feasibility (Technical ease)
           - Moat (Defensibility)
           - Market (Profit potential)
        3. Calculate Overall = (Feas + Moat + Market) / 3
        
        {format_instructions}
        """
    )
    
    chain = prompt | llm | parser
    scored_idea = chain.invoke({
        "title": idea.title, 
        "description": idea.description,
        "format_instructions": parser.get_format_instructions()
    })
    
    # Metadata preservation
    scored_idea.round_id = idea.round_id
    scored_idea.iteration_count = idea.iteration_count
    scored_idea.target_niche = idea.target_niche
    
    return {"current_idea": scored_idea}