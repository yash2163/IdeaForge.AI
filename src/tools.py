from langchain_community.tools import DuckDuckGoSearchRun

search_tool = DuckDuckGoSearchRun()

def perform_market_research(topic: str) -> str:
    """Searches for market size and competitors"""
    try:
        # We run 2 searches to get better coverage
        query_market = f"market size and growth trends for {topic} 2025"
        query_competitors = f"top competitors and startups in {topic}"
        
        res_market = search_tool.invoke(query_market)
        res_competitors = search_tool.invoke(query_competitors)
        
        return f"**Market Data:** {res_market}\n\n**Competitors:** {res_competitors}"
    except Exception as e:
        return f"Research failed: {str(e)}"