import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.models import BusinessIdea, BattleState
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

# --- AGENT 1: THE GENERATOR (Visionary) ---
def generate_node(state: BattleState):
    niche = state.niche
    current_idea = state.current_idea
    
    parser = PydanticOutputParser(pydantic_object=BusinessIdea)
    
    if current_idea is None:
        # First creation
        prompt = ChatPromptTemplate.from_template(
            """You are a visionary startup founder. Generate a unique, high-potential business idea for the niche: {niche}.
            Focus on technical innovation.
            
            {format_instructions}
            """
        )
        chain = prompt | llm | parser
        new_idea = chain.invoke({"niche": niche, "format_instructions": parser.get_format_instructions()})
        new_idea.iteration_count = 1
        
    else:
        # Refinement based on critique
        prompt = ChatPromptTemplate.from_template(
            """You are a resilient founder. Your previous idea was roasted.
            Previous Idea: {title} - {description}
            Critique: {critique}
            
            Refine the idea to address the gaps. Do NOT create a totally new business, just pivot or fix the issues.
            Keep the same Title if possible, or slight modification.
            
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
        new_idea.iteration_count = current_idea.iteration_count + 1

    return {"current_idea": new_idea, "messages": [f"Generator: Proposed {new_idea.title}"]}

# --- AGENT 2: THE ROASTER (Cynic) ---
def roast_node(state: BattleState):
    idea = state.current_idea
    
    # We want the Roaster to return a partial update (scores + critique), 
    # but for simplicity in Phase 1, we'll just update the Idea object directly via LLM logic.
    
    parser = PydanticOutputParser(pydantic_object=BusinessIdea)
    
    prompt = ChatPromptTemplate.from_template(
        """You are a ruthless Venture Capitalist. finding gaps is your job.
        Analyze this idea:
        Title: {title}
        Description: {description}
        
        1. Roast it. Find logical gaps, technical risks, and market lies.
        2. Score it strictly (1-10) on Feasibility and Moat.
        3. Calculate overall score.
        
        Output the updated Idea object with your scores and critique added.
        
        {format_instructions}
        """
    )
    
    chain = prompt | llm | parser
    scored_idea = chain.invoke({
        "title": idea.title, 
        "description": idea.description, 
        "format_instructions": parser.get_format_instructions()
    })
    
    # Preserve iteration count and niche from previous state (LLM might hallucinate them)
    scored_idea.iteration_count = idea.iteration_count
    scored_idea.target_niche = idea.target_niche
    
    return {"current_idea": scored_idea, "messages": [f"Roaster: Critiqued {idea.title} (Score: {scored_idea.score_overall})"]}