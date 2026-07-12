---
name: release-tweets
description: Draft, validate, copy, or post concise X/Twitter or Threads release announcements from changelogs, tags, release notes, npm/appcast state, and shipped artifacts.
---

**Source:** https://github.com/steipete/agent-scripts/tree/main/skills/release-tweets (adopted 2026-05-16)
**적용 대상:** soma/p9 릴리즈 트윗, 블로그 shortform 헤드라인, 텔레그램 알림 카피. Peter의 X 계정 인프라(bird/xurl) 의존성 제거. 카피라이팅 룰만 유지. 한국어 출력 허용.

# Release Tweets

Use when 지혁 asks for a release tweet, launch tweet, X/Threads announcement, release thread, changelog-to-tweet rewrite, or social copy for a shipped version. This skill is about release copy, not cutting the release.

## Ground The Copy

- Verify the release target before writing confident copy:
  - read the relevant `CHANGELOG.md` section or GitHub release notes
  - check the tag/release/npm/appcast/artifact state that applies to the project
  - distinguish `Unreleased`, beta/prerelease, stable, hotfix, and correction releases
- Do not say a feature shipped only because it is in the top changelog block. Confirm the tag/release/package evidence when available.
- Lead with user-visible wins: features, integrations, workflow improvements, install/update reliability, security fixes.
- Avoid leading with CI, coverage, validation, refactors, internal migrations, or release mechanics unless that is the actual story.
- If evidence is incomplete, say what is unverified and draft with softer wording.

## Launch Tweet Shape

- One standard tweet under 280 characters (X/Twitter) or 500 자 (Threads).
- 한국어 트윗: 한글 280자 한도 (X는 한글은 1자=2바이트 카운트 아니라 1자=1자임).
- Typical format:
  - product + version
  - blank line
  - 3-4 compact emoji-led feature bullets
  - blank line
  - one short punchline
  - release/changelog URL
- Use emoji bullets by default for launch tweets. Pick clear, low-noise emoji that match the feature or product; skip only when the user asks for plain text or the release is incident-style.
- Tone: high-signal, compact, confident, a little dry when earned. Not corporate.
- One joke max. Let the feature bullets do the work.
- Put the release/changelog URL at the end.
- Count final raw characters before presenting it as ready to post.

## Beta, Hotfix, Correction

- Beta/prerelease:
  - make beta status explicit
  - avoid implying stable promotion
  - phrase as "beta N", `VERSION-beta.N`, or "preview" as appropriate
- Hotfix/correction:
  - be direct and accountable
  - state what slipped, what is fixed, and the new version
  - skip jokes unless the user asks for a lighter tone

## Threads (X/Twitter thread sense, not Meta Threads)

- First agree on the generic launch tweet.
- Then write follow-ups one at a time. When 지혁 says `next`, provide only the next reply.
- Each follow-up should focus on one feature or user workflow.
- Include a docs/release URL for the specific feature when available.
- Avoid repeating the version in every reply when the thread context already has it.
- Good follow-up length: 160-220 raw characters. Hard cap: 280.

## Posting And Clipboard

- **Draft by default. Do not post unless 지혁 explicitly asks.**
- 카피 결과를 텔레그램으로 전달: `mcp__send-file__send_document` 또는 직접 텍스트로 답.
- Never invent media. If 지혁 wants media, use an existing release screenshot/asset or generate one via `image-gen` / `nano-banana-pro` separately.

## Quality Pass

Before final:

- Character count under 280 for each tweet (영어) / 500 (Threads).
- Exact version string and channel.
- Release URL included when requested or expected.
- No unverified claims.
- No more than 3-4 emoji-led bullets in the launch tweet.
- 지혁 style: 간결, 직설, 광고 톤 회피.

## Examples

```text
soma v0.4.2 released

🧠 Memory restoration on restart fixed
⚡ Codex MCP latency -40%
🔧 bd-verify enforcement
🐛 Context crash at 62% (soma-u63c) closed

Brittle beta, finally less brittle.
https://github.com/icedac/soma/releases/tag/v0.4.2
```

```text
p9 daily memory update — 2026-05-16

📝 ZETTEL/000_index refreshed
🛠️ cron.yaml: link-summary every 30min
🧹 67 stale bd issues cleared (last spring)

Cleaner queue, faster wake.
```

```text
릴리즈 깨졌습니다. v0.4.2-beta.1

v0.4.2-beta.2에서 install/update 검증 수정. 태그 재작성 없음, 베타는 그대로 전진.
```
