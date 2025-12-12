import os
import json
import dataclasses
from datetime import datetime
from typing import List

from core.types import IdeaObject

def generate_markdown_report(ideas: List[IdeaObject], keyword: str, output_dir: str = "results") -> str:
    """
    Generates a markdown report from accepted ideas.
    Includes the full evolution history with Critic and Refiner thoughts.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"research_report_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)
    
    lines = []
    lines.append("# 연구 아이디어 최종 보고서")
    lines.append("")
    lines.append(f"**Keyword:** {keyword}")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Total Accepted Ideas:** {len(ideas)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    for idx, idea in enumerate(ideas, 1):
        lines.append(f"## 아이디어 {idx}: {idea.latest_content.title if idea.latest_content else 'Untitled'}")
        lines.append("")
        lines.append(f"**Status:** `{idea.status}`")
        lines.append(f"**Total Iterations:** {idea.current_iteration + 1}")
        lines.append("")
        
        # Evolution History
        lines.append("### 진화 과정 (Evolution History)")
        lines.append("")
        
        for snap_idx, snapshot in enumerate(idea.evolution_history):
            lines.append(f"#### Iteration {snapshot.iteration} - {snapshot.role.upper()}")
            lines.append("")
            lines.append(f"**Title:** {snapshot.content.title}")
            lines.append("")
            lines.append("**Methodology:**")
            # Handle multi-line methodology with proper markdown
            methodology_text = snapshot.content.methodology or "Not provided"
            lines.append("")
            lines.append(f"{methodology_text}")
            lines.append("")
            
            # Show description if available
            if snapshot.content.description:
                lines.append("**Description:**")
                lines.append("")
                lines.append(f"{snapshot.content.description}")
                lines.append("")
            
            if snapshot.critique:
                crit = snapshot.critique
                lines.append("##### 🧐 Critic Agent의 평가")
                lines.append("")
                lines.append("| 평가 항목 | 점수 |")
                lines.append("|---|---|")
                lines.append(f"| Novelty (독창성) | {crit.novelty_score}/5 |")
                lines.append(f"| Feasibility (실현가능성) | {crit.feasibility_score}/5 |")
                lines.append(f"| Specificity (구체성) | {crit.specificity_score}/5 |")
                lines.append(f"| Impact (파급력) | {crit.impact_score}/5 |")
                lines.append(f"| **Average** | **{crit.average_score:.2f}** |")
                lines.append("")
                lines.append("**Critic의 상세 피드백:**")
                lines.append("")
                # Format feedback text properly (it may contain markdown)
                feedback = crit.feedback_text or "No feedback provided"
                lines.append(feedback)
                lines.append("")
            
            # If this is a refined version, show refiner thoughts in detail
            if snapshot.role == "refined" and snapshot.refinement_details:
                details = snapshot.refinement_details
                lines.append("##### 🔧 Refiner Agent의 개선 내용")
                lines.append("")
                
                lines.append(f"**이전 점수:** {details.critique_score:.2f}/5")
                lines.append("")
                
                lines.append("**Refiner의 사고 과정:**")
                lines.append("")
                lines.append(f"{details.refinement_reasoning}")
                lines.append("")
                
                lines.append("**주요 변경 사항:**")
                lines.append("")
                lines.append(f"{details.changes_made}")
                lines.append("")
            elif snapshot.role == "refined":
                # Fallback if no refinement_details
                lines.append("##### 🔧 Refiner Agent의 개선 내용")
                lines.append("")
                lines.append("> 제목과 방법론이 위와 같이 개선되었습니다.")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        lines.append("")
    
    lines.append("## 결론")
    lines.append("")
    lines.append(f"본 보고서는 **{keyword}** 키워드를 기반으로 생성된 연구 아이디어들을 담고 있습니다.")
    lines.append(f"Generator-Critic-Refiner 멀티 에이전트 시스템을 통해 총 **{len(ideas)}개**의 아이디어가 최종 채택되었습니다.")
    lines.append("")
    
    content = "\n".join(lines)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Report saved to: {filepath}")
    return filepath
