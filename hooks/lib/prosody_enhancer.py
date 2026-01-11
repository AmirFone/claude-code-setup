"""
Prosody enhancement for voice output.
Enhances voice output with emotional markers and natural speech patterns.

Migrated from ~/.config/pai/hooks/lib/prosody-enhancer.ts
"""

import os
import re
import random
from typing import Optional, Dict, Any


# Agent personality configurations
AGENT_PERSONALITIES: Dict[str, Dict[str, Any]] = {
    "default": {
        "name": "Assistant",
        "rate_wpm": 235,
        "stability": 0.38,
        "archetype": "professional",
        "energy_level": "expressive"
    },
    "intern": {
        "name": "Intern",
        "rate_wpm": 270,
        "stability": 0.30,
        "archetype": "enthusiast",
        "energy_level": "chaotic"
    },
    "pentester": {
        "name": "Pentester",
        "rate_wpm": 260,
        "stability": 0.18,
        "archetype": "enthusiast",
        "energy_level": "chaotic"
    },
    "artist": {
        "name": "Artist",
        "rate_wpm": 215,
        "stability": 0.20,
        "archetype": "enthusiast",
        "energy_level": "chaotic"
    },
    "designer": {
        "name": "Designer",
        "rate_wpm": 226,
        "stability": 0.52,
        "archetype": "critic",
        "energy_level": "measured"
    },
    "engineer": {
        "name": "Engineer",
        "rate_wpm": 212,
        "stability": 0.72,
        "archetype": "wise-leader",
        "energy_level": "stable"
    },
    "architect": {
        "name": "Architect",
        "rate_wpm": 205,
        "stability": 0.75,
        "archetype": "wise-leader",
        "energy_level": "stable"
    },
    "researcher": {
        "name": "Researcher",
        "rate_wpm": 229,
        "stability": 0.64,
        "archetype": "analyst",
        "energy_level": "measured"
    },
    "writer": {
        "name": "Writer",
        "rate_wpm": 230,
        "stability": 0.48,
        "archetype": "storyteller",
        "energy_level": "expressive"
    }
}

# Content patterns for detecting emotional context
CONTENT_PATTERNS = {
    "excited": [
        r"\b(breakthrough|discovered|found it|eureka|amazing|incredible)\b",
        r"\b(wait wait|ooh|wow|check this|look at this)\b",
        r"!{2,}|[💥🔥⚡]"
    ],
    "celebration": [
        r"\b(finally|at last|phew|we did it|victory)\b",
        r"\b(all .* passing|zero errors|zero (data )?loss)\b",
        r"[🎉🥳🍾]"
    ],
    "insight": [
        r"\b(wait|aha|I see|that'?s why|now I understand)\b",
        r"\b(this explains|the real issue|actually)\b",
        r"[💡🔦]"
    ],
    "success": [
        r"\b(completed|finished|done|success|working|fixed|resolved|solved)\b",
        r"\b(all tests? pass|deploy|ship|launch)\b",
        r"[✅✨]"
    ],
    "progress": [
        r"\b(phase .* complete|step .* done)\b",
        r"\b(moving to|now|next|partial|incremental)\b",
        r"[📈⏩]"
    ],
    "investigating": [
        r"\b(analyzing|examining|investigating|tracing)\b",
        r"\b(pattern detected|correlation|cross-referencing)\b",
        r"[🔍🔬📊]"
    ],
    "debugging": [
        r"\b(bug|error|issue|problem)\b",
        r"\b(tracking|hunting|found it|located)\b",
        r"[🐛🔧]"
    ],
    "caution": [
        r"\b(warning|careful|slow|partial|incomplete)\b",
        r"\b(needs review|check|verify)\b",
        r"[⚠️⚡]"
    ],
    "urgent": [
        r"\b(urgent|critical|down|failing|broken|alert)\b",
        r"\b(immediate|asap|now|quickly|emergency)\b",
        r"[🚨❌⛔]"
    ]
}

# Emotional markers
EMOTIONAL_MARKERS = {
    "excited": "[excited]",
    "celebration": "[celebration]",
    "insight": "[insight]",
    "success": "[success]",
    "progress": "[progress]",
    "investigating": "[investigating]",
    "debugging": "[debugging]",
    "caution": "[caution]",
    "urgent": "[urgent]"
}


