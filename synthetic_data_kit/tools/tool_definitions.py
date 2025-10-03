"""Tool definitions for ArXiv and DuckDuckGo"""

ARXIV_TOOL = {
    "name": "arxiv_search",
    "description": "Search for academic papers on ArXiv. Use this when you need to find research papers, scientific articles, or academic publications on a specific topic.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query for finding papers. Be specific about the research topic."
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of papers to return (default: 5, max: 10)",
                "default": 5
            }
        },
        "required": ["query"]
    }
}

DUCKDUCKGO_TOOL = {
    "name": "duckduckgo_search",
    "description": "Search the web using DuckDuckGo. Use this for general information, news, current events, or any topic not requiring academic papers.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query. Be specific about what information you're looking for."
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 5, max: 10)",
                "default": 5
            }
        },
        "required": ["query"]
    }
}

TOOLS = [ARXIV_TOOL, DUCKDUCKGO_TOOL]

def get_tool_definitions():
    """Return all tool definitions"""
    return TOOLS