# port-to-rust — Rust 포팅 실행기 (executor)

`plan-port-to-rust` 가 생성한 `.claude/workflows/port-to-rust/` 디렉토리를 읽고 실제 포팅을 phase 별로 실행한다. **계획 생성 안 한다.** plan 이 없으면 거부.

**Triggers:**
- "rust 포팅 실행", "execute port-to-rust", "execute port plan", "port to rust now"
- 프로젝트 루트에 `.claude/workflows/port-to-rust/` 디렉토리 + 검토된 `02-rulebook.md` 존재
- `state.json` 의 `current_phase` 에서 resume

**기반 패턴**: oven-sh/bun `.claude/workflows/` 의 50+ 워크플로우 micro-loop (Implement → 2-vote Verify → Fix → Re-verify).
분석 원본: `/home/zhugehyuk/2lab.ai/soul/p9/ARTIFACTS/analyses/2026-05-15-bun-claude-workflows-zig-to-rust-port-analysis.md`

---

## 🚨 인코딩 강제 (BOM + NFC)

이 SKILL.md 파일 자체 + 실행 중 생성하는 모든 .md (artifact / log) 는 UTF-8 BOM + NFC. 저장 후 즉시 재포장:
```bash
python3 -c "
import unicodedata, sys
p = sys.argv[1]
with open(p, 'rb') as f: raw = f.read()
if raw.startswith(b'\xef\xbb\xbf'): sys.exit(0)
text = unicodedata.normalize('NFC', raw.decode('utf-8'))
with open(p, 'wb') as f: f.write(b'\xef\xbb\xbf' + text.encode('utf-8'))
" /path/to/file.md
```

---

## Phase 0: Sanity check + plan 로드

호출 시 입력:

```yaml
workflow_dir: ${project_path}/.claude/workflows/port-to-rust   # 필수
phase: A | B | B0 | B1 | B2 | C | D | E | F | G | auto         # 기본 auto (state.json 기반)
shard: 0                                                       # 선택
nshards: 1                                                     # 선택
resume: bool                                                   # 기본 true
dry_run: bool                                                  # 기본 false — true 면 실행 안 하고 plan 만 출력
```

**Pre-flight checks (어떤 것 하나라도 실패 시 즉시 중단):**

1. `${workflow_dir}/00-overview.md` 부터 `09-phase-f-test.md` (또는 그에 준하는 phase 파일) 가 존재.
2. `${workflow_dir}/02-rulebook.md` 첫 줄에 `REVIEWED-BY: <name> <date>` 가 있는지 확인. 없으면 거부:
   ```
   ⚠️ Rulebook not reviewed. plan-port-to-rust 가 만든 초안을 사람이 검토하지 않았다.
   포팅 시작 전 02-rulebook.md 검토 후 첫 줄에 "REVIEWED-BY: <name> 2026-MM-DD" 추가하기.
   ```
3. `${workflow_dir}/state.json` 존재 (없으면 template 으로 초기화).
4. `git status` 깨끗한지 확인. 더러우면 사용자에게 commit/stash 요청.
5. `git rev-parse --abbrev-ref HEAD` 가 main 이면 거부 — 별도 branch (`port-to-rust/${phase}`) 만들도록 요청.

**자동 phase 결정 (`phase: auto`):**
- state.json 의 `current_phase` 확인.
- 그 phase 의 status 가 `pending` 또는 `in_progress` 면 그것부터.
- `completed` 면 다음 phase 로.
- 모든 phase 가 `completed` 면 "🎉 포팅 완료" + 종료.

---

## Phase 1: 워크플로우 spec 파싱

해당 phase 의 `.md` 파일을 읽고 spec 추출.

각 .md 파일은 `plan-port-to-rust` 가 다음 구조로 작성:

```yaml
phase: A | B0 | ...
purpose: <한 줄>
unit: per-file | per-crate | per-symbol | per-test-signature | per-edge
parallelism: <number>
inputs:
  - <required artifact paths>
steps:
  - <step name>:
      label: <agent label>
      schema: <JSON schema>
      prompt: <prompt template>
      mode: implement | verify | fix | adversarial-verify
exit_criteria:
  - <human-readable verification check>
verification:
  - <bash command that should exit 0>
bd_issue:
  title: <title>
  priority: P0
```

이 spec 을 실행기가 generic loop 으로 돌린다.

---

## Phase 2: 실행 루프 (generic micro-loop)

