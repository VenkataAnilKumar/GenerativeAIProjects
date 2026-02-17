"""
Use Case 06: Personalized Learning Content Generator
Cloud: GCP | Category: Text Generation | Model: PaLM 2 / Gemini

Core Logic:
  - Student level assessment
  - Adaptive content generation
  - Multi-format output (lessons, exercises, quizzes)
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
from scripts.mock_data import LEARNING_CONTENT, simulate_latency

# ─── Content Profiles ─────────────────────────────────────

DIFFICULTY_LEVELS = ["beginner", "intermediate", "advanced"]

CONTENT_FORMATS = {
    "lesson": "Generate a detailed lesson plan with explanations and examples.",
    "exercise": "Create practice exercises with increasing difficulty.",
    "quiz": "Generate a quiz with multiple choice and short answer questions.",
    "summary": "Provide a concise topic summary for review.",
}


def build_learning_prompt(topic, level, content_format, student_context=None):
    """Build an adaptive learning prompt."""
    format_instruction = CONTENT_FORMATS.get(content_format, CONTENT_FORMATS["lesson"])

    prompt = f"""You are an expert educational content creator.

Topic: {topic}
Student Level: {level}
Content Format: {content_format}

{format_instruction}

Requirements:
- Adapt language complexity for {level} students.
- Include 2-3 real-world examples.
- Add "Check Your Understanding" questions at the end.
- Use clear headings and bullet points.
"""
    if student_context:
        prompt += f"\nStudent Background: {student_context}\n"
    return prompt


# ─── Core Logic ────────────────────────────────────────────

def generate_content_demo(topic, level, content_format):
    """Demo content generation from mock data."""
    simulate_latency(0.5, 1.5)

    topic_key = topic.lower().replace(" ", "_")
    if topic_key in LEARNING_CONTENT and level in LEARNING_CONTENT[topic_key]:
        data = LEARNING_CONTENT[topic_key][level]
        return {
            "title": data["title"],
            "content": data["content"],
            "objectives": data.get("objectives", []),
            "exercises": data.get("exercises", []),
            "level": level,
            "format": content_format,
            "mode": "demo",
        }

    return {
        "title": f"{topic} — {level.capitalize()} Level",
        "content": (
            f"Lesson on {topic} for {level} students.\n\n"
            f"1. Introduction to {topic}\n"
            f"2. Key concepts and definitions\n"
            f"3. Examples and applications\n"
            f"4. Practice problems\n"
        ),
        "objectives": [
            f"Understand fundamentals of {topic}",
            f"Apply {topic} concepts to problems",
        ],
        "exercises": [
            {"question": f"Define {topic} in your own words.", "answer": "Open-ended"},
        ],
        "level": level,
        "format": content_format,
        "mode": "demo",
    }


def generate_content_llm(topic, level, content_format, student_context=None):
    """Generate learning content using LLM."""
    prompt = build_learning_prompt(topic, level, content_format, student_context)

    try:
        if GCP_PROJECT_ID:
            import vertexai
            from vertexai.generative_models import GenerativeModel

            vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)
            model = GenerativeModel(GEMINI_MODEL)
            response = model.generate_content(prompt)
            content = response.text
            mode = "gemini"
        else:
            from openai import OpenAI

            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=800,
                temperature=0.7,
            )
            content = response.choices[0].message.content
            mode = "openai_fallback"

        return {
            "title": f"{topic} — {level.capitalize()} Level",
            "content": content,
            "level": level,
            "format": content_format,
            "mode": mode,
        }
    except Exception as e:
        print(f"LLM Error: {e}")
        return None


def generate(topic, level="beginner", content_format="lesson", student_context=None):
    """Main entry point."""
    print(f"[Mode: {MODE}] Generating {content_format} on '{topic}' for {level} students...")

    if is_demo():
        return generate_content_demo(topic, level, content_format)
    elif GCP_PROJECT_ID or OPENAI_API_KEY:
        return generate_content_llm(topic, level, content_format, student_context)
    else:
        return generate_content_demo(topic, level, content_format)


# ─── CLI ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Personalized Learning Content Generator")
    parser.add_argument("--topic", default="algebra")
    parser.add_argument("--level", choices=DIFFICULTY_LEVELS, default="beginner")
    parser.add_argument("--format", choices=list(CONTENT_FORMATS.keys()), default="lesson")
    args = parser.parse_args()

    result = generate(args.topic, args.level, args.format)
    if result:
        print("\n" + "=" * 60)
        print(f"  📚 {result['title']}")
        print("=" * 60)
        print(f"\n{result['content']}")
        if result.get("objectives"):
            print("\nLearning Objectives:")
            for obj in result["objectives"]:
                print(f"  ✅ {obj}")
        if result.get("exercises"):
            print("\nExercises:")
            for ex in result["exercises"]:
                print(f"  ❓ {ex['question']}")
        print(f"\n[Mode: {result['mode']}]")


if __name__ == "__main__":
    main()
