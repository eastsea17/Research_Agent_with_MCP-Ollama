from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import uuid

@dataclass
class CritiqueMetrics:
    novelty_score: int
    feasibility_score: int
    specificity_score: int
    impact_score: int
    average_score: float
    feedback_text: str
    raw_response: Optional[str] = None  # Store full LLM response for debugging

    def compute_average(self) -> float:
        """Compute average from individual scores."""
        scores = [self.novelty_score, self.feasibility_score, 
                  self.specificity_score, self.impact_score]
        valid_scores = [s for s in scores if s > 0]
        if not valid_scores:
            return 0.0
        return sum(valid_scores) / len(valid_scores)

@dataclass
class IdeaContent:
    title: str
    methodology: str
    description: Optional[str] = None
    raw_content: Optional[str] = None  # To store full LLM output if needed

@dataclass
class RefinementDetails:
    """Details about why and how an idea was refined."""
    original_title: str
    original_methodology: str
    critique_feedback: str
    critique_score: float
    refinement_reasoning: str  # Why the refiner made these changes
    changes_made: str  # Summary of changes

@dataclass
class IdeaSnapshot:
    iteration: int
    role: str  # "draft", "refined"
    content: IdeaContent
    critique: Optional[CritiqueMetrics] = None
    refinement_details: Optional[RefinementDetails] = None  # Added for refinement tracking

@dataclass
class IdeaObject:
    idea_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    current_iteration: int = 0
    status: str = "active"  # active, accepted, rejected
    evolution_history: List[IdeaSnapshot] = field(default_factory=list)

    @property
    def latest_content(self) -> Optional[IdeaContent]:
        if not self.evolution_history:
            return None
        return self.evolution_history[-1].content

    @property
    def latest_critique(self) -> Optional[CritiqueMetrics]:
        if not self.evolution_history:
            return None
        return self.evolution_history[-1].critique