bun 의 모든 workflow 가 공유하는 4-stage micro-loop 의 generic 구현. 각 phase 의 spec 에 따라 stage 가 켜지고 꺼짐.

```
┌─ Survey ─┐
│ items[]  │  ← Per-X (file/crate/edge/...) 작업 단위 리스트업
└────┬─────┘
     ▼
┌─ Implement ─┐
│ parallel    │  ← 각 item 별 agent → structured output
│ per item    │
└──────┬──────┘
       ▼
┌─ Verify ────┐
│ 2-vote      │  ← 두 agent 적대적 verify → intersection (둘 다 flag = agreed)
│ parallel    │     한쪽만 flag = tiebreaker (default reject)
└──────┬──────┘
       ▼
┌─ Fix ───────┐
│ parallel    │  ← agreed bugs 만 fix
│ per item    │
└──────┬──────┘
       ▼
┌─ Verify-2 ──┐
│ optional    │  ← 재검증, 통과 못 하면 사람 요청
└──────┬──────┘
       ▼
   (next phase or repeat round)
```

### Agent dispatch

각 agent 호출은 다음 형식:

```python
result = Agent({
    description: f"port-to-rust {phase} {label}: {item}",
    subagent_type: "general-purpose",
    prompt: <spec.steps[stage].prompt 의 변수 치환>,
})
# 결과는 structured output schema 매칭 강제
```

**HARD RULES (모든 agent prompt 끝에 inject):**
- Edit ONLY 정해진 unit boundary 안의 파일.
- NEVER edit source language files (.zig / .go / ...). Ground truth.
- NEVER run `git reset/checkout/stash/clean/restore`.
- NEVER delete files. NEVER create new files unless spec 허용.
- Commit with explicit paths only: `git add 'src/' && git commit -q -m "..."`. NEVER `git add -A` (heap snapshots / coredumps 휘말림).
- NO push (orchestrator 가 검증 후 push).

### Survey 단계

source language 별 작업 단위 enumerate. 예:

- Phase A (per-file): `find ${project_path} -name '*.${ext}'` → 각 파일 LOC 측정.
- Phase B0 (per-edge): 의존성 그래프에서 cycle 추출.
- Phase C (per-panic-loc): `RUST_BACKTRACE=1 ./target/debug/<bin> <cmds>` 실행 → panic 위치 dedup.
- Phase D (per-frontier-file): `cargo build 2>&1 | grep error | uniq -c` → 에러 가장 많은 파일.
- Phase G (per-test-signature): test suite 실행 → crash signature dedup.

### Implement / Verify / Fix 단계

위 micro-loop 의 핵심. spec 의 `steps[].prompt` 를 변수 치환 후 agent 에 전달. structured output 강제.

**2-vote intersection logic:**
```python
def merge_votes(votes_a, votes_b):
    bugs_a = {(b.fn, b.what[:80]): b for b in votes_a.issues if b.severity != 'nit'}
    bugs_b = {(b.fn, b.what[:80]): b for b in votes_b.issues if b.severity != 'nit'}
    agreed = [bugs_a[k] for k in bugs_a if k in bugs_b]
    disputed_a = [b for k, b in bugs_a.items() if k not in bugs_b]
    disputed_b = [b for k, b in bugs_b.items() if k not in bugs_a]
    return agreed, disputed_a + disputed_b  # disputed 는 tiebreaker

def tiebreak(bug):
    # default reject — verifier prompt 에 "default confirmed=false" 명시
    result = Agent({
        prompt: f"Default reject. Is this bug REAL? {bug}",
        schema: {confirmed: bool, reason: str}
    })
    return result.confirmed
```

### 검증 게이트 (각 phase 종료 시)

spec 의 `verification` 리스트의 모든 bash 명령어가 exit 0 이어야 함.

예시 (Phase A):
```bash
# 모든 source 파일에 대응하는 .rs 파일 존재
test $(find . -name '*.zig' | wc -l) -eq $(find . -name '*.rs' -not -path 'target/*' | wc -l)

# 각 .rs 파일에 PORT STATUS trailer 존재
! find . -name '*.rs' -not -path 'target/*' -exec grep -L 'PORT STATUS' {} +
```

검증 실패 시:
1. `state.json` 의 phase status → `verification_failed`.
2. `ARTIFACTS/port-to-rust/${phase}/<timestamp>-verification-fail.md` 에 실패 명령어 + 출력 저장.
3. bd 이슈에 note append: `bd update ${id} --append-notes "Verification failed at ${phase}: ${cmd}"`.
4. 사용자에게 보고 + 다음 단계 묻기.

