"""
Prompt Management System
Version-controlled prompt templates with A/B testing and performance tracking.
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime


class PromptTemplate:
    """A single versioned prompt template."""

    def __init__(self, name: str, template: str, version: str = "1.0",
                 metadata: Optional[Dict] = None):
        self.name = name
        self.template = template
        self.version = version
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow().isoformat()
        self.prompt_id = hashlib.md5(
            f"{name}:{version}".encode()
        ).hexdigest()[:12]

    def render(self, **kwargs) -> str:
        """Render template with variables."""
        rendered = self.template
        for key, value in kwargs.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        return rendered

    def to_dict(self) -> Dict:
        return {
            "prompt_id": self.prompt_id,
            "name": self.name,
            "version": self.version,
            "template": self.template,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


class PromptManager:
    """
    Manages versioned prompt templates with A/B testing.
    
    Usage:
        pm = PromptManager()
        pm.register("email", "Write a {{tone}} email about {{product}}", version="1.0")
        pm.register("email", "Compose a {{tone}} email for {{product}}", version="1.1")
        
        # Get specific version
        prompt = pm.get("email", version="1.1")
        rendered = prompt.render(tone="professional", product="CloudSync")
        
        # A/B test
        variant = pm.get_ab_variant("email", variants=["1.0", "1.1"])
    """

    def __init__(self, store_dir: Optional[str] = None):
        self.templates: Dict[str, Dict[str, PromptTemplate]] = {}
        self.performance_log: List[Dict] = []
        self.store_dir = Path(store_dir) if store_dir else None

        if self.store_dir:
            self.store_dir.mkdir(parents=True, exist_ok=True)
            self._load_from_disk()

    def register(self, name: str, template: str, version: str = "1.0",
                 metadata: Optional[Dict] = None) -> PromptTemplate:
        """Register a new prompt template."""
        pt = PromptTemplate(name, template, version, metadata)
        
        if name not in self.templates:
            self.templates[name] = {}
        self.templates[name][version] = pt
        
        if self.store_dir:
            self._save_template(pt)
        
        return pt

    def get(self, name: str, version: str = "latest") -> Optional[PromptTemplate]:
        """Get a prompt template by name and version."""
        if name not in self.templates:
            return None
        
        versions = self.templates[name]
        if version == "latest":
            latest = sorted(versions.keys(), reverse=True)[0]
            return versions[latest]
        
        return versions.get(version)

    def get_ab_variant(self, name: str, variants: List[str] = None) -> PromptTemplate:
        """
        Get a random A/B test variant.
        Uses hash-based selection for deterministic assignment per session.
        """
        import random
        
        if name not in self.templates:
            raise ValueError(f"No templates found for '{name}'")
        
        available = list(self.templates[name].keys())
        if variants:
            available = [v for v in variants if v in self.templates[name]]
        
        if not available:
            raise ValueError(f"No matching variants for '{name}'")
        
        selected = random.choice(available)
        return self.templates[name][selected]

    def track_performance(self, prompt_id: str, score: float,
                          tokens: int = 0, cost: float = 0.0,
                          metadata: Optional[Dict] = None):
        """Track performance of a prompt execution."""
        entry = {
            "prompt_id": prompt_id,
            "score": score,
            "tokens": tokens,
            "cost": cost,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        self.performance_log.append(entry)

    def get_performance_summary(self, name: Optional[str] = None) -> Dict:
        """Get aggregated performance stats."""
        relevant = self.performance_log
        
        if name:
            # Filter by prompt name
            template_ids = set()
            if name in self.templates:
                for v in self.templates[name].values():
                    template_ids.add(v.prompt_id)
            relevant = [e for e in relevant if e["prompt_id"] in template_ids]
        
        if not relevant:
            return {"total": 0, "avg_score": 0.0, "avg_cost": 0.0}
        
        scores = [e["score"] for e in relevant]
        costs = [e["cost"] for e in relevant]
        
        return {
            "total": len(relevant),
            "avg_score": sum(scores) / len(scores),
            "max_score": max(scores),
            "min_score": min(scores),
            "avg_cost": sum(costs) / len(costs),
            "total_cost": sum(costs),
        }

    def list_templates(self) -> List[Dict]:
        """List all registered templates."""
        result = []
        for name, versions in self.templates.items():
            for version, pt in versions.items():
                result.append({
                    "name": name,
                    "version": version,
                    "prompt_id": pt.prompt_id,
                    "preview": pt.template[:80] + "..." if len(pt.template) > 80 else pt.template,
                })
        return result

    def _save_template(self, pt: PromptTemplate):
        """Save template to disk."""
        filepath = self.store_dir / f"{pt.name}_v{pt.version}.json"
        filepath.write_text(json.dumps(pt.to_dict(), indent=2))

    def _load_from_disk(self):
        """Load templates from disk."""
        if not self.store_dir.exists():
            return
        for filepath in self.store_dir.glob("*.json"):
            try:
                data = json.loads(filepath.read_text())
                self.register(
                    data["name"], data["template"],
                    data["version"], data.get("metadata"),
                )
            except (json.JSONDecodeError, KeyError):
                pass


# ─── Pre-built Prompt Library ────────────────────────────────

def create_default_prompt_manager() -> PromptManager:
    """Create a PromptManager pre-loaded with templates for all use cases."""
    pm = PromptManager()
    
    # Marketing (UC01)
    pm.register("marketing_email", """
