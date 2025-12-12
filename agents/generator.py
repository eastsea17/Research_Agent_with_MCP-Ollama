from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from core.types import IdeaObject, IdeaSnapshot, IdeaContent
from utils.parser import extract_json
import requests
import re
import uuid

# Concise example JSON structure for one-shot learning
EXAMPLE_JSON_STRUCTURE = """
{
  "topics": [
    {
      "title": "Graph Neural Network for Patent Claim Analysis",
      "background": "Current patent analysis is manual and slow.",
      "necessity": "Existing NLP fails to capture claim hierarchy.",
      "methodology": "Use GNN + RAG: (1) Build claim graph, (2) Embed with PatentBERT, (3) Apply GAT for reasoning.",
      "table_of_contents": ["1. Introduction", "2. Related Work", "3. Method", "4. Experiments", "5. Conclusion"],
      "expected_effects": "60% faster analysis, 85% accuracy on prior art detection.",
      "description": "Novel GNN+RAG approach for patent analysis."
    }
  ]
}
"""

class GeneratorAgent(BaseAgent):
    """
    Generator Agent that fetches papers from OpenAlex API and generates research ideas
    based on the latest, most relevant papers.
    """
    
    def __init__(self, model_manager, role: str):
        super().__init__(model_manager, role)
        self.openalex_url = "https://api.openalex.org/works"
        self.user_agent_email = "research-agent@example.com"
        
        # Read OpenAlex settings from config
        openalex_config = model_manager.config.get("openalex", {})
        
        if "fetch_limit" not in openalex_config or "top_k_papers" not in openalex_config:
            raise ValueError("Missing 'fetch_limit' or 'top_k_papers' in config.yaml under 'openalex' section.")
            
        self.fetch_limit = openalex_config["fetch_limit"]
        self.top_k_papers = openalex_config["top_k_papers"]
    
    def fetch_papers_from_openalex(self, keyword: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch papers from OpenAlex API.
        Returns list of papers with title, abstract, year, authors.
        """
        print(f"[{self.role}] Fetching papers from OpenAlex for: '{keyword}'...")
        
        params = {
            "search": keyword,
            "per-page": min(limit, 200),  # OpenAlex max is 200 per page
            "filter": "has_abstract:true",
            "sort": "publication_year:desc"  # Get newest first
        }
        headers = {
            "User-Agent": f"mailto:{self.user_agent_email}"
        }
        
        try:
            response = requests.get(self.openalex_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            
            papers = []
            for result in results:
                title = result.get("title")
                abstract_inverted = result.get("abstract_inverted_index")
                abstract = self._reconstruct_abstract(abstract_inverted)
                
                # Extract authors
                authorships = result.get("authorships", [])
                authors = []
                for authorship in authorships[:5]:  # Limit to 5 authors
                    author = authorship.get("author", {})
                    author_name = author.get("display_name")
                    if author_name:
                        authors.append(author_name)
                
                if title and abstract:
                    papers.append({
                        "title": title,
                        "abstract": abstract,
                        "year": result.get("publication_year"),
                        "authors": authors,
                        "url": result.get("id"),
                        "cited_by_count": result.get("cited_by_count", 0)
                    })
            
            print(f"[{self.role}] Found {len(papers)} papers from OpenAlex.")
            return papers
            
        except Exception as e:
            print(f"[{self.role}] Error fetching from OpenAlex: {e}")
            return []
    
    def _reconstruct_abstract(self, inverted_index: Dict) -> str:
        """Reconstruct abstract from OpenAlex inverted index format."""
        if not inverted_index:
            return ""
        word_positions = []
        for word, positions in inverted_index.items():
            for pos in positions:
                word_positions.append((pos, word))
        word_positions.sort()
        return " ".join([word for _, word in word_positions])
    
    def _select_top_papers(self, papers: List[Dict], keyword: str, top_k: int = 10) -> List[Dict]:
        """
        Select most relevant recent papers.
        Prioritizes: recency (year) and citation count.
        Reduced to 5 papers to keep prompt size manageable.
        """
        if not papers:
            return []
        
        # Sort by year (desc) then by citations (desc)
        sorted_papers = sorted(
            papers,
            key=lambda x: (x.get('year', 0) or 0, x.get('cited_by_count', 0) or 0),
            reverse=True
        )
        
        return sorted_papers[:top_k]
    
    def _format_papers_for_prompt(self, papers: List[Dict]) -> str:
        """Format papers into a readable context for the LLM."""
        if not papers:
            return "No papers found."
        
        formatted = []
        for i, paper in enumerate(papers, 1):
            year = paper.get('year', 'N/A')
            title = paper.get('title', 'Unknown')
            authors = ', '.join(paper.get('authors', [])[:3])  # First 3 authors
            abstract = paper.get('abstract', '')[:200]  # Truncated to 200 chars
            citations = paper.get('cited_by_count', 0)
            
            formatted.append(f"""
                            **Paper {i}** [{year}] (Cited: {citations})
                            - **Title:** {title}
                            - **Authors:** {authors}
                            - **Abstract:** {abstract}...
                            """)
        
        return "\n".join(formatted)
    
    def create_drafts(self, keyword: str, context: str = "", n: int = 3) -> List[IdeaObject]:
        """
        Generate research topic drafts by:
        1. Fetching papers from OpenAlex API
        2. Selecting most relevant recent papers
        3. Using Chain of Thought reasoning with Critic -> Solution framework
        """
        
        # Step 1: Fetch papers from OpenAlex
        papers = self.fetch_papers_from_openalex(keyword, limit=self.fetch_limit)
        
        # Step 2: Select top relevant papers
        top_papers = self._select_top_papers(papers, keyword, top_k=self.top_k_papers)
        papers_context = self._format_papers_for_prompt(top_papers)
        
        # Build latest papers list for SOTA analysis
        latest_titles = []
        for paper in top_papers:
            year = paper.get('year', 'N/A')
            title = paper.get('title', 'Unknown')
            latest_titles.append(f"- [{year}] {title}")
        latest_papers_str = "\n".join(latest_titles) if latest_titles else "No latest papers found."
        
        # Step 3: Generate ideas with concise prompt
        prompt = f"""You are a research PI proposing {n} novel research topics for "{keyword}".

                    RECENT PAPERS:
                    {latest_papers_str}

                    CONTEXT:
                    {papers_context}

                    TASK:
                    1. First, use <think> to identify limitations in current research and propose solutions.
                    2. Then output JSON with {n} topics.

                    <think>
                    CRITIC: What's missing/flawed in current research?
                    SOLUTION: How to fix it with novel approaches?
                    </think>

                    OUTPUT FORMAT (JSON only, no markdown):
                    {EXAMPLE_JSON_STRUCTURE}

                    Generate {n} topics now:
                    """
        
        print(f"[{self.role}] Generating ideas based on {len(top_papers)} relevant papers...")
        response = self.generate(prompt)
        
        # Post-processing: Remove <think> tags before JSON parsing
        processed_response = response
        if '<think>' in processed_response:
            # Extract thinking content for debugging/logging
            think_match = re.search(r'<think>(.*?)</think>', processed_response, re.DOTALL)
            if think_match:
                thinking_content = think_match.group(1).strip()
                print(f"[{self.role}] Thinking process captured ({len(thinking_content)} chars)")
            
            # Remove <think> block for JSON parsing
            processed_response = re.sub(r'<think>.*?</think>', '', processed_response, flags=re.DOTALL).strip()
        
        # Clean markdown artifacts
        processed_response = processed_response.replace('```json', '').replace('```', '').strip()
        
        data = extract_json(processed_response)
        
        ideas = []
        
        # Handle the nested structure: {"topics": [...]}
        if isinstance(data, dict) and "topics" in data:
            topics_list = data["topics"]
        elif isinstance(data, list):
            topics_list = data
        else:
            print(f"[{self.role}] Warning: Unexpected response format. Attempting recovery...")
            topics_list = []
        
        for item in topics_list:
            if not isinstance(item, dict):
                continue
                
            # Build detailed methodology from available fields
            methodology_parts = []
            
            if item.get("methodology"):
                methodology_parts.append(item["methodology"])
            
            if item.get("table_of_contents"):
                toc = item["table_of_contents"]
                if isinstance(toc, list):
                    methodology_parts.append("\n**Proposed Structure:**\n" + "\n".join(toc))
            
            methodology = "\n\n".join(methodology_parts) if methodology_parts else item.get("methodology", "")
            
            # Build description from background, necessity, expected_effects
            description_parts = []
            if item.get("background"):
                description_parts.append(f"**Background:** {item['background']}")
            if item.get("necessity"):
                description_parts.append(f"**Necessity:** {item['necessity']}")
            if item.get("expected_effects"):
                description_parts.append(f"**Expected Effects:** {item['expected_effects']}")
            
            description = "\n\n".join(description_parts) if description_parts else item.get("description", "")
            
            content = IdeaContent(
                title=item.get("title", "Untitled"),
                methodology=methodology,
                description=description,
                raw_content=str(item)
            )
            
            # Create IdeaObject with initial snapshot
            idea = IdeaObject()
            snapshot = IdeaSnapshot(
                iteration=0,
                role="draft",
                content=content
            )
            idea.evolution_history.append(snapshot)
            ideas.append(idea)
        
        print(f"[{self.role}] Generated {len(ideas)} ideas.")
        return ideas
