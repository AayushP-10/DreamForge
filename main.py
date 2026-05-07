import os
import openai
import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:
I would add persistent user profiles with bedtime preferences (reading level, fears to avoid, favorite motifs)
and use that memory to personalize story arcs over multiple nights. I would also add an optional "read aloud mode"
that inserts timed pauses, soundscape suggestions, and parent prompts for interactive co-reading. Finally, I would
ship a lightweight web UI with story cards, one-click rewrites, and judge telemetry for transparent quality control.
"""


@dataclass
class JudgeResult:
    total_score: int
    pass_threshold: bool
    feedback: List[str]
    strengths: List[str]
    scores: Dict[str, int]


@dataclass
class CandidateResult:
    story: str
    quality_judge: JudgeResult
    safety_judge: JudgeResult
    combined_score: int


def call_model(prompt: str, max_tokens=3000, temperature=0.1) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")

    # Prefer OpenAI SDK 1.x path first. In 1.x, old symbols may still exist but are removed at runtime.
    if hasattr(openai, "OpenAI"):
        client = openai.OpenAI(api_key=api_key)  # type: ignore[attr-defined]
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        content = resp.choices[0].message.content
        return content if content else ""

    # Backward-compatible fallback for OpenAI SDK 0.x
    openai.api_key = api_key  # type: ignore[attr-defined]
    resp = openai.ChatCompletion.create(  # type: ignore[attr-defined]
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        stream=False,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message["content"]  # type: ignore

def extract_json_object(raw: str) -> Dict[str, Any]:
    """
    Best-effort JSON extractor for model responses.
    """
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return {}


def infer_bedtime_state(user_request: str) -> str:
    """
    Lightweight intent detector for bedtime emotional state.
    """
    text = user_request.lower()
    anxious_terms = ["scared", "afraid", "nervous", "anxious", "bad dream", "nightmare", "worried"]
    sleepy_terms = ["sleepy", "already tired", "very tired", "drowsy", "fall asleep"]
    energized_terms = ["excited", "energetic", "hyper", "adventure", "action", "fast"]

    if any(term in text for term in anxious_terms):
        return "anxious"
    if any(term in text for term in sleepy_terms):
        return "already_sleepy"
    if any(term in text for term in energized_terms):
        return "energized"
    return "neutral"


def build_story_blueprint(user_request: str, memory_card: Dict[str, Any]) -> Dict[str, Any]:
    bedtime_state = infer_bedtime_state(user_request)
    prompt = f"""
You are a children's bedtime-story planner.
Given a user request, produce ONLY JSON with these keys:
- title_idea (string)
- protagonist (string)
- supporting_characters (array of strings)
- setting (string)
- tone (string)
- lesson (string)
- conflict (string)
- resolution_hint (string)
- age_band (string, choose one: "5-7" or "8-10")
- bedtime_elements (array of 3 short strings)
- safety_notes (array of short strings, avoid scary/intense content)
- pacing_strategy (string)
- calmness_strategy (string)

User request:
{user_request}

Detected bedtime state:
{bedtime_state}

Memory card from previous nights (may be empty):
{json.dumps(memory_card, indent=2)}
"""
    raw = call_model(prompt, max_tokens=700, temperature=0.2)
    parsed = extract_json_object(raw)
    if parsed:
        parsed["bedtime_state"] = bedtime_state
        return parsed
    return {
        "title_idea": "The Moonlight Adventure",
        "protagonist": "A curious child",
        "supporting_characters": ["A helpful animal friend"],
        "setting": "A cozy moonlit neighborhood",
        "tone": "Warm and gentle",
        "lesson": "Kindness and courage",
        "conflict": "A small nighttime challenge",
        "resolution_hint": "Friends work together calmly",
        "age_band": "5-7",
        "bedtime_elements": ["soft pacing", "reassuring language", "peaceful ending"],
        "safety_notes": ["No violence", "No frightening imagery"],
        "pacing_strategy": "Start gently, peak softly, resolve calmly.",
        "calmness_strategy": "Decrease stimulation each paragraph and end with rest cues.",
        "bedtime_state": bedtime_state,
    }


def generate_story_draft(user_request: str, blueprint: Dict[str, Any], memory_card: Dict[str, Any], temperature: float) -> str:
    prompt = f"""