---

## Phase 3: State management

`state.json` 을 매 step 마다 업데이트.

```json
{
  "current_phase": "A",
  "phases": {
    "A": {
      "status": "in_progress",
      "started": "2026-05-15T00:30:00Z",
      "items_total": 1247,
      "items_done": 893,
      "items_failed": 12,
      "rounds": 3,
      "by_confidence": {"high": 412, "medium": 387, "low": 94}
    }
  }
}
```

상태 저장은 atomic: tmp file 에 write → rename. concurrent write 방지.

---

## Phase 4: Sharding (선택)

큰 작업은 `args.shard / args.nshards` 로 분할. bun 의 패턴 그대로:

```python
mine = sorted_items[shard::nshards][:max_per_round]
```

여러 메타 에이전트가 같은 워크플로우를 다른 shard 로 동시 실행 가능. 단:
- `index.md` / `state.json` 같은 공유 파일은 lock 또는 retry on conflict.
- Phase F-H 의 worktree 격리 모드에서는 shard 별 worktree 권장.

---

## Phase 5: Worktree isolation (Phase F-H)

bun 의 `phase-f-reviewed-refactor` / `phase-h-windows-*` 패턴 일반화. risky refactor 는 격리.

```bash
WT="/tmp/port-to-rust-wt-${phase}-${shard}-$$"
git worktree add "$WT" "port-to-rust/${phase}"

# agent 가 $WT 에서 작업, 끝나면 patch 반환
cd "$WT"
# ... agent operations ...
git diff > /tmp/patch-${phase}-${shard}.diff
cd -

# 2-vote review (main repo 에서 read-only)
# accept 시 cherry-pick or apply patch
git worktree remove "$WT"
```

---

## Phase 6: bd 통합 (P9 컨텍스트 한정)

```bash
# Phase 시작
BD_ID=$(bd create --title "$(yq '.bd_issue.title' phase-spec.md)" \
                  --type task --priority P0 \
                  --label port-to-rust --label "phase-${PHASE}" \
                  -f json | jq -r .id)
echo "$BD_ID" > "${workflow_dir}/bd-${PHASE}.id"

# Phase 종료 (verification 통과 후)
./scripts/bd-verify "$BD_ID" "$(yq '.verification[0]' phase-spec.md)"
./scripts/bd-close-verified "$BD_ID" "완료: Phase ${PHASE} (${items_done}/${items_total} items)"

# 실패 시
bd update "$BD_ID" --append-notes "Phase ${PHASE} verification failed: ${output}"
# 지혁에게 보고
```

비-P9 컨텍스트면 bd 단계 skip, 대신 git tag (`port-to-rust/${phase}-done`).

---

## Phase 7: 자기개선 호출 (선택)

매 phase 종료 후 또는 사용자 트리거 시 `11-rulebook-audit.md` 의 spec 으로 룰북 audit.

```
audit_rulebook() {
    spec = read 11-rulebook-audit.md
    for dim in spec.dimensions:
        findings = Agent(audit prompt for dim).findings
    # 3-vote refute per finding
    confirmed = [f for f in findings if 3_vote_refute(f).survived]
    if confirmed:
        patch = Agent(synthesize patch prompt).sections
        # 사용자에게 patch 보고, 적용 여부 묻기
}
```

룰북 변경은 항상 사용자 승인 필요.

---

## Phase 8: 실패 / 롤백

각 phase 별 commit 단위 보존. 실패 시:

1. **Soft fail** (verification fail, agent confusion): state.json 의 status → `needs_human`. bd 에 note. 사용자 요청.
2. **Hard fail** (UB introduced, semantic broken): 마지막 known-good commit 으로 `git revert` 권장 (사용자 승인 후).
3. **Rollback never automatic.** 사람이 결정.

```yaml
on_failure:
  - save state.json with status="failed"
  - write ARTIFACTS/port-to-rust/${phase}/<ts>-failure.md (logs, errors, last 100 agent outputs)
  - bd update --append-notes
  - 사용자에게 보고 + 다음 행동 묻기
  - NEVER auto-rollback
  - NEVER auto-retry > max_rounds (spec 정의)
```

---

## Phase 9: 보고 (사용자에게)

각 phase 시작 / 진행 / 종료마다:

