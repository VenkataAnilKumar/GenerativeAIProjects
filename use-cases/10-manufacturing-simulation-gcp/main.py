"""
Use Case 10: Operational Simulation for Manufacturing
Cloud: GCP | Category: RAG Pipeline | Model: Gemini Pro

Core Logic:
  - Manufacturing data analysis
  - Scenario simulation with LLM
  - Impact prediction across metrics
  - Recommendation generation
"""

import sys
import os
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from scripts.config import (
    MODE, GCP_PROJECT_ID, GCP_LOCATION, GEMINI_MODEL,
    OPENAI_API_KEY, is_demo,
)
from scripts.mock_data import MANUFACTURING_DATA, simulate_latency

# ─── Data Analysis Engine ──────────────────────────────────

def analyze_production_data(data):
    """Analyze current production metrics."""
    lines = data["production_lines"]
    total_capacity = sum(l["capacity"] for l in lines)
    avg_utilization = sum(l["utilization"] for l in lines) / len(lines)
    avg_defect = sum(l["defect_rate"] for l in lines) / len(lines)
    daily_output = data["daily_output"]
    cost_per_unit = data["cost_per_unit"]

    return {
        "total_capacity": total_capacity,
        "current_output": daily_output,
        "utilization_pct": f"{avg_utilization:.1%}",
        "avg_defect_rate": f"{avg_defect:.2%}",
        "daily_cost": f"${daily_output * cost_per_unit:,.2f}",
        "production_lines": len(lines),
        "suppliers": len(data["suppliers"]),
    }


def simulate_impact(scenario, data):
    """Simulate the impact of a scenario on production metrics."""
    metrics = analyze_production_data(data)
    scenario_lower = scenario.lower()
    impacts = {}

    # Supply delay simulation
    if "delay" in scenario_lower or "supplier" in scenario_lower:
        delay_pct = 0.2
        impacts = {
            "production_impact": f"-{delay_pct:.0%} daily output",
            "new_daily_output": int(data["daily_output"] * (1 - delay_pct)),
            "revenue_loss_daily": f"${data['daily_output'] * delay_pct * data['cost_per_unit']:,.2f}",
            "recommended_actions": [
                "Activate secondary supplier (Supplier Y)",
                "Increase safety stock by 15%",
                "Reschedule non-critical production runs",
            ],
        }

    # Capacity change simulation
    elif "capacity" in scenario_lower or "expand" in scenario_lower:
        expand_pct = 0.2
        new_capacity = int(sum(l["capacity"] for l in data["production_lines"]) * (1 + expand_pct))
        impacts = {
            "production_impact": f"+{expand_pct:.0%} capacity",
            "new_total_capacity": new_capacity,
            "investment_needed": f"${new_capacity * data['cost_per_unit'] * 30:,.2f} (est.)",
            "recommended_actions": [
                "Phase expansion over 3 months",
                "Hire 10-15 additional operators",
                "Update maintenance schedule",
            ],
        }

    # Defect rate simulation
    elif "defect" in scenario_lower or "quality" in scenario_lower:
        new_defect = 0.05
        waste_cost = data["daily_output"] * new_defect * data["cost_per_unit"]
        impacts = {
            "production_impact": f"Defect rate increase to {new_defect:.0%}",
            "daily_waste_cost": f"${waste_cost:,.2f}",
            "monthly_impact": f"${waste_cost * 30:,.2f}",
            "recommended_actions": [
                "Implement additional QC checkpoints",
                "Root cause analysis on Line B (highest defect rate)",
                "Operator retraining on critical processes",
            ],
        }

    # Generic scenario
    else:
        impacts = {
            "production_impact": "Analysis required",
            "recommended_actions": [
                "Gather more specific scenario parameters",
                "Run detailed simulation with historical data",
                "Consult domain experts for edge cases",
            ],
        }

    return impacts


# ─── Core Logic ────────────────────────────────────────────