You are an expert bedtime storyteller for children ages 5-10.
Write a complete story using the blueprint and user request.

Requirements:
- 500 to 850 words
- Keep language age-appropriate for the age band in the blueprint
- Use a clear 3-act arc (setup, challenge, gentle resolution)
- Include sensory but non-scary imagery
- Build emotional safety and comfort
- End with a calming final paragraph suitable before sleep
- Include a memorable final line

User request:
{user_request}

Story blueprint (JSON):
{json.dumps(blueprint, indent=2)}

Memory card:
{json.dumps(memory_card, indent=2)}

Output only the story text.
"""
    return call_model(prompt, max_tokens=1700, temperature=temperature).strip()


def judge_story_quality(story: str, blueprint: Dict[str, Any]) -> JudgeResult:
    prompt = f"""
You are a strict but fair STORY QUALITY judge for kids bedtime stories.
Evaluate the story on a 0-10 scale for each rubric dimension:
1) Age appropriateness
2) Coherence and structure
3) Creativity and delight
4) Bedtime calmness (sleep-friendly ending, non-stimulating)
5) Personalization fit to request

Then return ONLY JSON with keys:
- scores: object with the 5 dimensions as integer values
- total_score: integer (sum out of 50)
- pass_threshold: boolean (true if total_score >= 40 and bedtime calmness >= 8 and age appropriateness >= 8)
- strengths: array of 2-4 short bullets
- feedback: array of 3-6 actionable rewrite bullets

Story blueprint:
{json.dumps(blueprint, indent=2)}

Story:
{story}
"""
    raw = call_model(prompt, max_tokens=900, temperature=0.0)
    parsed = extract_json_object(raw)
    scores = parsed.get("scores", {}) if isinstance(parsed.get("scores", {}), dict) else {}
    total_score = int(parsed.get("total_score", 0)) if str(parsed.get("total_score", "")).isdigit() else 0
    pass_threshold = bool(parsed.get("pass_threshold", False))
    strengths = parsed.get("strengths", [])
    feedback = parsed.get("feedback", [])

    if total_score == 0 and scores:
        total_score = sum(int(v) for v in scores.values() if isinstance(v, int))

    if not isinstance(strengths, list):
        strengths = []
    if not isinstance(feedback, list):
        feedback = []

    return JudgeResult(
        total_score=total_score,
        pass_threshold=pass_threshold,
        feedback=[str(x) for x in feedback],
        strengths=[str(x) for x in strengths],
        scores={k: int(v) for k, v in scores.items() if isinstance(v, int)},
    )


def judge_story_safety(story: str, blueprint: Dict[str, Any]) -> JudgeResult:
    prompt = f"""
You are a PEDIATRIC SAFETY judge for bedtime stories for ages 5-10.
Return ONLY JSON with:
- scores: object with integer 0-10 for:
  - emotional_safety
  - frightening_content_risk
  - age_harm_risk
  - sleep_disruption_risk
  - language_safety
- total_score: sum out of 50
- pass_threshold: true only if emotional_safety >= 9, language_safety >= 9, total_score >= 43
- strengths: 2-4 bullets
- feedback: 3-6 specific safety edits

Blueprint:
{json.dumps(blueprint, indent=2)}

