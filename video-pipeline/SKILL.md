---
name: video-pipeline
description: "End-to-end video production: design system → TTS → scene verification → final render. Uses ui-ux-pro-max for design, Fish-TTS for voice, video-gen (Remotion) for rendering. Actions: make video, create video, 영상 만들어, 샘플 영상, video sample. Always verify scenes before final render."
---
# Video Pipeline — Design → Voice → Verify → Render

Full video production pipeline integrating 3 skills with a mandatory verification phase.

## When to Use

When user requests video creation, sample videos, or "영상 만들어줘":
- Product demos, explainers, social content
- AI/tech concept visualizations
- Personal brand content
- Any YAML-scripted video

## Pipeline Overview

```
Phase 1: UI/UX Pro Max → Design System (style, colors, fonts)
Phase 2: YAML Script → Fish-TTS Audio + Scene Config
Phase 3: Scene Verification → Render stills, review each scene ⚠️ MANDATORY
Phase 4: Final Render → Only after verification approval
```

## Dependencies

| Skill | Location | Purpose |
|-------|----------|---------|
| ui-ux-pro-max | `~/.claude/skills/ui-ux-pro-max/` | Design system generation |
| fish-audio | `~/2lab.ai/skills/fish-audio/` | Voice reference files |
| video-gen | `~/2lab.ai/skills/video-gen/` | Remotion-based video rendering |

## Step-by-Step Workflow

### Phase 1: Design System

Generate a design system using UI/UX Pro Max based on the video's topic:

```bash
python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py \
  "<topic keywords>" --design-system -p "<Project Name>"
```

**Output gives you:**
- Recommended style (Cyberpunk, Minimal, etc.)
- Color palette (primary, secondary, CTA, bg, text)
- Typography pairing (heading + body fonts)
- Key effects (neon glow, glassmorphism, etc.)

**Map to video-gen theme:** Match the recommended style to the closest video-gen theme:

| UI/UX Pro Style | video-gen Theme |
|----------------|-----------------|
| Cyberpunk UI | `neon` |
| Dark Mode OLED | `default` or `bigbrain` |
| Minimalism | `minimal` |
| Glassmorphism | `default` |
| Retro-Futurism | `evangelion` |
| Warm/Organic | `warm` |
| Nature | `nature` |
| Elegant/Serif | `cinematic` or `manuscript` |
| Notion-style | `notion` |

### Phase 2: Write YAML Script + Generate TTS

Write a YAML script file. See `~/2lab.ai/skills/video-gen/SKILL.md` for full scene types.

**Available voices:** elon, iu, karina, egirl (in `~/2lab.ai/fish-tts/voices/`)

**Available scenes:** hero, list, grid, code, flow, chat, stat, quote, timeline, comparison, emoji, image, bigtext, terminal, tokenPredict, matrixRain, progressBar, radar, countdown, map, callout, splitScreen, typewriter, pyramid, reveal, infographic, trainingData, systemPrompt, conversation

**Run Phase 1+2 together:**

```bash
bash ~/2lab.ai/skills/video-pipeline/scripts/pipeline.sh <script.yaml> <output.mp4>
```

This stops after Phase 3 (verification) and waits for approval.

### Phase 3: Scene Verification ⚠️ CRITICAL

**This phase is MANDATORY. Never skip.**

After TTS + metadata generation, render each scene as a still PNG:

```bash
bash ~/2lab.ai/skills/video-pipeline/scripts/verify-scenes.sh <workspace_dir> /tmp/scene-verify
```

**Verification workflow:**
1. Script renders PNG for each scene's midpoint frame
2. Images saved to `/tmp/scene-verify/scene-001.png`, `scene-002.png`, etc.
3. **Read each PNG with the Read tool** to visually inspect
4. Check for:
   - Text readability (not cut off, correct content)
   - Color/contrast issues
   - Layout problems (overlapping elements)
   - Theme consistency
   - Data display correctness (stats, lists, code)
5. If issues found → modify `video-config.json` in workspace and re-verify
6. If all scenes pass → proceed to Phase 4

**Sending stills to user:**
- Use `mcp__send-file__send_photo` to send each scene PNG to user
- User can approve or request changes per scene

### Phase 4: Final Render

Only after all scenes are verified:

```bash
WORKSPACE=<workspace_dir> bash ~/2lab.ai/skills/video-pipeline/scripts/render-final.sh <output.mp4>
```

Or if using the pipeline script with verification skipped:

```bash
SKIP_VERIFY=1 bash ~/2lab.ai/skills/video-pipeline/scripts/pipeline.sh <script.yaml> <output.mp4>
```

## Quick Reference: One-Shot (No Verification)

For rapid prototyping when verification isn't needed:

```bash
bash ~/2lab.ai/skills/video-gen/scripts/build-from-script.sh <script.yaml> <output.mp4>
```

## Quick Reference: Full Pipeline (Recommended)

```bash
# 1. Design system
python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py "AI tech dark" --design-system -p "My Project"

# 2. Write YAML (use design system recommendations)
# 3. Run pipeline (stops at verification)
bash ~/2lab.ai/skills/video-pipeline/scripts/pipeline.sh script.yaml output.mp4

# 4. Review stills
# Read /tmp/scene-verify/scene-001.png ... scene-N.png

# 5. Final render (after approval)
WORKSPACE=/tmp/video-pipeline-xxx bash ~/2lab.ai/skills/video-pipeline/scripts/render-final.sh output.mp4
```

## Content Tips

- **Don't be generic** — Use real quotes, real data, real stories
- **Vary scene types** — Don't repeat the same scene type twice in a row
- **Terminal scenes** — Great for "hacker" feel, real commands
- **Code scenes** — Show actual algorithms, not pseudocode
- **Stat scenes** — Use real numbers with units
- **Quote scenes** — Real quotes hit harder than fabricated ones
- **Flow/Timeline** — Good for processes, history, concept progressions

## File Structure

```
~/2lab.ai/skills/video-pipeline/
├── SKILL.md                    # This file
└── scripts/
    ├── pipeline.sh             # Full 4-phase pipeline orchestrator
    ├── verify-scenes.sh        # Phase 3: render stills per scene
    └── render-final.sh         # Phase 4: final render after approval
```
