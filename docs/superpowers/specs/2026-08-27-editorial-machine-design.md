# Editorial Machine Landing System Design

**Date:** 2026-08-27
**Status:** Approved by `/goal` execution mandate

## User contract

| User clause | Acceptance proof |
|---|---|
| “다음의 사이트들을 철저하게 분석” | `editorial-machine/references/source-analysis.md` covers every site listed by the post author: char.com, anarlog.so, fastrepl.com, agentpub.dev, johnjeong.com; each observation is labeled observed or inferred. |
| “해당 스타일로 랜딩 페이지 만들어주는 스킬” | `editorial-machine/SKILL.md` defines inputs, evidence extraction, composition, implementation, and browser QA. |
| “2lab-ai/skills 레포에 적절히 추가” | Skill is a self-contained top-level directory in this repository and is added to `README.md`. |
| “이름도 니가 지어주고” | Name: `editorial-machine` — editorial storytelling wrapped around working product evidence. |
| “이 스킬을 이용해서 … 2lab.ai 랑 zhugehyuk.com에 어울리는 페이지” | Two self-contained responsive pages in `editorial-machine/examples/`, sharing the method but not a cloned template. |
| “llmux 소개 페이지 xfx 소개 페이지 등” | `llmux.html` and `xfx.html`, with claims grounded in each project's README. |

## Source boundary

The Threads author explicitly labeled five sites as “제가 만든 것들 예시”: `char.com`, `anarlog.so`, `fastrepl.com`, `agentpub.dev`, and `johnjeong.com`. Other links are commenters’ submissions for critique, not examples of the requested author style, so they are catalogued but excluded from the style synthesis.

## What the style actually is

The shared system is not one palette or one template. It is a composition grammar:

1. **Editorial thesis before feature inventory.** Lead with a belief or tension, then show the product as the resolution.
2. **Serif-led character, utility-led evidence.** Distinctive serif/display type carries the narrative; mono/system type carries commands, receipts, and interface evidence.
3. **Warm neutral canvas with one rationed signal color.** Paper-like backgrounds, near-black copy, low-chroma borders, one product-specific accent.
4. **One long reading path.** Generous vertical rhythm, narrow prose measures, occasional full-width product “proof objects.”
5. **Concrete transformation.** Before/after, input/output, or fragmented/unified states prove the promise.
6. **Human irregularity.** Handwritten accents, stamps, marginal notes, or gentle rotation appear sparingly; they never replace hierarchy.
7. **Motion as explanation.** Short reveal, state transformation, or horizontal evidence movement; no ambient animation without meaning.
8. **Founder-level candor.** Explicit limitations and boundaries increase credibility.

## Skill architecture

`editorial-machine` has five independent units:

- `SKILL.md`: runtime workflow and decision rules.
- `references/source-analysis.md`: evidence ledger and common/variable pattern synthesis.
- `references/composition-system.md`: reusable tokens, section grammar, copy model, responsive and motion rules.
- `scripts/validate.py`: deterministic structural/accessibility checks for generated HTML.
- `examples/`: two complete pages and their page briefs.

The skill consumes a product brief plus verified source facts. It outputs a standalone HTML page, browser receipts, and a validation result. It does not copy source assets or layout byte-for-byte.

## Page concepts

### llmux — “The harness is capital”

A dark ink-on-warm-paper editorial page. Its proof object is a routing ledger: one Claude Code request, several model lanes, one unchanged harness. The page moves from the instability of model supply to the durable harness bet, then shows routing, request receipts, remote topology, installation, and compliance boundaries. Accent: routing red.

### xfx — “Small enough to audit”

A more austere field-manual page. Its proof object is the explicit capability boundary: eight tools, six commands, one provider in v0.1, with absences named rather than hidden. It moves from “a terminal agent you can account for” through the bounded loop, permission modes, append-only sessions, llmux backend, install commands, and honest non-goals. Accent: safety green.

They share composition grammar and brand footer, but use different hierarchy, accent, proof object, and cadence. This demonstrates a skill rather than a fixed template.

## Quality contract

- Standalone HTML/CSS/JS; no framework or build step.
- No externally hosted images; visual proof objects are CSS/HTML/SVG authored for the page.
- Google Fonts may be linked, with real local fallback stacks.
- Semantic landmarks and ordered heading hierarchy.
- Keyboard-visible focus states and minimum 44px primary interaction targets.
- Full readability at 390×844 and 1440×1000 with no body horizontal scroll.
- `prefers-reduced-motion` disables non-essential animation.
- Text contrast meets WCAG AA; accent is never the only status signal.
- Every factual product claim maps to the corresponding README evidence in the page brief.
- Validator rejects missing title, description, main, h1, install snippet, reduced-motion handling, skip link, or horizontal-overflow guards.