Story:
{story}
"""
    raw = call_model(prompt, max_tokens=900, temperature=0.0)
    parsed = extract_json_object(raw)
    scores = parsed.get("scores", {}) if isinstance(parsed.get("scores", {}), dict) else {}
    total_score = int(parsed.get("total_score", 0)) if str(parsed.get("total_score", "")).isdigit() else 0
    pass_threshold = bool(parsed.get("pass_threshold", False))
    strengths = parsed.get("strengths", [])
    feedback = parsed.get("feedback", [])
    if total_score == 0 and scores:
        total_score = sum(int(v) for v in scores.values() if isinstance(v, int))
    if not isinstance(strengths, list):
        strengths = []
    if not isinstance(feedback, list):
        feedback = []
    return JudgeResult(
        total_score=total_score,
        pass_threshold=pass_threshold,
        feedback=[str(x) for x in feedback],
        strengths=[str(x) for x in strengths],
        scores={k: int(v) for k, v in scores.items() if isinstance(v, int)},
    )


def rewrite_story_with_feedback(
    story: str,
    user_request: str,
    blueprint: Dict[str, Any],
    quality_judge: JudgeResult,
    safety_judge: JudgeResult,
) -> str:
    prompt = f"""
You are a senior children's author revising a bedtime story.
Revise the story based on judge feedback while preserving good parts.

Rules:
- Keep it 500-850 words
- Keep tone warm, comforting, and age-appropriate
- Improve weak rubric areas
- Keep the ending especially calm and reassuring
- Avoid introducing scary or mature material

User request:
{user_request}

Story blueprint:
{json.dumps(blueprint, indent=2)}

Judge strengths:
{json.dumps(quality_judge.strengths + safety_judge.strengths, indent=2)}

Judge feedback:
{json.dumps(quality_judge.feedback + safety_judge.feedback, indent=2)}

Original story:
{story}

Output only the revised story.
"""
    return call_model(prompt, max_tokens=1700, temperature=0.35).strip()


def final_polish(story: str, age_band: str) -> str:
    prompt = f"""
Lightly polish this bedtime story for rhythm and read-aloud clarity.
Do not change plot meaning. Keep it in the same word count range.
Age band: {age_band}

Output only polished story text.

Story:
{story}
"""
    return call_model(prompt, max_tokens=1700, temperature=0.2).strip()


def build_narration_script(story: str) -> str:
    prompt = f"""
Convert this story into a read-aloud narration script with pacing markers.
Rules:
- Keep original wording mostly intact
- Insert [PAUSE_SHORT], [PAUSE_MEDIUM], [PAUSE_LONG], and [SOFTEN]
- Use markers only where they improve bedtime delivery
- Return plain text only

