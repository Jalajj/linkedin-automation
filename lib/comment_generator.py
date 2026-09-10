"""
Comment Generator - Uses OpenRouter + Claude skills to draft LinkedIn comments.

Integrates with the installed LinkedIn skills for template-based generation.
"""

import os
import json
from typing import List, Dict, Optional
import httpx
from datetime import datetime


class CommentGenerator:
    """Generates LinkedIn comment variants using AI models via OpenRouter."""

    # Comment templates based on linkedin-skills/comment-templates
    TEMPLATES = {
        "missing_piece": {
            "name": "T1 Missing-Piece",
            "pattern": "{name} the {their_thesis} argument misses one piece. {what_moved}. When {condition}, the real differentiator is {skill}, not {their_focus}.",
            "hit_rate": "highest"
        },
        "answer_question": {
            "name": "T2 Answer-the-Closing-Question",
            "pattern": "{answer}\n\n{example}. {why_it_matters}",
            "hit_rate": "high"
        },
        "data_first": {
            "name": "T2 Data-First",
            "pattern": "Half the {population} I see now {behavior}. The {old_assumption} broke around {date}. {new_rule}.",
            "hit_rate": "medium"
        },
        "practitioner": {
            "name": "T4 Practitioner Observation",
            "pattern": "When X, the system does Y. When X', it does Y'. That's when {outcome} kicks in.",
            "hit_rate": "medium"
        },
        "counter_concession": {
            "name": "T5 Counter-with-Concession",
            "pattern": "Agree on: {point1}. Push back on: {point2} — {reason}.",
            "hit_rate": "medium-high"
        },
        "quotable_reframe": {
            "name": "T6 Quotable-Reframe",
            "pattern": "{one_liner} {expansion}",
            "hit_rate": "low-medium"
        },
        "sharper_question": {
            "name": "T7 Ask-a-Sharper-Question",
            "pattern": "The harder version of this question is: {question}",
            "hit_rate": "high"
        }
    }

    # Voice profiles for different tones
    VOICE_PROFILES = {
        "professional": {
            "style": "concise, data-backed, avoids buzzwords, cites specifics",
            "vocabulary": ["strategic", "leveraged", "impact", "metrics", "execution"],
            "phrase_endings": [".", " — especially in", " — notably when"]
        },
        "analytical": {
            "style": "structured, hypothesis-driven, references frameworks",
            "vocabulary": ["hypothesis", "variable", "correlation", "causation", "regression"],
            "phrase_endings": ["; the data shows", " — which validates"]
        },
        "casual": {
            "style": "conversational, uses contractions, personal examples",
            "vocabulary": ["yeah", "actually", "honestly", "turns out", "kind of"],
            "phrase_endings": [". I found that", " — and that's the thing:"]
        },
        "witty": {
            "style": "sharp, ironic contrasts, mild humor, cultural references",
            "vocabulary": ["ironic", "surprise", "paradox", "plot twist", "ironically"],
            "phrase_endings": [". The plot thickens:", " — which is hilarious because"]
        },
        "nuanced": {
            "style": "acknowledges complexity, avoids absolutes, explores trade-offs",
            "vocabulary": ["on the other hand", "however", "tension between", "depends on", "context matters"],
            "phrase_endings": [", but there's a catch:", " — though it depends on "]
        }
    }

    def __init__(self, api_key: str = None, voice_profile: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.voice_profile_path = voice_profile or os.getenv("VOICE_PROFILE_PATH")
        self.voice_profile = self._load_voice_profile()

    def _load_voice_profile(self) -> Dict:
        """Load user's voice profile if available."""
        if self.voice_profile_path and os.path.exists(self.voice_profile_path):
            with open(self.voice_profile_path, "r") as f:
                return json.load(f)
        return {}

    def generate_comments(self, post_content: str, tone: str = "professional",
                          existing_comments: List[str] = None,
                          author_name: str = "Author") -> List[Dict]:
        """Generate multiple comment variants for a LinkedIn post."""
        existing_comments = existing_comments or []
        existing_texts = [c.get("text", "") if isinstance(c, dict) else str(c)
                          for c in existing_comments]

        # Detect post type and closing question
        post_type = self._analyze_post(post_content)
        voice = self.VOICE_PROFILES.get(tone, self.VOICE_PROFILES["professional"])

        if self.api_key:
            return self._generate_via_api(post_content, tone, existing_texts,
                                         author_name, post_type, voice)
        else:
            return self._generate_fallback(post_content, tone,
                                           existing_texts, author_name,
                                           post_type, voice)

    def _analyze_post(self, text: str) -> Dict:
        """Analyze post for type, question, sentiment."""
        result = {
            "has_closing_question": "?" in text[-200:],
            "is_listicle": any(word in text.lower() for word in ["5 ways", "10 tips", "3 things"]),
            "is_thread": text.count("\n\n") > 5,
            "sentiment": "positive" if any(w in text.lower() for w in ["excited", "proud", "thrilled"]) else "neutral",
            "closing_question": ""
        }

        # Extract closing question if present
        if result["has_closing_question"]:
            sentences = text.split(".")
            for s in reversed(sentences[-3:]):
                if "?" in s:
                    result["closing_question"] = s.strip()
                    break

        return result

    def _generate_via_api(self, post_content: str, tone: str,
                          existing_comments: List[str],
                          author_name: str, post_type: Dict,
                          voice: Dict) -> List[Dict]:
        """Generate comments using OpenRouter API."""
        existing_context = "\n".join([f"- {c}" for c in existing_comments[:5]]) or "None"

        prompt = f"""Generate exactly 3 LinkedIn comment variants (250 chars max each) on this post:

Post by {author_name}:
{post_content[:1000]}

Existing comments (don't repeat):
{existing_context}

Tone: {tone}
Voice style: {voice['style']}

Constraints:
- Always capitalize the author's name when addressing them by first name
- No hashtags, no emoji
- No generic praise like "Great post!"
- Each variant should use a different template approach
- Add an odd-precision number if possible

Format as JSON:
{{
  "variants": [
    {{
      "text": "...",
      "reaction": "LIKE|PRAISE|INTEREST|EMPATHY|APPRECIATION|ENTERTAINMENT",
      "pattern": "T1|T2|T3|T4|T5|T6|T7",
      "rationale": "why this template fits"
    }}
  ]
}}"""

        try:
            response = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "https://github.com/Jalajj/linkedin-automation",
                    "X-Title": "LinkedIn Comment Bot",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek/deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "You are a LinkedIn engagement specialist. Generate high-quality comment drafts that get author replies. Return JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]

                # Parse JSON from response
                try:
                    data = json.loads(content)
                    return data.get("variants", [])
                except json.JSONDecodeError:
                    # Extract JSON if embedded in text
                    start = content.find("{")
                    end = content.rfind("}") + 1
                    if start >= 0 and end > start:
                        data = json.loads(content[start:end])
                        return data.get("variants", [])
                    return []

        except Exception as e:
            print(f"API error: {e}")

        # Fallback to template-based
        return self._generate_fallback(post_content, tone,
                                       existing_comments, author_name,
                                       post_type, voice)

    def _generate_fallback(self, post_content: str, tone: str,
                           existing_comments: List[str],
                           author_name: str, post_type: Dict,
                           voice: Dict) -> List[Dict]:
        """Generate comments without API (template-based)."""
        author_first = author_name.split()[0] if author_name else "Author"

        variants = []

        # Template 1: Missing-Piece (highest hit rate)
        variants.append({
            "text": f"{author_first} the platform-first approach misses one piece — the adoption curve flattens around month 3 for 62% of teams. When the initial hype dies, retention depends on workflow integration, not feature breadth.",
            "reaction": "INTEREST",
            "pattern": "T1",
            "rationale": "F1 Platform Risk Anaphora - addresses the core thesis with data",
            "char_count": 231
        })

        # Template 2: Answer-the-Closing-Question (if present)
        if post_type["has_closing_question"]:
            variants.append({
                "text": f"The harder version of this question is: not \"how to adopt AI\" but \"which 27% of workflows actually need it.\" We've seen teams waste 4 months automating tasks that don't compound.",
                "reaction": "PRAISE",
                "pattern": "T2",
                "rationale": "T7 Ask-a-Sharper-Question - sharpens the author's framing",
                "char_count": 244
            })
        else:
            variants.append({
                "text": "The data from 157 teams shows the same bottleneck: onboarding. Not feature gaps — time-to-first-value. Teams that hit 4 hours see 3.2x faster expansion rates.",
                "reaction": "INTEREST",
                "pattern": "T3",
                "rationale": "T3 Data-First - anchors claim in specific numbers",
                "char_count": 231
            })

        # Template 3: Practitioner Observation
        variants.append({
            "text": "When the system gets 100 users, it reveals friction. When it gets 1000, it reveals architecture. That's when the real product decisions kick in.",
            "reaction": "APPRECIATION",
            "pattern": "T4",
            "rationale": "T4 Practitioner Observation - shares hard-won insight",
            "char_count": 219
        })

        # Filter out any that are too long
        variants = [v for v in variants if v["char_count"] <= 350]
        return variants[:3]


# Import datetime for timestamp fields
from datetime import datetime