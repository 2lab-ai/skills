---
name: github-deep-review
description: "GitHub deep review: bugs, PRs, best fix, stale-or-real, read-code-first."
---

**Source:** https://github.com/steipete/agent-scripts/tree/main/skills/github-deep-review (adopted 2026-05-16)
**적용 대상:** soma / p9 PR 리뷰, issue triage, 버그 root cause 분석. Peter의 maintainer/contributor 노트 컨텍스트는 제거. 일반 root-cause + fix-quality 방법론만 유지.

# GitHub Deep Review

Review with high confidence, evidence-first, code-aware, and willing to say "not proven" when the trail is weak. The goal is not a generic summary. The goal is to understand the bug class, find the real cause if possible, decide the best fix after reading enough code, and call out whether a larger refactor would improve the design.

## Start

Use `gh`, not web browsing, for GitHub refs:

```bash
gh issue view <n> --json number,title,state,author,body,comments,labels,updatedAt,url
gh pr view <n> --json number,title,state,author,body,comments,reviews,files,commits,statusCheckRollup,mergeStateStatus,headRefName,headRepositoryOwner,url
gh pr diff <n> --patch
```

For repo-local review, also inspect:

```bash
git status --short --branch
git fetch origin
git log --oneline --decorate -20
```

Use Grep tool (ripgrep) to search:

```
<key symbol/error/config/endpoint>
```

If the repo has local instructions (CLAUDE.md, AGENTS.md, etc.), issue/PR skills, docs lists, test guidance, or maintainer runbooks, read those before deciding.

## Review Contract

Always answer these, explicitly:

- URL/ref: issue or PR number and affected surface.
- What is the bug or behavior being fixed?
- Can we identify the root cause? If yes, where in code and why. If no, what evidence is missing.
- For regressions, who/what introduced it and when? Include commit/PR provenance when traceable by bounded history; say unknown instead of guessing.
- Is the current/proposed fix the best possible fix after reading adjacent code?
- Would a bigger refactor improve correctness, clarity, or future maintainability?
- What proof exists: tests, live repro, CI checks, docs, dependency docs/source, shipped/current behavior.
- What remains risky or unverified.

## Code Reading Depth

Read past the first touched file. Follow the real call path:

- entrypoint -> validation/parsing -> routing/dispatch -> owner module -> shared helper -> persistence/network/runtime boundary
- config/schema/docs -> runtime usage -> doctor/migration/fix path
- provider/channel/plugin owner code -> generic core seam, only if multiple owners need it
- tests around the touched surface plus adjacent regression tests

When behavior depends on a dependency, read the upstream docs/source/types or current package contract before assuming.

Prefer current source and executable proof over issue comments. Treat stale comments, old CI, and old release behavior as hints until rechecked.

## Provenance

For bug/regression reviews, include a compact `Provenance:` answer when feasible:

- Use `git log -S/-G`, `git blame`, linked PRs/issues, and tests.
- Separate author, committer/merger, and current PR author when they differ.
- Phrase as `introduced by`, `made visible by`, or `carried forward by`.
- Include confidence: `clear`, `likely`, or `unknown`.
- For features, docs, refactors, or untraceable bugs, write `N/A` or say what evidence is missing.

## Fix Quality Bar

Good fixes usually:

- live at the ownership boundary where the bug belongs
- preserve public/backward-compatible behavior unless the issue is about retiring it
- add a regression test at the smallest meaningful seam
- avoid broad special cases, hidden migrations, semantic sentinels, and provider/channel IDs in generic core
- update docs/changelog when user-visible behavior changes
- fail clearly in runtime paths and repair through doctor/migration paths when that is the established contract

Call out when a fix is only symptom-level. If a slightly larger refactor makes the invariant obvious and reduces future bugs, recommend it. If the refactor widens risk without improving the bug class, say so.

## PR Review Shape

Lead with findings when reviewing a PR. Findings need file/line/symbol references and a concrete failure mode. Avoid vague "consider" comments.

If no blocking issues:

- say no blocking correctness issues found
- list the strongest proof checked
- name residual risk/test gaps
- answer whether the design is the best available shape

Do not approve, comment, close, merge, push, or land unless the user asked for that action.

## Issue Review Shape

For bugs/issues:

1. Reconstruct the reporter's scenario and affected version/surface.
2. Check whether current `main` already fixes it.
3. Reproduce or create a minimal local/live proof when feasible.
4. If clear, identify root cause and proposed fix.
5. If solved on `main`, only comment/close when the user asks; include proof and the canonical commit/PR if known.

