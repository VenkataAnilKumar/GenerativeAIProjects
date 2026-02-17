"""
Use Case 08: Automated Code Review System
Cloud: AWS | Category: Code Completion | Model: Amazon Q / GPT-4

Core Logic:
  - Static analysis (AST-based)
  - AI-powered review with LLM
  - Rule-based checks (style, security, performance)
  - Structured feedback generation
"""

import sys
import os
import json
import ast
import re
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from scripts.config import MODE, OPENAI_API_KEY, is_demo
from scripts.mock_data import CODE_REVIEW_RULES, simulate_latency

# ─── Static Analysis Rules ─────────────────────────────────

def check_syntax(code):
    """Check for syntax errors."""
    try:
        ast.parse(code)
        return {"status": "pass", "message": "No syntax errors"}
    except SyntaxError as e:
        return {"status": "fail", "message": f"Syntax error at line {e.lineno}: {e.msg}"}


def check_docstrings(code):
    """Check if functions and classes have docstrings."""
    issues = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not (node.body and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, (ast.Str, ast.Constant))):
                    issues.append({
                        "line": node.lineno,
                        "severity": "warning",
                        "rule": "missing_docstring",
                        "message": f"'{node.name}' is missing a docstring.",
                    })
    except SyntaxError:
        pass
    return issues


def check_error_handling(code):
    """Check for functions without error handling."""
    issues = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_try = any(isinstance(child, ast.Try) for child in ast.walk(node))
                calls_external = any(isinstance(child, ast.Call) for child in ast.walk(node))
                if calls_external and not has_try:
                    issues.append({
                        "line": node.lineno,
                        "severity": "info",
                        "rule": "no_try_except",
                        "message": f"'{node.name}' has external calls but no try/except.",
                    })
    except SyntaxError:
        pass
    return issues


def check_security(code):
    """Basic security checks."""
    issues = []
    patterns = [
        (r"eval\s*\(", "Use of eval() — potential code injection risk"),
        (r"exec\s*\(", "Use of exec() — potential code injection risk"),
        (r"os\.system\s*\(", "Use of os.system() — prefer subprocess.run()"),
        (r"pickle\.loads?\s*\(", "Unpickling untrusted data — security risk"),
        (r"password\s*=\s*['\"]", "Hardcoded password detected"),
        (r"api_key\s*=\s*['\"]", "Hardcoded API key detected"),
    ]
    for pattern, msg in patterns:
        matches = list(re.finditer(pattern, code))
        for match in matches:
            line_num = code[:match.start()].count("\n") + 1
            issues.append({
                "line": line_num,
                "severity": "error",
                "rule": "security",
                "message": msg,
            })
    return issues


def check_complexity(code):
    """Check function length and nesting depth."""
    issues = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno + 1 if hasattr(node, "end_lineno") else 0
                if func_lines > 50:
                    issues.append({
                        "line": node.lineno,
                        "severity": "warning",
                        "rule": "long_function",
                        "message": f"'{node.name}' is {func_lines} lines. Consider breaking it up.",
                    })
    except SyntaxError:
        pass
    return issues


def run_static_analysis(code):
    """Run all static analysis checks."""
    results = {
        "syntax": check_syntax(code),
        "issues": [],
    }
    results["issues"].extend(check_docstrings(code))
    results["issues"].extend(check_error_handling(code))
    results["issues"].extend(check_security(code))
    results["issues"].extend(check_complexity(code))

    # Sort by severity
    severity_order = {"error": 0, "warning": 1, "info": 2}
    results["issues"].sort(key=lambda x: severity_order.get(x["severity"], 3))
    return results


# ─── Core Logic ────────────────────────────────────────────

def review_demo(code):
    """Demo code review with static analysis only."""
    simulate_latency(0.5, 2.0)
    analysis = run_static_analysis(code)

    summary = (
        f"Found {len(analysis['issues'])} issue(s): "
        f"{sum(1 for i in analysis['issues'] if i['severity'] == 'error')} errors, "
        f"{sum(1 for i in analysis['issues'] if i['severity'] == 'warning')} warnings, "
        f"{sum(1 for i in analysis['issues'] if i['severity'] == 'info')} info."
    )

    return {
        "syntax": analysis["syntax"],
        "issues": analysis["issues"],
        "summary": summary,
        "ai_suggestions": "Run with API keys for AI-powered suggestions.",
        "mode": "demo",
    }


def review_llm(code):
    """AI-powered code review using LLM."""
    # Step 1: Static analysis
    analysis = run_static_analysis(code)

    # Step 2: LLM review
    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = (
            f"Review this code. Provide specific, actionable feedback on:\n"
            f"1. Bugs and logic errors\n"
            f"2. Performance improvements\n"
            f"3. Code style and readability\n"
            f"4. Security concerns\n"
            f"5. Best practices\n\n"
            f"Format each item as: [SEVERITY] Line X: Description\n\n"
            f"```python\n{code}\n```"
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a senior software engineer doing code review."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.2,
        )

        return {
            "syntax": analysis["syntax"],
            "static_issues": analysis["issues"],
            "ai_review": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
            "mode": "openai_review",
        }
    except Exception as e:
        print(f"LLM Error: {e}")
        return None


def review(code):
    """Main entry point."""
    print(f"[Mode: {MODE}] Reviewing code ({len(code.splitlines())} lines)...")

    if is_demo():
        return review_demo(code)
    elif OPENAI_API_KEY:
        return review_llm(code)
    else:
        return review_demo(code)


# ─── CLI ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Automated Code Review System")
    parser.add_argument("--file", default=None, help="Path to Python file to review")
    parser.add_argument("--code", default=None, help="Inline code string to review")
    args = parser.parse_args()

    if args.file and os.path.isfile(args.file):
        with open(args.file) as f:
            code = f.read()
    elif args.code:
        code = args.code
    else:
        # Sample code for demo
        code = '''
import os
import json

def fetch_data(url):
    password = "admin123"
    result = eval(url)
    data = json.loads(result)
    return data

def process_items(items):
    output = []
    for i in range(len(items)):
        item = items[i]
        if item > 0:
            output.append(item * 2)
    return output
'''

    result = review(code)
    if result:
        print("\n" + "=" * 60)
        print("  🔍 Code Review Results")
        print("=" * 60)
        print(f"\nSyntax: {result['syntax']['status']}")
        if result.get("issues"):
            print(f"\nStatic Analysis Issues ({len(result['issues'])}):")
            for issue in result["issues"]:
                icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(issue["severity"], "•")
                print(f"  {icon} Line {issue['line']}: {issue['message']}")
        if result.get("ai_review"):
            print(f"\nAI Review:\n{result['ai_review']}")
        print(f"\n[Mode: {result['mode']}]")


if __name__ == "__main__":
    main()
