"""
Use Case 03: Developer Code Completion Assistant
Cloud: GCP | Category: Code Completion | Model: Gemini

Core Logic:
  - Context-aware code analysis
  - Multi-language support
  - Prompt chaining for better accuracy
"""

import sys
import os
import json
import ast
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from scripts.config import (
    MODE, GCP_PROJECT_ID, GCP_LOCATION, GEMINI_MODEL,
    OPENAI_API_KEY, is_demo,
)
from scripts.mock_data import CODE_COMPLETIONS, simulate_latency

# ─── Context Extraction ───────────────────────────────────

def extract_code_context(code_snippet, language="python"):
    """Analyze code to extract context for better completions."""
    context = {
        "language": language,
        "imports": [],
        "functions": [],
        "classes": [],
        "variables": [],
    }

    if language == "python":
        try:
            tree = ast.parse(code_snippet)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        context["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    context["imports"].append(f"{node.module}")
                elif isinstance(node, ast.FunctionDef):
                    context["functions"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    context["classes"].append(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            context["variables"].append(target.id)
        except SyntaxError:
            pass  # Incomplete code is expected

    return context


# ─── Prompt Engineering ────────────────────────────────────

def build_completion_prompt(code_snippet, instruction=None, language="python"):
    """Build optimized prompt for code completion."""
    context = extract_code_context(code_snippet, language)

    prompt = f"""You are an expert {language} developer. Complete the following code.

Context:
- Language: {language}
- Existing imports: {', '.join(context['imports']) or 'None'}
- Defined functions: {', '.join(context['functions']) or 'None'}
- Defined classes: {', '.join(context['classes']) or 'None'}

Code to complete:
```{language}
{code_snippet}
```
"""
    if instruction:
        prompt += f"\nSpecific instruction: {instruction}\n"

    prompt += (
        "\nProvide ONLY the completed code, no explanations. "
        "Follow best practices: type hints, docstrings, error handling."
    )
    return prompt


# ─── Core Logic ────────────────────────────────────────────

def complete_code_demo(code_snippet, language="python"):
    """Demo mode code completion using pattern matching."""
    simulate_latency(0.3, 1.0)

    completions = CODE_COMPLETIONS.get(language, {})
    for pattern, completion in completions.items():
        if pattern in code_snippet:
            return {
                "completion": code_snippet + "\n" + completion,
                "pattern_matched": pattern,
                "mode": "demo",
            }

    return {
        "completion": code_snippet + "\n    # TODO: implement\n    pass\n",
        "pattern_matched": "generic",
        "mode": "demo",
    }


def complete_code_gemini(code_snippet, instruction=None, language="python"):
    """Generate code completion using Gemini on Vertex AI."""
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel

        vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)
        model = GenerativeModel(GEMINI_MODEL)

        prompt = build_completion_prompt(code_snippet, instruction, language)
        response = model.generate_content(prompt)

        return {
            "completion": response.text,
            "model": GEMINI_MODEL,
            "mode": "gemini",
        }
    except ImportError:
        print("Error: Install google-cloud-aiplatform → pip install google-cloud-aiplatform")
        return None
    except Exception as e:
        print(f"Vertex AI Error: {e}")
        return None


def complete_code_openai(code_snippet, instruction=None, language="python"):
    """Fallback: Code completion using OpenAI."""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = build_completion_prompt(code_snippet, instruction, language)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are an expert {language} developer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.2,
        )
        return {
            "completion": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
            "model": "gpt-3.5-turbo",
            "mode": "openai_fallback",
        }
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return None


def complete(code_snippet, instruction=None, language="python"):
    """Main entry point."""
    print(f"[Mode: {MODE}] Completing {language} code...")

    if is_demo():
        return complete_code_demo(code_snippet, language)
    elif GCP_PROJECT_ID:
        return complete_code_gemini(code_snippet, instruction, language)
    elif OPENAI_API_KEY:
        return complete_code_openai(code_snippet, instruction, language)
    else:
        print("No API keys configured. Running in demo mode.")
        return complete_code_demo(code_snippet, language)


# ─── CLI ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI Code Completion Assistant")
    parser.add_argument("--code", default="def calculate_fibonacci(n):")
    parser.add_argument("--instruction", default=None)
    parser.add_argument("--language", default="python")
    args = parser.parse_args()

    result = complete(args.code, args.instruction, args.language)
    if result:
        print("\n" + "=" * 60)
        print("  Code Completion Result")
        print("=" * 60)
        print(result["completion"])
        print(f"\n[Mode: {result['mode']}]")


if __name__ == "__main__":
    main()