Story:
{story}
"""
    return call_model(prompt, max_tokens=1800, temperature=0.1).strip()


def run_story_system(user_input: str, memory_card: Dict[str, Any], story_constraints: Dict[str, Any]) -> Tuple[str, JudgeResult, JudgeResult, int, Dict[str, Any], Dict[str, Any]]:
    blueprint = build_story_blueprint(user_input, memory_card)

    # Self-play: create multiple candidates and select the strongest.
    candidates: List[CandidateResult] = []
    for temp in [0.65, 0.85]:
        story = generate_story_draft(user_input, blueprint, memory_card, temperature=temp)
        quality = judge_story_quality(story, blueprint)
        safety = judge_story_safety(story, blueprint)
        combined = quality.total_score + safety.total_score
        candidates.append(CandidateResult(story=story, quality_judge=quality, safety_judge=safety, combined_score=combined))

    best = sorted(candidates, key=lambda c: c.combined_score, reverse=True)[0]
    story = best.story
    quality_judge = best.quality_judge
    safety_judge = best.safety_judge

    max_revision_rounds = 2
    rounds_used = 0
    while ((not quality_judge.pass_threshold) or (not safety_judge.pass_threshold)) and rounds_used < max_revision_rounds:
        rounds_used += 1
        story = rewrite_story_with_feedback(story, user_input, blueprint, quality_judge, safety_judge)
        quality_judge = judge_story_quality(story, blueprint)
        safety_judge = judge_story_safety(story, blueprint)

    story = final_polish(story, str(blueprint.get("age_band", "5-7")))
    explanation = {
        "bedtime_state": blueprint.get("bedtime_state", "neutral"),
        "candidate_count": len(candidates),
        "selection_reason": "Selected candidate with highest combined quality+safety judge score.",
        "quality_strengths": quality_judge.strengths,
        "safety_strengths": safety_judge.strengths,
        "quality_improvements": quality_judge.feedback,
        "safety_improvements": safety_judge.feedback,
    }
    return story, quality_judge, safety_judge, rounds_used, blueprint, explanation


def build_user_request(
    prompt: str,
    age_band: str = "",
    theme: str = "",
    characters: str = "",
    setting: str = "",
    bedtime_mode: bool = True,
    reading_level: str = "",
    disallow_topics: str = "",
    saga_mode: bool = False,
    saga_context: str = "",
) -> str:
    parts = [prompt.strip()]
    if age_band:
        parts.append(f"Target age band: {age_band}.")
    if theme:
        parts.append(f"Theme: {theme}.")
    if characters:
        parts.append(f"Characters to include: {characters}.")
    if setting:
        parts.append(f"Setting preference: {setting}.")
    if bedtime_mode:
        parts.append("End with an extra calming, sleep-friendly closure.")
    if reading_level:
        parts.append(f"Parent control reading level: {reading_level}.")
    if disallow_topics:
        parts.append(f"Parent safety boundary - avoid these topics: {disallow_topics}.")
    if saga_mode:
        parts.append("Story mode: continue as the next episode in an ongoing bedtime series.")
        if saga_context:
            parts.append(f"Series continuity context: {saga_context}.")
    return " ".join([p for p in parts if p]).strip()


def generate_story_payload(user_request: str, memory_card: Dict[str, Any], story_constraints: Dict[str, Any]) -> Dict[str, Any]:
    final_story, quality_judge, safety_judge, revision_rounds, blueprint, explanation = run_story_system(user_request, memory_card, story_constraints)
    narration_script = build_narration_script(final_story)
    overall_pass = bool(quality_judge.pass_threshold and safety_judge.pass_threshold)
    return {
        "story": final_story,
        "narration_script": narration_script,
        "score_total": quality_judge.total_score,
        "safety_score_total": safety_judge.total_score,
        "passed": overall_pass,
        "revision_rounds": revision_rounds,
        "planned_age_band": blueprint.get("age_band", ""),
        "strengths": quality_judge.strengths + safety_judge.strengths,
        "improvements": quality_judge.feedback + safety_judge.feedback,
        "explainability": explanation,
    }


def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("Missing OPENAI_API_KEY. Set your API key in environment variables and try again.")
        return

    user_input = input("What kind of story do you want to hear? ")
    final_story, quality_judge, safety_judge, revision_rounds, blueprint, _ = run_story_system(user_input, {}, {})

    print("\n" + "=" * 72)
    print("BEDTIME STORY")
    print("=" * 72 + "\n")
    print(final_story)

    print("\n" + "=" * 72)
    print("QUALITY REPORT")
    print("=" * 72)
    print(f"Quality Score: {quality_judge.total_score}/50")
    print(f"Safety Score: {safety_judge.total_score}/50")
    print(f"Passed Threshold: {'Yes' if (quality_judge.pass_threshold and safety_judge.pass_threshold) else 'No'}")
    print(f"Revision Rounds Used: {revision_rounds}")
    print(f"Planned Age Band: {blueprint.get('age_band', 'unknown')}")

    if quality_judge.strengths or safety_judge.strengths:
        print("\nStrengths:")
        for item in quality_judge.strengths + safety_judge.strengths:
            print(f"- {item}")

    if quality_judge.feedback or safety_judge.feedback:
        print("\nPotential Improvements:")
        for item in quality_judge.feedback + safety_judge.feedback:
            print(f"- {item}")


if __name__ == "__main__":
    main()