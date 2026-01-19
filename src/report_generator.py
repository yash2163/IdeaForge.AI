import pandas as pd
import io

def generate_csv_report(ideas):
    """
    Converts a list of BusinessIdea objects into a CSV string 
    compatible with Streamlit's download button.
    """
    data = []
    for idea in ideas:
        data.append({
            "Round": idea.round_id,
            "Iteration": idea.iteration_count,
            "Title": idea.title,
            "One-Liner": idea.description,
            "Overall Score": idea.score_overall,
            "Feasibility": idea.score_feasibility,
            "Moat": idea.score_moat,
            "Market Potential": idea.score_market,
            "Market Research Used": idea.market_research,
            "Last Critique": idea.critique
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Convert to CSV string
    # index=False ensures we don't save the pandas row numbers
    return df.to_csv(index=False).encode('utf-8')