def detect_emotional_context(message: str) -> Optional[str]:
    """Detect emotional context from message content."""
    # Check for existing emotional markers
    if re.search(r"\[[💥✨⚠️🚨🎉💡🤔🔍📈🎯🎨🐛📚]", message):
        return None  # Already has marker

    priority_order = [
        "urgent", "debugging", "insight", "celebration", "excited",
        "investigating", "progress", "success", "caution"
    ]

    for emotion in priority_order:
        patterns = CONTENT_PATTERNS.get(emotion, [])
        for pattern in patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return emotion

    return None


def add_personality_prosody(message: str, personality: Dict[str, Any]) -> str:
    """Add personality-specific prosody patterns."""
    enhanced = message
    archetype = personality.get("archetype", "professional")
    energy = personality.get("energy_level", "expressive")

    if archetype == "enthusiast" and energy == "chaotic":
        if "..." not in enhanced and random.random() > 0.5:
            enhanced = re.sub(r"\b(wait|found|check|look)\b", r"\1...", enhanced, flags=re.IGNORECASE)
        if not re.search(r"[!?]$", enhanced):
            enhanced = re.sub(r"\.$", "!", enhanced)

    elif archetype == "wise-leader" and energy == "stable":
        if "," in enhanced:
            enhanced = re.sub(r",\s+", " -- ", enhanced, count=1)

    elif archetype == "professional" and energy == "expressive":
        if "**" not in enhanced:
            enhanced = re.sub(
                r"\b(completed|fixed|deployed|built|created|found)\b",
                r"**\1**",
                enhanced,
                flags=re.IGNORECASE
            )

    elif archetype == "analyst":
        enhanced = re.sub(
            r"\b(confirmed|verified|analyzed|discovered)\b",
            r"**\1**",
            enhanced,
            flags=re.IGNORECASE
        )

    elif archetype == "storyteller":
        if enhanced[0:1].isupper() and "..." not in enhanced:
            enhanced = re.sub(r"\. ([A-Z])", r"... \1", enhanced)

    return enhanced


def enhance_prosody(
    message: str,
    agent_type: str,
    emotional_markers: bool = True,
    markdown_prosody: bool = True,
    personality_enhancement: bool = True,
    context_analysis: bool = True
) -> str:
    """Main prosody enhancement function."""
    enhanced = message

    personality = AGENT_PERSONALITIES.get(
        agent_type.lower(),
        AGENT_PERSONALITIES["default"]
    )

    # 1. Context Analysis - Detect emotional context
    if context_analysis and emotional_markers:
        emotion = detect_emotional_context(enhanced)
        if emotion:
            marker = EMOTIONAL_MARKERS.get(emotion, "")
            if marker:
                enhanced = f"{marker} {enhanced}"

    # 2. Personality Enhancement
    if personality_enhancement and markdown_prosody:
        enhanced = add_personality_prosody(enhanced, personality)

    return enhanced.strip()


def clean_for_speech(message: str) -> str:
    """Clean message for speech while preserving prosody."""
    cleaned = message

    # Remove code blocks and inline code
    cleaned = re.sub(r"```[\s\S]*?```", "code block", cleaned)
    cleaned = re.sub(r"`[^`]+`", "", cleaned)

    # Strip emoji while preserving text in brackets
    parts = []
    last_index = 0
    for match in re.finditer(r"\[[^\]]+\]", cleaned):
        if match.start() > last_index:
            parts.append({"is_marker": False, "text": cleaned[last_index:match.start()]})
        parts.append({"is_marker": True, "text": match.group(0)})
        last_index = match.end()

    if last_index < len(cleaned):
        parts.append({"is_marker": False, "text": cleaned[last_index:]})

    if not parts:
        parts = [{"is_marker": False, "text": cleaned}]

    # Strip emoji from non-marker parts only
    result_parts = []
    for part in parts:
        if part["is_marker"]:
            result_parts.append(part["text"])
        else:
            # Remove common emoji
            text = re.sub(r"[\U0001F300-\U0001F9FF]", "", part["text"])
            result_parts.append(text)

    cleaned = "".join(result_parts)

    # Clean up whitespace
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()


def get_voice_id(agent_type: str) -> str:
    """Get the voice ID for an agent type."""
    # Read from environment
    env_key = f"ELEVENLABS_VOICE_{agent_type.upper()}"
    env_voice = os.environ.get(env_key)
    if env_voice:
        return env_voice

    # Fallback to default
    return os.environ.get("ELEVENLABS_VOICE_DEFAULT", "")
