---
name: nano-banana-pro
description: "Nano Banana 2 / Gemini 3.1 Flash Image gen/edit: text-to-image, image-to-image, 512/1K/2K/4K, input-image workflows."
---

**Source:** https://github.com/steipete/agent-scripts/tree/main/skills/nano-banana-pro (adopted 2026-05-16)
**적용 대상:** Gemini 3.1 Flash Image (Nano Banana 2) API 호출. 기존 `image-gen` 스킬은 Codex OAuth (OpenAI 이미지). 본 스킬은 Gemini API key 기반 — 다른 백엔드.

# Nano Banana 2 Image Generation & Editing

Generate new images or edit existing ones using Google's Nano Banana 2 API (Gemini 3.1 Flash Image).

## Script path (adapted)

```
~/2lab.ai/skills/nano-banana-pro/scripts/generate_image.py
```

## Usage

Run the script using absolute path (do NOT cd to skill directory first):

**Generate new image:**
```bash
uv run ~/2lab.ai/skills/nano-banana-pro/scripts/generate_image.py --prompt "your image description" --filename "output-name.png" [--resolution 512|1K|2K|4K] [--api-key KEY]
```

**Edit existing image:**
```bash
uv run ~/2lab.ai/skills/nano-banana-pro/scripts/generate_image.py --prompt "editing instructions" --filename "output-name.png" --input-image "path/to/input.png" [--resolution 512|1K|2K|4K] [--api-key KEY]
```

**Important:** Always run from 지혁's current working directory so images are saved where 지혁 is working, not in the skill directory. Default 저장 위치: `ARTIFACTS/images/YYYY-MM/`.

## Default Workflow (draft → iterate → final)

Goal: fast iteration without burning time on 4K until the prompt is correct.

- Draft (1K): quick feedback loop
- Iterate: adjust prompt in small diffs; keep filename new per run
  - If editing: keep the same `--input-image` for every iteration until 지혁 is happy.
- Final (4K): only when prompt is locked

## Resolution Options

The Gemini 3.1 Flash Image API supports these output size values:

- **512** - compact ~512px-class resolution
- **1K** (default) - ~1024px resolution
- **2K** - ~2048px resolution
- **4K** - ~4096px resolution

Map user requests to API parameters:
- "512", "512px", "0.5K", "thumbnail", "tiny" → `512`
- No mention of resolution → `1K`
- "low resolution", "1080", "1080p", "1K" → `1K`
- "2K", "2048", "normal", "medium resolution" → `2K`
- "high resolution", "high-res", "hi-res", "4K", "ultra" → `4K`

## API Key

The script checks for API key in this order:
1. `--api-key` argument (use if 지혁 provided key in chat)
2. `GEMINI_API_KEY` environment variable

If neither is available, the script exits with an error message.

지혁 환경에서는 `.env` 또는 `~/2lab.ai/p9/.env`에 `GEMINI_API_KEY` 둘 것 (이미 있을 수 있음).

## Preflight + Common Failures (fast fixes)

- Preflight:
  - `command -v uv` (must exist)
  - `test -n "$GEMINI_API_KEY"` (or pass `--api-key`)
  - If editing: `test -f "path/to/input.png"`

- Common failures:
  - `Error: No API key provided.` → set `GEMINI_API_KEY` or pass `--api-key`
  - `Error loading input image:` → wrong path / unreadable file; verify `--input-image` points to a real image
  - "quota/permission/403" style API errors → wrong key, no access, or quota exceeded; try a different key/account

## Filename Generation

Generate filenames with the pattern: `yyyy-mm-dd-hh-mm-ss-name.png`

**Format:** `{timestamp}-{descriptive-name}.png`
- Timestamp: Current date/time in format `yyyy-mm-dd-hh-mm-ss` (24-hour format)
- Name: Descriptive lowercase text with hyphens
- Keep the descriptive part concise (1-5 words typically)
- Use context from user's prompt or conversation

Examples:
- Prompt "A serene Japanese garden" → `2026-05-16-14-23-05-japanese-garden.png`
- Prompt "한복 입은 고양이" → `2026-05-16-15-30-12-hanbok-cat.png`

## Image Editing

When 지혁 wants to modify an existing image:
1. Check if 지혁 provides an image path or references an image in the current directory
2. Use `--input-image` parameter with the path to the image
3. The prompt should contain editing instructions
4. Common editing tasks: add/remove elements, change style, adjust colors, blur background, etc.

## Prompt Handling

**For generation:** Pass 지혁's image description as-is to `--prompt`. 한국어 prompt OK — Gemini는 한국어 처리 가능. Only rework if clearly insufficient.

**For editing:** Pass editing instructions in `--prompt` (e.g., "add a rainbow in the sky", "make it look like a watercolor painting")

Preserve 지혁's creative intent in both cases.

## Prompt Templates (high hit-rate)

- Generation template:
  - "Create an image of: <subject>. Style: <style>. Composition: <camera/shot>. Lighting: <lighting>. Background: <background>. Color palette: <palette>. Avoid: <list>."

- Editing template (preserve everything else):
  - "Change ONLY: <single change>. Keep identical: subject, composition/crop, pose, lighting, color palette, background, text, and overall style. Do not add new objects. If text exists, keep it unchanged."

## Output

- Saves PNG to current directory (or specified path if filename includes directory)
- Script outputs the full path to the generated image
- **Do not read the image back** - just inform 지혁 of the saved path
- 텔레그램 전송 필요 시: `mcp__send-file__send_photo` (10MB 이하; 4K PNG은 sometimes >10MB → JPEG 변환 또는 PDF로 send_document).

## When to use this vs existing image-gen

- 기존 `image-gen` 스킬: OpenAI gpt-image-1 (Codex OAuth 사용). 빠르고 quota 공유.
- **본 스킬** (nano-banana-pro): Google Gemini 3.1 Flash Image. 4K 지원, 다른 스타일, 별도 quota.
- 같은 prompt를 양쪽에 돌려 비교하고 싶을 때 유용.