If reproduction is not feasible, say exactly what blocks it and what evidence would make the decision reliable.

## Output Template

Use this shape when 지혁 asks "what is this about", "is this the best fix", or "what did we fix":

```text
Ref: #123 / PR #456
Surface: <runtime/CLI/provider/channel/docs>

Bug: <one or two sentences>
Cause: <code path + confidence>
Provenance: <introduced/made visible/carried forward by commit/PR/date, or N/A/unknown>
Best fix: <what should change and why>
Refactor: <yes/no, specific shape>
Proof: <tests/live/CI/source/dependency docs>
Risk: <remaining uncertainty>
```

Keep it concise, but do not skip the cause/fix/refactor/proof decision.

## Tool / Project Adoption Review (쓸만한가?)

PR/버그가 아니라 **"이 레포/도구를 쓸지"** 판단할 때. 위 root-cause 방법론과 별개 모드.

세 질문에 답한다 (순서대로):
1. **메커니즘이 실제로 뭘 하나?** README 주장을 코드로 환원한 *동작*. (안티패턴 2 참조)
2. **이게 *우리* 문제를 푸나?** 일반 좋음이 아니라 지혁/soma/p9의 *구체적 미해결 문제*와의 적합성. 적합 없으면 "흥미롭지만 우리엔 무관"이 정답.
3. **리스크와 저위험 검증 경로.** 채택 전 *우리 워크로드로* 재볼 수 있는 최소 실험(holdout/dry-run/벤치 재현).

### Anti-patterns (검증된 실패 — 2026-06-20 지혁 교정)

**AP1. 대리지표(vanity metric)를 품질로 착각 금지.**
- ❌ "테스트 619개 → 진지한 프로젝트", "10K stars → 좋음", "커밋 많음/CI 초록/codecov 배지 → 신뢰".
- 이유: 테스트 수·LOC·⭐·커밋·트렌딩·배지는 **AI가 다 양산하는 시대에 품질과 무상관**. 테스트 30만 개여도 검증력 0일 수 있다. 양은 신호가 아니다.
- ✅ 대신: 주장의 **핵심 모듈 1~3개를 직접 읽고** 구현 깊이·정직성·엣지케이스 처리를 판단. 평가는 *읽은 코드*에 근거. 숫자 세지 말고 코드를 봐라.

**AP2. 마케팅 용어를 메커니즘으로 환원하라 (그대로 옮기지 마라).**
- ❌ README의 "X compression", "Nx faster", "output token reduction", "AI-powered", "60–95% fewer" 를 *그 표현 그대로* 리뷰에 전달.
- ✅ 절차: (a) **물리적으로 말이 되나 먼저 의심** — 예: "API 출력을 사후 압축"은 불가능(응답 받으면 이미 토큰 청구됨). 말 안 되면 README가 뭔가 다른 걸 그 이름으로 부르는 것. (b) **코드를 까서 실제 동작으로 환원** — 예: headroom "output reduction"의 실체 = `output_shaper.py`가 *프롬프트 끝에 terse 문구 추가 + reasoning effort 사전 하향* = "사후 압축"이 아니라 "사전 프롬프트 조작으로 출력 길이 억제". (c) 환원 못 하면 **"검증 안 됨 — 주장일 뿐"** 명시.

**AP3. 벤치마크는 자체측정·cherry-pick으로 가정.**
- 숫자가 자체 벤치(N 작음)이거나 유리한 workload만 고른 건 아닌지. holdout/독립재현/counterfactual 여부 확인. README가 "estimate"라 자인하면 그대로 estimate로 전달.

### Adoption 출력 템플릿
```text
도구: <name> — <한 줄 실체(메커니즘 환원형, 마케팅 용어 X)>
실체 메커니즘: <코드로 까본 실제 동작>
우리 적합성: <지혁/soma/p9 구체 문제와 매칭, 또는 "무관">
리스크: <정보손실/복잡도/의존성/레이턴시/pre-1.0 등>
검증 경로: <채택 전 우리 워크로드로 잴 최소 실험>
판정: 쓸만/조건부/패스 + 근거(읽은 코드, 대리지표 아님)
```

## p9/soma 적용 노트

- p9 issue: `bd list` → `bd show <id>` → 위 템플릿으로 답.
- soma 코드 변경 검토: `cd ~/2lab.ai/soma && git diff` + 위 워크플로우.
- "고친다"고 말하기 전에 `./scripts/bd-verify`로 증명 후 `bd-close-verified`.
