from typing import List, Dict
from agents.base_agent import BaseAgent
from core.types import IdeaObject, CritiqueMetrics
from utils.parser import extract_json
import re

class CriticAgent(BaseAgent):
    def evaluate(self, ideas: List[IdeaObject]) -> List[CritiqueMetrics]:
        if not ideas:
            return []
            
        critiques = []
        
        # Evaluate each idea individually for better quality responses
        for i, idea in enumerate(ideas):
            content = idea.latest_content
            if not content:
                critiques.append(self._create_error_critique("No content found"))
                continue
                
            prompt = f"""You are evaluating a research proposal. Be thorough and critical.

PROPOSAL:
Title: {content.title}
Methodology: {content.methodology}
Description: {content.description or 'Not provided'}

Evaluate this proposal on each criterion (1-5 scale):

1. **Novelty (1-5)**: Is this idea truly novel? Has similar work been published in the last 3 years?
2. **Feasibility (1-5)**: Can this be implemented with current technology, data, and resources?
3. **Specificity (1-5)**: Are the methods, models, and datasets clearly specified?
4. **Impact (1-5)**: What is the potential impact on the field or industry?

Provide your response in this EXACT JSON format:
{{
    "novelty_score": <1-5>,
    "novelty_reasoning": "<why this score>",
    "feasibility_score": <1-5>,
    "feasibility_reasoning": "<why this score>",
    "specificity_score": <1-5>,
    "specificity_reasoning": "<why this score>",
    "impact_score": <1-5>,
    "impact_reasoning": "<why this score>",
    "overall_feedback": "<comprehensive critique with specific suggestions for improvement>",
    "key_weaknesses": ["<weakness 1>", "<weakness 2>", ...],
    "key_strengths": ["<strength 1>", "<strength 2>", ...]
}}

Be harsh but fair. Provide specific, actionable feedback."""
            
            print(f"[{self.role}] Evaluating idea {i+1}/{len(ideas)}: {content.title[:50]}...")
            response = self.generate(prompt)
            
            critique = self._parse_critique_response(response)
            critiques.append(critique)
        
        return critiques
    
    def _parse_critique_response(self, response: str) -> CritiqueMetrics:
        """Parse the LLM response into CritiqueMetrics."""
        data = extract_json(response)
        
        if isinstance(data, dict):
            # Extract scores
            novelty = self._safe_int(data.get("novelty_score", 0))
            feasibility = self._safe_int(data.get("feasibility_score", 0))
            specificity = self._safe_int(data.get("specificity_score", 0))
            impact = self._safe_int(data.get("impact_score", 0))
            
            # Build comprehensive feedback
            feedback_parts = []
            
            # Add overall feedback
            if data.get("overall_feedback"):
                feedback_parts.append(f"**Overall Assessment:** {data['overall_feedback']}")
            
            # Add individual reasoning
            if data.get("novelty_reasoning"):
                feedback_parts.append(f"**Novelty ({novelty}/5):** {data['novelty_reasoning']}")
            if data.get("feasibility_reasoning"):
                feedback_parts.append(f"**Feasibility ({feasibility}/5):** {data['feasibility_reasoning']}")
            if data.get("specificity_reasoning"):
                feedback_parts.append(f"**Specificity ({specificity}/5):** {data['specificity_reasoning']}")
            if data.get("impact_reasoning"):
                feedback_parts.append(f"**Impact ({impact}/5):** {data['impact_reasoning']}")
            
            # Add weaknesses and strengths
            if data.get("key_weaknesses"):
                weaknesses = data["key_weaknesses"]
                if isinstance(weaknesses, list):
                    feedback_parts.append("**Key Weaknesses:**\n" + "\n".join(f"- {w}" for w in weaknesses))
            
            if data.get("key_strengths"):
                strengths = data["key_strengths"]
                if isinstance(strengths, list):
                    feedback_parts.append("**Key Strengths:**\n" + "\n".join(f"- {s}" for s in strengths))
            
            feedback_text = "\n\n".join(feedback_parts) if feedback_parts else data.get("overall_feedback", "No detailed feedback provided.")
            
            # Calculate average
            scores = [novelty, feasibility, specificity, impact]
            valid_scores = [s for s in scores if s > 0]
            average = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
            
            return CritiqueMetrics(
                novelty_score=novelty,
                feasibility_score=feasibility,
                specificity_score=specificity,
                impact_score=impact,
                average_score=round(average, 2),
                feedback_text=feedback_text,
                raw_response=response
            )
        
        # Fallback: try to extract scores from text
        return self._parse_from_text(response)
    
    def _parse_from_text(self, response: str) -> CritiqueMetrics:
        """Fallback parser for non-JSON responses."""
        # Try to find scores in text
        novelty = self._find_score(response, ["novelty", "novel"])
        feasibility = self._find_score(response, ["feasibility", "feasible"])
        specificity = self._find_score(response, ["specificity", "specific"])
        impact = self._find_score(response, ["impact"])
        
        scores = [novelty, feasibility, specificity, impact]
        valid_scores = [s for s in scores if s > 0]
        average = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
        
        return CritiqueMetrics(
            novelty_score=novelty,
            feasibility_score=feasibility,
            specificity_score=specificity,
            impact_score=impact,
            average_score=round(average, 2),
            feedback_text=response[:2000],  # Use raw response as feedback
            raw_response=response
        )
    
    def _find_score(self, text: str, keywords: List[str]) -> int:
        """Find a score near keywords in text."""
        text_lower = text.lower()
        for keyword in keywords:
            # Look for patterns like "novelty: 3" or "novelty score: 3/5"
            patterns = [
                rf'{keyword}[:\s]+(\d)[/\s]?5?',
                rf'{keyword}\s+score[:\s]+(\d)',
            ]
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    score = int(match.group(1))
                    if 1 <= score <= 5:
                        return score
        return 0
    
    def _safe_int(self, value) -> int:
        """Safely convert to int."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
    
    def _create_error_critique(self, error_msg: str) -> CritiqueMetrics:
        """Create an error critique when parsing fails."""
        return CritiqueMetrics(
            novelty_score=0,
            feasibility_score=0,
            specificity_score=0,
            impact_score=0,
            average_score=0.0,
            feedback_text=f"Error: {error_msg}",
            raw_response=None
        )
