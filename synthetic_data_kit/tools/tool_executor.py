"""Tool execution implementations"""
import arxiv
from ddgs import DDGS
from typing import Dict, Any, List

class ToolExecutor:
    """Executes tool calls and returns results"""
    
    def __init__(self):
        self.ddgs = DDGS()
    
    def execute_arxiv_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Execute ArXiv search"""
        try:
            search = arxiv.Search(
                query=query,
                max_results=min(max_results, 10),
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            results = []
            for paper in search.results():
                results.append({
                    "title": paper.title,
                    "authors": [author.name for author in paper.authors],
                    "summary": paper.summary[:500],  # Truncate for brevity
                    "published": paper.published.strftime("%Y-%m-%d"),
                    "pdf_url": paper.pdf_url,
                    "entry_id": paper.entry_id
                })
            
            return results
        except Exception as e:
            return [{"error": f"ArXiv search failed: {str(e)}"}]
    
    def execute_duckduckgo_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Execute DuckDuckGo search"""
        try:
            results = list(self.ddgs.text(query, max_results=min(max_results, 10)))
            return [
                {
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "url": r.get("href", "")
                }
                for r in results
            ]
        except Exception as e:
            return [{"error": f"DuckDuckGo search failed: {str(e)}"}]
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a tool by name"""
        if tool_name == "arxiv_search":
            return self.execute_arxiv_search(**tool_input)
        elif tool_name == "duckduckgo_search":
            return self.execute_duckduckgo_search(**tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}