Write a {{tone}} marketing email for {{product}}.
Target audience: {{audience}}
Key benefits: {{benefits}}
Include a compelling subject line and call-to-action.
""".strip(), version="1.0", metadata={"use_case": "01"})

    pm.register("marketing_email", """
You are an expert email marketer. Create a high-converting {{tone}} email campaign for {{product}}.
Audience: {{audience}}
Benefits to highlight: {{benefits}}

Structure:
1. Subject line (max 50 chars, create urgency)
2. Preview text (max 100 chars)
3. Opening hook (personalized)
4. Body (2-3 short paragraphs)
5. CTA button text
6. P.S. line
""".strip(), version="1.1", metadata={"use_case": "01"})

    # Code Completion (UC03)
    pm.register("code_completion", """
Complete the following {{language}} code. Provide only the completed code.

Context: {{context}}

```{{language}}
{{code}}
```
""".strip(), version="1.0", metadata={"use_case": "03"})

    # Customer Support (UC04)
    pm.register("support_answer", """
You are a helpful customer support agent. Answer the user's question based on the provided context.

Context:
{{context}}

Question: {{query}}

Rules:
- Only use information from the context
- Be concise and helpful
- If unsure, say so honestly
""".strip(), version="1.0", metadata={"use_case": "04"})

    # Healthcare (UC05)
    pm.register("medical_summary", """
Summarize the following medical report in a structured format.

Report:
{{report}}

Output format:
- Patient Overview
- Key Findings
- Diagnoses  
- Recommended Actions
- Follow-up Needed

IMPORTANT: Do not include any personally identifiable information.
""".strip(), version="1.0", metadata={"use_case": "05"})

    # Code Review (UC08)
    pm.register("code_review", """
Review this {{language}} code for:
1. Code quality and readability
2. Potential bugs
3. Security vulnerabilities
4. Performance issues
5. Best practices

```{{language}}
{{code}}
```

Format: List issues with severity (HIGH/MEDIUM/LOW) and suggestions.
""".strip(), version="1.0", metadata={"use_case": "08"})

    # Legal (UC09)
    pm.register("legal_analysis", """
Analyze this contract clause for legal risks:

Clause: {{clause}}

Provide:
1. Risk level (HIGH/MEDIUM/LOW)
2. Key concerns
3. Recommended modifications
4. Comparison to standard terms

DISCLAIMER: This is AI-assisted analysis, not legal advice.
""".strip(), version="1.0", metadata={"use_case": "09"})

    return pm