```
🚀 Phase ${X} 시작: ${purpose}
   ├─ Unit: ${unit}
   ├─ Items: ${total}
   ├─ Parallelism: ${concurrent_agents}
   └─ Shard: ${shard}/${nshards}

⏳ Progress: ${done}/${total} (${pct}%)
   ├─ ✅ ${clean} clean
   ├─ 🔧 ${fixed} fixed (verifier found bugs)
   ├─ ⚠️  ${low_confidence} low confidence
   └─ ❌ ${failed} failed

✅ Phase ${X} 완료
   ├─ Verification: PASS (${cmd})
   ├─ bd: closed (${id})
   ├─ Next: Phase ${Y} 권장
   └─ Artifacts: ${workflow_dir}/${phase}-results.json
```

장기 실행 phase 는 매 N개 item 마다 short progress 텔레그램 (선택).

---

## HARD RULES (모든 agent / loop / step)

1. **Source 언어 파일은 절대 편집 금지.** `.zig` / `.go` / `.ts` 등 = ground truth.
2. **Plan 이 없으면 거부.** plan-port-to-rust 먼저.
3. **Rulebook 미검토 시 거부.** REVIEWED-BY 사인 필수.
4. **Main branch 에서 직접 실행 금지.** 별도 branch.
5. **Worktree 격리 모드 (F+) 에서는 main repo write 금지.** patch 만 반환.
6. **HARD-CAP rounds** spec 정의 따름. 무한 루프 방지.
7. **2-vote intersection + tiebreak**, single-vote 로 fix 절대 적용 금지.
8. **Default reject** verifier prompt 에 명시.
9. **Structured output schema 강제.** 자유 텍스트 결과 금지.
10. **state.json atomic write.**

---

## bd 통합 (P9 only)

```bash
# 실행 시작
bd create --title "port-to-rust: ${project} phase ${X}" --priority P0 --label port-to-rust

# verification 통과 후
./scripts/bd-verify <id> '<phase-specific check>'
./scripts/bd-close-verified <id> "Phase ${X} 완료 (${items_done}/${total})"

# 실패 시
bd update <id> --append-notes "Phase ${X} failed at item ${N}: ${reason}"
# 절대 close 금지, 지혁에게 보고
```

---

## 차이점 정리 (plan-port-to-rust vs port-to-rust)

| | plan-port-to-rust | port-to-rust |
|---|---|---|
| **목적** | 계획 수립 | 실행 |
| **코드 수정** | ❌ 절대 | ✅ phase 별 |
| **소스 언어 파일** | read | read only (수정 금지) |
| **target rust 파일** | 생성 안 함 | 생성 / 수정 |
| **agent 호출** | 분석용 (discovery, classify) | 작업용 (port, fix, verify) |
| **비용** | 저렴, deterministic | 비싼, parallel |
| **사람 sign-off** | 출력 후 검토 요청 | 시작 전 검토 확인 |
| **반복성** | 1회 (또는 audit 시 재호출) | phase 단위 반복 |

---

## 예시 호출

```
# Phase A 만 실행 (per-file draft)
port-to-rust --workflow-dir /path/to/proj/.claude/workflows/port-to-rust --phase A

# auto resume (state.json 기반)
port-to-rust --workflow-dir /path/to/proj/.claude/workflows/port-to-rust --phase auto

# shard 0/4 of Phase D
port-to-rust --workflow-dir ... --phase D --shard 0 --nshards 4

# dry run (실행 안 하고 plan 만 출력)
port-to-rust --workflow-dir ... --phase B --dry-run
```

---

## 참조

- 원본 패턴: bun `.claude/workflows/` @ SHA 23427dbc12fdcff30c23a96a3d6a66d62fdc091d
- 분석 문서: `/home/zhugehyuk/2lab.ai/soul/p9/ARTIFACTS/analyses/2026-05-15-bun-claude-workflows-zig-to-rust-port-analysis.md`
- 계획 스킬: `~/2lab.ai/skills/plan-port-to-rust/SKILL.md`
- bd verification 워크플로우: `~/2lab.ai/soul/p9/scripts/bd-verify`, `bd-close-verified`
- Karpathy plan-then-execute: plan 단계의 deterministic 산출물에 execute 단계가 의존.

---

**한 줄 요약: plan 디렉토리 받아서 phase A→G 를 (Implement → 2-vote Verify → Fix → Re-verify) micro-loop 으로 실행. 사람 sign-off, worktree 격리, bd 통합 강제.**