def simulate_demo(scenario):
    """Demo simulation using rule-based analysis."""
    simulate_latency(1.0, 3.0)

    current_metrics = analyze_production_data(MANUFACTURING_DATA)
    impacts = simulate_impact(scenario, MANUFACTURING_DATA)

    return {
        "scenario": scenario,
        "current_state": current_metrics,
        "predicted_impact": impacts,
        "confidence": "Medium (rule-based analysis)",
        "mode": "demo",
    }


def simulate_llm(scenario):
    """AI-powered simulation using LLM."""
    current_metrics = analyze_production_data(MANUFACTURING_DATA)
    rule_impacts = simulate_impact(scenario, MANUFACTURING_DATA)

    context = (
        f"Manufacturing Data:\n"
        f"- Production Lines: {json.dumps(MANUFACTURING_DATA['production_lines'], indent=2)}\n"
        f"- Suppliers: {json.dumps(MANUFACTURING_DATA['suppliers'], indent=2)}\n"
        f"- Cost per unit: ${MANUFACTURING_DATA['cost_per_unit']}\n"
        f"- Daily output: {MANUFACTURING_DATA['daily_output']}\n\n"
        f"Current Metrics: {json.dumps(current_metrics, indent=2)}\n\n"
        f"Rule-based impact estimate: {json.dumps(rule_impacts, indent=2)}"
    )

    prompt = (
        f"You are a manufacturing operations analyst.\n\n"
        f"{context}\n\n"
        f"Scenario: {scenario}\n\n"
        f"Provide a detailed simulation analysis including:\n"
        f"1. Impact on production volume, quality, and costs\n"
        f"2. Timeline for effects (immediate, short-term, long-term)\n"
        f"3. Risks and mitigation strategies\n"
        f"4. Specific recommendations with priorities\n"
        f"5. Estimated recovery timeline"
    )

    try:
        if GCP_PROJECT_ID:
            import vertexai
            from vertexai.generative_models import GenerativeModel

            vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)
            model = GenerativeModel(GEMINI_MODEL)
            response = model.generate_content(prompt)
            ai_analysis = response.text
            mode = "gemini"
        else:
            from openai import OpenAI

            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a manufacturing operations analyst."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=600,
                temperature=0.3,
            )
            ai_analysis = response.choices[0].message.content
            mode = "openai_fallback"

        return {
            "scenario": scenario,
            "current_state": current_metrics,
            "rule_based_impact": rule_impacts,
            "ai_analysis": ai_analysis,
            "confidence": "High (AI + rule-based)",
            "mode": mode,
        }
    except Exception as e:
        print(f"LLM Error: {e}")
        return None


def simulate(scenario):
    """Main entry point."""
    print(f"[Mode: {MODE}] Simulating: '{scenario}'...")

    if is_demo():
        return simulate_demo(scenario)
    elif GCP_PROJECT_ID or OPENAI_API_KEY:
        return simulate_llm(scenario)
    else:
        return simulate_demo(scenario)


# ─── CLI ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Manufacturing Operational Simulator")
    parser.add_argument("--scenario", default="20% delay in raw material delivery from Supplier X")
    args = parser.parse_args()

    result = simulate(args.scenario)
    if result:
        print("\n" + "=" * 60)
        print("  🏭 Manufacturing Simulation Results")
        print("=" * 60)
        print(f"\nScenario: {result['scenario']}")
        print(f"\nCurrent State:")
        for k, v in result["current_state"].items():
            print(f"  • {k}: {v}")
        print(f"\nPredicted Impact:")
        impacts = result.get("predicted_impact") or result.get("rule_based_impact", {})
        for k, v in impacts.items():
            if k == "recommended_actions":
                print(f"  📋 Recommendations:")
                for action in v:
                    print(f"     → {action}")
            else:
                print(f"  • {k}: {v}")
        if result.get("ai_analysis"):
            print(f"\nAI Analysis:\n{result['ai_analysis']}")
        print(f"\nConfidence: {result['confidence']}")
        print(f"[Mode: {result['mode']}]")


if __name__ == "__main__":
    main()
