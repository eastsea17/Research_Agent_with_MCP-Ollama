import sys
import os
import argparse
import json
import dataclasses
from typing import List

from core.model_manager import ModelManager
from core.mcp_client import MCPClient
from agents.generator import GeneratorAgent
from agents.critic import CriticAgent
from agents.refiner import RefinerAgent
from core.types import IdeaObject, IdeaSnapshot, CritiqueMetrics
from utils.report_generator import generate_markdown_report
from utils.html_generator import convert_md_to_html

# Helper to serialize dataclasses
class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

def research_loop(keyword: str, max_loops: int = 3, output_file: str = "ideas.json"):
    print(f"=== Starting Research Loop for Keyword: {keyword} ===")
    
    # 1. Initialize
    model_mgr = ModelManager()
    mcp_client = MCPClient()
    
    # Read thresholds from config
    loop_settings = model_mgr.config.get("loop_settings", {})
    score_threshold = loop_settings.get("score_threshold", 3.0)
    drop_threshold = loop_settings.get("drop_threshold", 2.0)
    print(f"Thresholds: Accept >= {score_threshold}, Drop < {drop_threshold}")
    
    # 2. Context
    print("Fetching Context...")
    context = mcp_client.get_context(keyword)
    
    # 3. Generator
    print("Initialization Generator...")
    model_mgr.load_model("generator")
    generator = GeneratorAgent(model_mgr, "generator")
    ideas = generator.create_drafts(keyword, context, n=3)
    model_mgr.unload_model("generator")
    
    # Loop
    accepted_ideas = []
    
    critic = CriticAgent(model_mgr, "critic")
    refiner = RefinerAgent(model_mgr, "refiner")

    for loop in range(max_loops):
        print(f"\n--- Iteration {loop + 1}/{max_loops} ---")
        
        if not ideas:
            print("No ideas left to process.")
            break
            
        # 3. Critic
        model_mgr.load_model("critic")
        critiques = critic.evaluate(ideas)
        model_mgr.unload_model("critic")
        
        needs_refinement = []
        
        # 4. Filter
        for idea, review in zip(ideas, critiques):
            # Update history
            if idea.evolution_history:
                idea.evolution_history[-1].critique = review
            
            print(f"Idea: {idea.latest_content.title[:30]}... | Score: {review.average_score}")
            
            if review.average_score >= score_threshold:
                print(" -> Accepted!")
                idea.status = "accepted"
                accepted_ideas.append(idea)
            elif review.average_score < drop_threshold:
                print(" -> Rejected (Score too low).")
                idea.status = "rejected"
            else:
                print(" -> Needs Refinement.")
                needs_refinement.append(idea)
        
        if not needs_refinement:
            print("No ideas need refinement. Loop finished.")
            break
            
        # 5. Refiner
        model_mgr.load_model("refiner")
        refined_ideas = []
        for idea in needs_refinement:
            new_content, refinement_details = refiner.improve(idea)
            
            # Create new snapshot with refinement details
            new_snapshot = IdeaSnapshot(
                 iteration=loop + 1,
                 role="refined",
                 content=new_content,
                 refinement_details=refinement_details
            )
            idea.evolution_history.append(new_snapshot)
            idea.current_iteration += 1
            refined_ideas.append(idea)
            
        model_mgr.unload_model("refiner")
        
        # Prepare for next loop
        ideas = refined_ideas

    # After all iterations: include remaining refined ideas even if they didn't meet threshold
    # These represent the best effort of the refiner
    if ideas:  # Remaining ideas after last iteration
        print(f"\n--- Including {len(ideas)} refined ideas (best effort) ---")
        for idea in ideas:
            if idea.status == "active":  # Not yet accepted or rejected
                idea.status = "refined_best_effort"
                accepted_ideas.append(idea)

    # Save Results
    print(f"\n=== Final Results: {len(accepted_ideas)} Ideas ===")
    with open(output_file, 'w') as f:
        json.dump(accepted_ideas, f, cls=EnhancedJSONEncoder, indent=2)
    print(f"Saved to {output_file}")
    
    # Generate Markdown Report
    if accepted_ideas:
        report_path = generate_markdown_report(accepted_ideas, keyword, output_dir="results")
        print(f"Markdown report generated: {report_path}")
        
        # Convert to HTML
        html_path = convert_md_to_html(report_path)
    
    return accepted_ideas

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deep Research Agent")
    parser.add_argument("--keyword", type=str, required=True, help="Research keyword")
    parser.add_argument("--loops", type=int, default=3, help="Max iterations")
    parser.add_argument("--output", type=str, default="results/research_results.json", help="Output file")
    
    args = parser.parse_args()
    
    research_loop(args.keyword, args.loops, args.output)

