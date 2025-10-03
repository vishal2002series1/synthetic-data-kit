# synthetic_data_kit/create/tool_use_generator.py
import json
import logging
import hashlib
from typing import List, Dict, Any
from synthetic_data_kit.providers.bedrock_provider import BedrockProvider

logger = logging.getLogger(__name__)


class ToolUseGenerator:
    def __init__(self, provider: BedrockProvider):
        self.provider = provider
        
        # Define available tools
        self.tools = {
            "arxiv_search": {
                "type": "function",
                "function": {
                    "name": "arxiv_search",
                    "description": "Search for academic papers on arXiv repository",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string", 
                                "description": "Search query for academic papers"
                            },
                            "max_results": {
                                "type": "integer", 
                                "description": "Maximum number of results to return",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            "duckduckgo_search": {
                "type": "function", 
                "function": {
                    "name": "duckduckgo_search",
                    "description": "Search the web using DuckDuckGo for current information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for web search"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        }

    def generate_tool_requiring_queries(self, context: str, num_queries: int = 3) -> List[str]:
        """Generate queries that would require tool usage based on context"""
        
        prompt = f"""Based on the following document context, generate {num_queries} questions that would require external tools to answer completely.

Context:
{context}

Generate questions that MUST use external tools because they ask for:
1. Recent research papers or academic studies (needs arxiv_search)
2. Current market data, news, or real-time information (needs duckduckgo_search)
3. Comparative analysis with external sources
4. Latest developments or trends not in the document

Examples:
- "What recent academic papers discuss [topic from context]?"
- "What is the current market cap of [company mentioned]?"
- "How do recent studies compare to the findings in this document?"
- "What are the latest industry trends for [sector mentioned]?"

Return ONLY a JSON array of {num_queries} questions:
["question 1", "question 2", "question 3"]"""

        response = self.provider.generate(
            prompt=prompt,
            max_tokens=800,
            temperature=0.8
        )
        
        # Extract text from response
        if isinstance(response, dict) and "content" in response:
            text_output = ""
            for content_block in response["content"]:
                if content_block.get("type") == "text":
                    text_output += content_block.get("text", "")
        else:
            text_output = str(response)
        
        # Clean and parse JSON
        text_output = text_output.strip()
        if text_output.startswith("```json"):
            text_output = text_output[7:]
        if text_output.startswith("```"):
            text_output = text_output[3:]
        if text_output.endswith("```"):
            text_output = text_output[:-3]
        text_output = text_output.strip()
        
        try:
            queries = json.loads(text_output)
            return queries[:num_queries] if isinstance(queries, list) else [text_output]
        except json.JSONDecodeError:
            logger.warning("Failed to parse queries JSON, extracting manually")
            # Fallback: extract questions from text
            lines = [l.strip(' "[],-') for l in text_output.split('\n') if l.strip() and '?' in l]
            return lines[:num_queries]

    def determine_appropriate_tool(self, query: str) -> str:
        """Determine which tool should be used for a given query"""
        academic_keywords = ["research", "papers", "academic", "study", "studies", "journal", "publication", "scholar"]
        
        if any(keyword in query.lower() for keyword in academic_keywords):
            return "arxiv_search"
        else:
            return "duckduckgo_search"

    def extract_search_terms(self, query: str, tool_name: str) -> str:
        """Extract appropriate search terms from query"""
        
        prompt = f"""Extract the most relevant search terms from this question for {tool_name}:

Question: {query}

Return only the search terms that would be most effective for {'academic paper search' if tool_name == 'arxiv_search' else 'web search'}. 
Keep it concise (2-5 key terms)."""

        response = self.provider.generate(
            prompt=prompt,
            max_tokens=100,
            temperature=0.3
        )
        
        # Extract text from response
        if isinstance(response, dict) and "content" in response:
            text_output = ""
            for content_block in response["content"]:
                if content_block.get("type") == "text":
                    text_output += content_block.get("text", "")
        else:
            text_output = str(response)
        
        return text_output.strip().strip('"')

    def generate_synthetic_tool_result(self, tool_name: str, search_query: str, context: str) -> str:
        """Generate realistic tool results"""
        
        if tool_name == "arxiv_search":
            prompt = f"""Generate realistic arXiv search results for query: "{search_query}"

Context: {context[:500]}...

Generate 2-3 realistic academic paper results with:
- Paper titles
- Authors  
- Brief abstracts (1-2 sentences each)
- arXiv IDs (format: 2024.XXXX)

Make them relevant to the context and search query. Format as a realistic search result."""

        else:  # duckduckgo_search
            prompt = f"""Generate realistic web search results for query: "{search_query}"

Context: {context[:500]}...

Generate 2-3 realistic web search results with:
- Page titles
- Brief descriptions/snippets
- Make them relevant to current market/industry information

Format as realistic search results."""

        response = self.provider.generate(
            prompt=prompt,
            max_tokens=600,
            temperature=0.7
        )
        
        # Extract text from response
        if isinstance(response, dict) and "content" in response:
            text_output = ""
            for content_block in response["content"]:
                if content_block.get("type") == "text":
                    text_output += content_block.get("text", "")
        else:
            text_output = str(response)
        
        return text_output.strip()

    def generate_final_response(self, query: str, tool_result: str, context: str) -> str:
        """Generate final assistant response using tool results and context"""
        
        prompt = f"""You are an AI assistant that just received search results. Generate a comprehensive answer using both the search results and document context.

User Question: {query}

Search Results: {tool_result}

Document Context: {context[:800]}...

Generate a helpful response that:
1. References the search results naturally
2. Connects findings to the document context
3. Provides a complete answer
4. Is conversational and informative

Keep response focused and under 200 words."""

        response = self.provider.generate(
            prompt=prompt,
            max_tokens=400,
            temperature=0.7
        )
        
        # Extract text from response
        if isinstance(response, dict) and "content" in response:
            text_output = ""
            for content_block in response["content"]:
                if content_block.get("type") == "text":
                    text_output += content_block.get("text", "")
        else:
            text_output = str(response)
        
        return text_output.strip()

    def create_tool_calling_conversation(self, query: str, context: str) -> Dict[str, Any]:
        """Create a complete tool-calling conversation example for training"""
        
        # Determine appropriate tool
        tool_name = self.determine_appropriate_tool(query)
        
        # Extract search terms
        search_terms = self.extract_search_terms(query, tool_name)
        
        # Create tool arguments
        if tool_name == "arxiv_search":
            tool_args = {"query": search_terms, "max_results": 5}
        else:
            tool_args = {"query": search_terms}
        
        # Generate synthetic tool results
        tool_result = self.generate_synthetic_tool_result(tool_name, search_terms, context)
        
        # Generate final response
        final_response = self.generate_final_response(query, tool_result, context)
        
        # Create unique call ID
        call_id = f"call_{abs(hash(query + tool_name)) % 10000:04d}"
        
        # Build the conversation
        conversation = {
            "messages": [
                {
                    "role": "user",
                    "content": query
                },
                {
                    "role": "assistant",
                    "content": f"I'll help you find information about that. Let me search for {'recent academic papers' if tool_name == 'arxiv_search' else 'current information'} on this topic.",
                    "tool_calls": [
                        {
                            "id": call_id,
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": json.dumps(tool_args)
                            }
                        }
                    ]
                },
                {
                    "role": "tool",
                    "tool_call_id": call_id,
                    "name": tool_name,
                    "content": tool_result
                },
                {
                    "role": "assistant",
                    "content": final_response
                }
            ],
            "tools": [self.tools[tool_name]],
            "metadata": {
                "source_context": context[:200] + "...",
                "tool_used": tool_name,
                "search_query": search_terms
            }
        }
        
        return conversation

    def generate_from_chunks(self, chunks: List[str], queries_per_chunk: int = 3) -> List[Dict[str, Any]]:
        """Generate tool-calling examples from document chunks"""
        
        tool_examples = []
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Generating tool-use examples from chunk {i+1}/{len(chunks)}")
            
            try:
                # Generate queries that require tools
                queries = self.generate_tool_requiring_queries(chunk, queries_per_chunk)
                
                # Create tool-calling conversations for each query
                for query in queries:
                    if len(query.strip()) > 10:  # Skip very short queries
                        conversation = self.create_tool_calling_conversation(query, chunk)
                        tool_examples.append(conversation)
                        logger.info(f"✓ Created tool-calling example: {query[:60]}...")
                
            except Exception as e:
                logger.error(f"Error processing chunk {i+1}: {e}")
                continue
        
        logger.info(f"Generated {len(tool_examples)} total tool-calling examples")
        return tool_examples