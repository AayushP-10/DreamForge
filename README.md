# DreamForge - Bedtime Story Intelligence Studio

An agentic bedtime story system for ages 5-10 that does more than generate text:
it plans, self-critiques, safety-checks, rewrites, personalizes across nights, and explains why the final story is trustworthy.

---

## Why This Submission Is Different

Most story demos are one-shot generation.
DreamForge is a **quality-and-safety controlled storytelling pipeline**:

- Detects bedtime emotional state from the user request (anxious, neutral, energized, already sleepy)
- Plans a structured blueprint before writing
- Generates multiple draft candidates (self-play)
- Uses **dual judges** (Quality Judge + Pediatric Safety Judge)
- Selects best candidate and rewrites when needed
- Applies final rhythm polish for read-aloud bedtime flow
- Persists per-user memory to improve continuity over time
- Surfaces explainability in UI ("Why This Story")
- Generates narration scripts with pacing markers for read-aloud delivery
- Supports parent controls for reading level and topic boundaries
- Supports automatic multi-night bedtime sequence mode
- Includes in-browser audio narration with selectable voice options
- Surprise suggestions are personalized from each user's history and themes

---

## Assignment Requirement Coverage

### 1) "Tell a story appropriate for ages 5 to 10"
**Satisfied.**

- Age band guidance is built into planner and generation prompts (`5-7` / `8-10`)
- Bedtime calming constraints are enforced at generation + revision steps
- Final polishing pass ensures gentle read-aloud cadence

### 2) "Incorporate a LLM judge to improve quality"
**Satisfied (and extended).**

- Quality Judge evaluates coherence, creativity, age fit, personalization, and calmness
- Pediatric Safety Judge evaluates emotional safety and sleep disruption risk
- Rewrite loop applies judge feedback up to threshold

### 3) "Provide a block diagram"
**Satisfied.**

- See `BLOCK_DIAGRAM.md` (includes user, planner, storyteller candidates, dual judges, selector, rewrite, memory, output)

### 4) "Do not change the OpenAI model being used"
**Satisfied.**

- Model remains fixed to `gpt-3.5-turbo`

### 5) "Use your own API key and do not include it"
**Satisfied.**

- Uses `OPENAI_API_KEY` environment variable only
- No key is stored in source files

---

## System Architecture (High-Level)

1. User submits bedtime prompt
2. Bedtime state detector infers emotional context
3. Planner creates story blueprint
4. Two draft candidates are generated (self-play)
5. Both drafts are scored by:
   - Quality Judge
   - Safety Judge
6. Best candidate is selected by combined score
7. If needed, rewrite loop runs with judge feedback
8. Final rhythm polish is applied
9. Story + telemetry are returned and persisted to user history/memory

---

## Product Features Implemented

- **Workshop:** story generation interface
- **Library:** per-user story history
- **Gallery:** card view of recent stories
- **Performance:** total stories, average score, pass rate, recent runs
- **Account:** sign up/sign in flow for user-specific persistence
- **Explainability panel:** shows bedtime state, candidate count, selection reason, quality/safety signals
- **Narration mode:** produces read-aloud script with pacing markers (`[PAUSE_SHORT]`, `[PAUSE_MEDIUM]`, `[PAUSE_LONG]`, `[SOFTEN]`)
- **Audio narrator:** play/stop narration with 3-4 browser voice options
- **Parent controls:** reading level selector + "avoid topics" safety boundary field
- **Bedtime sequence mode:** optional continuation mode that carries story context across nights
- **Personalized surprise:** prompt suggestions are generated from user story history/memory

---

## Tech Stack

- Backend: Python + Flask
- LLM: OpenAI Chat Completions (`gpt-3.5-turbo`)
- Persistence: SQLite (`users`, `stories`, `user_memory`)
- Frontend: HTML + Tailwind + vanilla JS

---

## Run Instructions

### 1) Install dependencies
```bash
pip install -r requirements.txt
```

### 2) Set API key
PowerShell:
```powershell
$env:OPENAI_API_KEY="your_key_here"
```

### 3) Start server
```bash
python app.py
```

### 4) Open app
`http://127.0.0.1:8000`

---

## Notes for Evaluators

- Database is auto-created at first run (`dreamforge.db`), no manual setup needed.
- To test personalized continuity:
  1. Create account
  2. Generate several stories
  3. Review Library + Performance
  4. Enable bedtime sequence mode and generate another story
  5. Inspect "Why This Story" + Narration Script + continuity behavior