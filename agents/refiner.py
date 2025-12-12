from agents.base_agent import BaseAgent
from core.types import IdeaObject, IdeaContent, IdeaSnapshot, RefinementDetails
from utils.parser import extract_json

class RefinerAgent(BaseAgent):
    def improve(self, idea: IdeaObject) -> tuple[IdeaContent, RefinementDetails]:
        """
        Improve an idea based on critic feedback.
        Returns both the new content and details about the refinement process.
        """
        content = idea.latest_content
        critique = idea.latest_critique
        
        if not content or not critique:
            return content, None
        
        prompt = f"""You are a Lead Research Architect. Your task is to substantially improve a research proposal based on critic feedback.

## ORIGINAL PROPOSAL
**Title:** {content.title}
**Methodology:** {content.methodology}
**Description:** {content.description or 'Not provided'}

## CRITIC'S FEEDBACK (Score: {critique.average_score}/5)
{critique.feedback_text}

## YOUR TASK
1. Carefully analyze each criticism
2. Address each weakness specifically
3. Substantially improve the proposal

Provide your response in this EXACT JSON format:
{{
    "thinking_process": "<your step-by-step reasoning about how to address each criticism>",
    "changes_summary": "<brief summary of the key changes you're making>",
    "refined_title": "<improved title that addresses novelty concerns>",
    "refined_methodology": "<detailed, specific methodology that addresses feasibility and specificity concerns>",
    "refined_description": "<comprehensive description with concrete details>",
    "addressed_weaknesses": [
        {{"weakness": "<original weakness>", "solution": "<how you addressed it>"}}
    ],
    "expected_score_improvement": "<why you expect the score to improve>"
}}

Be specific. Replace vague terms with concrete methods, models, and datasets."""
        
        print(f"[{self.role}] Refining idea: {content.title[:50]}...")
        response = self.generate(prompt)
        data = extract_json(response)
        
        if isinstance(data, dict):
            # Extract refined content
            new_content = IdeaContent(
                title=data.get("refined_title", content.title),
                methodology=data.get("refined_methodology", content.methodology),
                description=data.get("refined_description", content.description),
                raw_content=response  # Store full response
            )
            
            # Build changes summary
            changes_made = data.get("changes_summary", "")
            if data.get("addressed_weaknesses"):
                weaknesses = data["addressed_weaknesses"]
                if isinstance(weaknesses, list):
                    changes_list = []
                    for w in weaknesses:
                        if isinstance(w, dict):
                            changes_list.append(f"• {w.get('weakness', 'N/A')} → {w.get('solution', 'N/A')}")
                    if changes_list:
                        changes_made += "\n\n**Addressed Weaknesses:**\n" + "\n".join(changes_list)
            
            # Create refinement details
            refinement_details = RefinementDetails(
                original_title=content.title,
                original_methodology=content.methodology,
                critique_feedback=critique.feedback_text[:500],  # Truncate if too long
                critique_score=critique.average_score,
                refinement_reasoning=data.get("thinking_process", "No reasoning provided"),
                changes_made=changes_made or "No specific changes documented"
            )
            
            return new_content, refinement_details
        
        # Fallback: return original with error note
        print(f"[{self.role}] Failed to parse refinement, returning original.")
        refinement_details = RefinementDetails(
            original_title=content.title,
            original_methodology=content.methodology,
            critique_feedback=critique.feedback_text[:500],
            critique_score=critique.average_score,
            refinement_reasoning="Parsing failed - using original content",
            changes_made="No changes (parsing error)"
        )
        return content, refinement_details
