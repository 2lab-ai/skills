# plan-port-to-rust — Rust 포팅 계획 생성기 (planner)

임의의 source language (zig/go/c/c++/typescript/python/...) 프로젝트를 분석해서 Rust 포팅 워크플로우 디렉토리를 생성한다. **실제 포팅은 안 한다.** 계획만 만든다. 실행은 `port-to-rust` 스킬이 한다.

**Triggers:**
- "rust 로 포팅 계획", "plan port to rust", "porting plan", "<lang> to rust 계획"
- 프로젝트 루트에 `.claude/workflows/port-to-rust/` 가 없는데 사용자가 "rust 포팅 시작"이라고 함
- source 언어 자동 감지 (file 확장자 비율 > 60%)

**기반 패턴**: oven-sh/bun `.claude/workflows/` (SHA `23427dbc...`) 의 52개 워크플로우에서 추출한 일반화 가능한 phase ladder.
분석 원본: `/home/zhugehyuk/2lab.ai/soul/p9/ARTIFACTS/analyses/2026-05-15-bun-claude-workflows-zig-to-rust-port-analysis.md`

---

## 🚨 인코딩 강제 (BOM + NFC)

모든 출력 .md 파일은 UTF-8 BOM (`EF BB BF`) + NFC 정규화 적용. 위반 시 한글 깨짐.

저장 후 즉시 재포장:
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

검증: `head -c 3 file.md | xxd` → `efbb bf` 보여야 통과.

---

## Phase 0: 입력 수신 + sanity check

지혁 / 사용자가 호출 시 받는 입력:

```yaml
project_path: /absolute/path/to/project   # 필수
source_lang: zig | go | c | cpp | typescript | python | swift | ...
                                          # 선택, 미지정 시 자동 감지
target_lang: rust                         # 고정 (default), 변경 가능
options:
  depth: shallow | full                   # shallow=A-C만, full=A-H
  mode: incremental | bigbang             # 모듈별 점진 vs 한 번에
  has_ffi: bool                           # 자동 감지 가능
  has_async: bool                         # 자동 감지 가능
  test_framework: jest | go test | pytest | cargo | ...
  build_system: cargo | npm | make | gradle | ...
  parallelism: number                     # 동시 agent 수 (기본 32)
```

`project_path` 없으면 즉시 중단 + 사용자에게 물어본다. 절대 추측 금지.

**자동 감지 워크플로우:**
1. `find $PROJECT -type f \( -name "*.zig" -o -name "*.go" -o -name "*.ts" -o -name "*.py" -o -name "*.c" -o -name "*.cpp" -o -name "*.swift" \) | head -5000` → 확장자 빈도 카운트.
2. 가장 많은 확장자 = source_lang. 50% 미만이면 사용자에게 명시 요청.
3. `find $PROJECT -name "Cargo.toml"` / `go.mod` / `package.json` / `Makefile` 등 → build_system 추론.

---

## Phase 1: Discovery (산출물: `01-discovery.md`)

프로젝트 전체 스캔. **읽기만 하고 수정 금지.**

수집할 정보:

```yaml
size:
  total_loc: <number>
  file_count: <number>
  by_dir: {src/: N, lib/: N, ...}
  largest_files: [{path, loc}, ...]   # top 20
modules:
  count: <number>
  graph: <dot file path or summary>   # 의존성 그래프
  cycles: [{from, to, refs}]          # back-edges
  entry_points: [main.* / lib.* / ...]
deps:
  external_libs: [{name, version, why_used}]
  stdlib_usage: {alloc, fs, net, threading, async, ...}
  ffi_surface: [{c_lib, calls_count}]
build:
  system: cargo | npm | make | ...
  commands: {check, build, test, lint}
  artifacts: [...]
tests:
  framework: jest | go test | pytest | ...
  file_count: <number>
  coverage: <%>
  key_files: [...]
unsafe_surface:
  raw_pointers: <count>             # source 언어에서 unsafe / raw ptr
  global_state: <count>             # static / global var
  manual_alloc: <count>             # malloc / new / allocator pattern
risk_areas:
  - "async runtime — 큰 영향"
  - "FFI to libuv — 수동 매핑 필요"
  - ...
```

**Agent prompt 템플릿:**
```
You are doing pre-port discovery on a project. Read-only.

Project root: ${project_path}
Source language: ${source_lang}
Target: rust

Tasks:
1. Run: cd ${project_path} && cloc --include-lang=${source_lang},rust . 2>/dev/null || find . -name '*.${ext}' -exec wc -l {} + | tail -1
2. Enumerate modules / packages / crates.
3. Find dependency cycles (if static-type language).
4. Identify external lib deps + FFI surface.
5. Locate build system + test framework.
6. Scan for unsafe / raw pointer / global state patterns.
7. List top 20 largest files (LOC).
8. Flag risk areas: async runtime, FFI, generic-heavy code, macro-heavy code.

DO NOT modify any file. Output JSON matching the discovery schema.
Return ONLY the discovery JSON.
```

**Output**: discovery.json + Markdown summary written to `01-discovery.md`.

---

## Phase 2: Rulebook draft (산출물: `02-rulebook.md`)

bun 의 `PORTING.md` 에 해당. **언어쌍별 룰북.**

내용:

```markdown
# ${source_lang} → rust 포팅 룰북

## Ground rules
- 매 파일 끝에 PORT STATUS trailer (confidence, todos, source LOC, ported LOC).
- 절대 source `.${ext}` 편집 금지. ground truth.
- 모든 unsafe block 위 `// SAFETY:` 주석 필수.
- Forbidden: Box::leak, mem::forget for &'static, transmute lifetime, `let _ = result;` 에러 삼키기.

## Type map
| ${source_lang} | rust | 메모 |
|---|---|---|
| <source primitive> | <rust primitive> | ... |
| <source string> | Vec<u8>/&[u8]/String/&str | 데이터 vs 텍스트 구분 |
| <source ptr> | Box<T> / &T / Arc<T> / Option<NonNull<T>> | LIFETIMES 분류 후 |
| ... | ... | ... |

## Allocator handling
${language별 — Zig는 명시적 alloc, Go/TS는 GC, C는 malloc, Python은 refcount.}

## Error handling
| source pattern | rust pattern |
|---|---|
| <source error> | Result<T, E> with ? |
| ... | ... |

## Collections
| source | rust |
|---|---|
| <source list> | Vec<T> |
| <source map> | HashMap<K, V> |

## Concurrency
- ${source 언어의 async/threading model} → rust 에서는 ${tokio/async-std/std::thread/...}.

## Forbidden patterns (verifier 가 자동 reject)
- todo!() / unimplemented!() 가 final commit 에 남아있음
- #[cfg(any())] 게이트 그대로 잔존
- &mut 캐스트 from *const (UB)
- 표면적 transliteration (idiomatic Rust 아님)
- ${source lang} idiom 직역 (e.g. Zig `defer` → scopeguard guard 직역)

## Decision matrix
어떤 경우에 fix-forward 하고, 어떤 경우에 re-gate 하는지.
```

**중요**: 이 룰북 초안은 **사람이 검토해야 한다.** plan-port-to-rust 가 best guess 로 작성하지만, agent 가 무지성 적용하면 안 됨.

**파일 끝에 명시:**
```
🚨 SIGN-OFF REQUIRED: 이 룰북을 검토한 후 첫 줄에 "REVIEWED-BY: <name> <date>" 추가하기 전에는 port-to-rust 실행 금지.
```

---

## Phase 3: Pre-classify (산출물: `03-pre-classify.md`)

**Rust 가 target 일 때만** 필요. Go / Python 등 다른 target 이면 skip.

내용:

```yaml
ownership_classification:
  per_file_per_pointer_field:
    - file: src/foo.zig
      struct: Foo
      field: bar
      source_type: ?*Bar
      rust_class: OWNED | SHARED | BORROW_PARAM | STATIC | INTRUSIVE | FFI | UNKNOWN
      rust_type: Box<Bar> | Arc<Bar> | &'a Bar | ...
      evidence: src/foo.zig:42 — bun.new(Bar)
ffi_surface:
  per_extern_symbol:
    - name: uv_handle_t
      direction: import | export
      rust_repr: #[repr(C)] / extern "C" fn
unsafe_audit:
  per_unsafe_block:
    - file: ...
      reason: FFI | raw_ptr_deref | global_state | uninit_memory
```

**Agent prompt** (lifetime-classify.workflow.js 의 일반화):
```
Classify every pointer-like struct field in ${file}.

Taxonomy:
  OWNED        → Box<T>: 이 struct가 생성+해제
  SHARED       → Rc<T>/Arc<T>: ref-counted 다중 소유
  BORROW_PARAM → struct<'a>, &'a T: 생성자가 받음, 호출자 보장
  BORROW_FIELD → &'a T: 같은 struct의 다른 필드 안 가리킴
  STATIC       → &'static T: 전역/싱글톤
  BACKREF      → *const Parent (raw): 컨테이너 가리킴
  INTRUSIVE    → *mut T (raw): next/prev/link
  FFI          → *mut T / *const T (raw): C 경계
  ARENA        → StoreRef<T> / *const T: arena 안 가리킴
  UNKNOWN      → Option<NonNull<T>> + TODO

Return structured JSON. Cite file:line for evidence.
```

Agent verify pass: 3-vote refute on UNKNOWN + 12% sample.

산출: `LIFETIMES.tsv` (탭 구분: file, struct, field, source_type, class, rust_type, evidence).

---

## Phase 4: 각 phase 별 워크플로우 .md 생성

bun 의 phase ladder (A→H) 를 generic 하게 옮긴 워크플로우 정의. 각 .md 는 **execute 스킬이 읽을 spec**.

### `04-phase-a-draft.md` — Draft Port (Implement → Verify → Fix)

```yaml
phase: A
purpose: draft .rs 파일 생성 per source 파일
unit: per-file (source file)
parallelism: ${options.parallelism}
inputs:
  - 03-pre-classify.md (LIFETIMES.tsv if rust target)
  - 02-rulebook.md (REVIEWED-BY 확인)
steps:
  - implement:
      label: impl
      schema: {rs_path, confidence: high|medium|low, todos: int, rs_loc: int, note: str}
      prompt: |
        You are a Phase-A drafter. Translate ONE source file to draft target.
        1. Read 02-rulebook.md (whole file, every rule load-bearing).
        2. For rust target: grep LIFETIMES.tsv for this file's pre-classified types.
        3. Read source file ${file} (${loc} LOC). Chunked Read if >1800 lines.
        4. Write target file to EXACTLY: ${target_path} (deterministic mapping, not agent choice).
        5. Chunked Write if >1000 LOC: 800 lines per Edit call to avoid 180s timeout.
        6. Match structure, fn names, field order, control flow. End with PORT STATUS trailer.
        7. Return structured output.
        HARD RULES: DO NOT read other source files, DO NOT run builds, DO NOT git anything.
  - verify:
      label: verify
      mode: adversarial
      schema: {ok: bool, issues: [{rule, detail, fix, severity: must-fix|should-fix|nit}]}
      prompt: |
        Adversarial Phase-A verifier. Find every PORTING.md violation.
        Read: rulebook, source file, draft .rs.
        Check the enumerated rule violations (must be inline in this prompt — generated from rulebook).
        Default ok=false if any must-fix.
  - fix:
      label: fix
      schema: {applied: int, remaining: int, note: str}
      prompt: |
        Apply verifier findings. Surgical edits only. Update PORT STATUS trailer.
exit_criteria:
  - 모든 source file 이 draft .rs 갖는다
  - by_confidence 통계: high N, medium N, low N
verification:
  - count(.${ext} files) == count(.rs files in target tree)
  - 각 .rs 파일에 PORT STATUS trailer 존재
bd_issue:
  title: "Phase A: draft port — ${file_count} files"
  priority: P0
```

### `05-phase-b-cycle.md` — Cycle break + tier compile (정적 타입 target 한정)

```yaml
phase: B
purpose: 의존성 cycle 제거 + per-crate cargo check 통과
sub_phases:
  - B0_cyclebreak:
      steps: [classify back-edges, move-out, move-in, verify]
      unit: per back-edge, per source crate, per target crate
  - B1_tier_check:
      steps: [per-crate cargo check loop with gate-and-stub]
      unit: per crate
  - B2_ungate:
      steps: [ungate, verify (2-vote+tiebreak), fix]
      unit: per tier (T0→T1→T2→...)
ground_truth: docs/CYCLEBREAK.md (생성됨, plan-port-to-rust 가 초안 작성, 사람 검토)
skip_if: source_lang in [python, typescript-flexible]  # 동적/유연한 타입
bd_issue:
  title: "Phase B: cycle break + tier compile"
  priority: P0
```

### `06-phase-c-link.md` — Workspace link + first run (panic-swarm)

```yaml
phase: C
purpose: 전체 workspace 컴파일 + 최소 commands panic 없이 실행
loop:
  - link: cargo build -p target_bin
  - probe: N basic commands in parallel (--help, --version, simple eval)
  - dedup: panic location 별 grouping
  - fix: per unique panic location
        decision: fix-forward (port real .zig body) vs re-gate (call site)
exit_criteria: probes all_pass
max_rounds: 6
bd_issue:
  title: "Phase C: bin link + panic-swarm"
```

### `07-phase-d-todo.md` — Todo sweep + body fill

```yaml
phase: D
purpose: 모든 todo!() / unimplemented!() / cfg(any()) 게이트 제거 + body 작성
sub_workflows:
  - build_queue: cargo build → frontier file (most errors) → per-file fix → 2-vote verify → bugfix
  - blocked_on_resolve: grep todo("blocked_on: X::Y") → port X::Y upstream → replace callers
  - todo_sweep: grep todo!() → port from source spec → 2-vote verify
  - unsafe_audit: raw ptr 캐스트 audit, UB 분류 4종 → fix
max_rounds_per_subworkflow: 12
bd_issue:
  title: "Phase D: todo sweep + body fill"
```

### `08-phase-e-quality.md` — Refactor + idiom + layering

```yaml
phase: E
purpose: layering 문제 root-fix, 모든 slop 제거, idiomatic rust
banned_patterns:  # phase-e-proper-port 의 BANS 일반화
  - todo!() / unimplemented!() / unreachable!("stub")
  - #[cfg(any())] / mod _gated
  - &self as *const _ as *mut _   # UB cast
  - Box::leak / mem::forget for &'static
  - let _ = result;   # error swallow
  - transliterated ${source_lang}
mandate:
  - LAYERING FIRST: blocked_on todos 거의 다 dep cycle → MOVE type/fn, not stub
  - real bodies from source spec, no stubs
verify: 2-vote, accept only if slop_found==0 AND no layering-workaround AND no logic-bug
bd_issue:
  title: "Phase E: proper port + layering fix"
```

### `09-phase-f-test.md` — Smoke + test swarm

```yaml
phase: F
purpose: 테스트 통과율 ↑ (기존 source 의 테스트 suite 가 있다는 가정)
patterns:
  - probe_swarm: N commands → dedup panics → fix root cause
  - test_swarm: per-test-file run → categorize {completing, crashing, hanging} → fix per signature → 2-vote review
  - accessor_sweep: raw ptr 필드 → 안전 accessor → 2-vote review (aliasing/null/lifetime)
  - reviewed_refactor: worktree 격리 refactor → 2-vote (UB? semantics 바뀜? perf 회귀?)
worktree_isolation: true   # phase-f 부터 worktree per shard
bd_issue:
  title: "Phase F: test swarm + refactor"
```

### `10-phase-g-hardening.md` — Cross-platform + parity

```yaml
phase: G
purpose: cross-platform (windows/linux/mac) + 메인 branch parity + reliability audit
sub_workflows:
  - main_parity: source main branch 의 fix 들이 .rs 에 반영되었는지 verify, missing 한 것 port
  - cross_platform_bughunt: cfg(windows) / cfg(unix) 블록별 2-hunter adversarial
  - libuv_audit (or framework-specific): handle ownership 추적, async-close / callback-reclaim UB
  - idioms_audit: anti-pattern 카탈로그 → 2-vote verify → ranked fix doc
  - diff_review: 2-vote adversarial review per file in diff range
  - classify_issues: github crash/leak issues 분류 (mutations 금지)
worktree_isolation: true
bd_issue:
  title: "Phase G: hardening + parity"
```

---

## Phase 5: 자기개선 워크플로우 (`11-rulebook-audit.md`)

bun 의 `porting-md-zigleakage` 일반화. 룰북을 주기적으로 적대적 audit.

```yaml
purpose: 02-rulebook.md 자체에 source-language leakage 가 있는지 audit
dimensions:
  - allocator-handling
  - collections
  - manual-lifetime
  - error-model
  - pointer-idiom
  - generic-carryover    # source 의 generic system 직역
  - api-shape            # out-params / init-deinit pairs
  - trial-port-diff      # 3 sample files: rule-based vs idiomatic, diff
steps:
  - audit: per-dimension agent finds rule violations in rulebook itself
  - verify: 3-vote adversarial refute (default refuted=true)
  - synthesize: surviving findings → rulebook patch
schedule: 매 phase 종료 후 또는 사람 트리거
```

---

## Phase 6: state.template.json + bd-issues.template.md

### `state.template.json`

```json
{
  "project_path": "${project_path}",
  "source_lang": "${source_lang}",
  "target_lang": "rust",
  "current_phase": "A",
  "phases": {
    "A": {"status": "pending", "started": null, "completed": null, "files_done": 0, "files_total": 0, "by_confidence": {"high": 0, "medium": 0, "low": 0}},
    "B0": {"status": "pending"},
    "B1": {"status": "pending"},
    "B2": {"status": "pending"},
    "C": {"status": "pending"},
    "D": {"status": "pending"},
    "E": {"status": "pending"},
    "F": {"status": "pending"},
    "G": {"status": "pending"}
  },
  "shards": {
    "nshards": 1,
    "current_shard": 0
  },
  "verification": {
    "last_verified_at": null,
    "last_verify_passed": null
  },
  "human_signoffs": {
    "rulebook_reviewed": false,
    "pre_classify_reviewed": false
  }
}
```

### `bd-issues.template.md`

```markdown
# bd 이슈 템플릿 (port-to-rust 실행 스킬이 자동 생성)

각 phase 시작 시 bd create:
- Title: "Phase ${X}: ${purpose}"
- Priority: P0
- Type: task
- Labels: [port-to-rust, phase-${X}]
- Verification 명령어: ${phase_specific}

각 phase 종료 시 bd-close-verified:
- Status: verified
- 증거: ${verification_output}
```

---

## Phase 7: 산출물 검증 + 사용자 보고

생성 완료 후:

1. `tree ${project_path}/.claude/workflows/port-to-rust/` 로 구조 확인.
2. 각 .md 파일 BOM 검증: `head -c 3 <file> | xxd` → `efbb bf`.
3. 핵심 룰북 + LIFETIMES.tsv 가 작성되었는지.
4. 사용자에게 보고:
   ```
   ✅ port-to-rust 워크플로우 디렉토리 생성:
      ${project_path}/.claude/workflows/port-to-rust/
   📋 11개 .md 파일 + state.template.json + bd-issues.template.md

   다음 단계:
   1. 02-rulebook.md 검토 후 "REVIEWED-BY: <name> <date>" 추가
   2. 필요시 03-pre-classify.md 의 UNKNOWN 항목 수동 분류
   3. `port-to-rust` 스킬로 실행 시작 (auto 또는 phase 지정)

   ⚠️ 룰북 검토 안 하면 port-to-rust 가 거부함.
   ```

---

## HARD RULES

1. **이 스킬은 코드를 절대 수정하지 않는다.** 오직 `.claude/workflows/port-to-rust/` 디렉토리 안의 plan 문서만 생성.
2. **source 언어 파일은 절대 건드리지 않는다.** read-only.
3. **자동 감지가 50% 미만 확신이면 사용자에게 명시 요청.**
4. **rulebook 초안은 best-guess** — 사람 검토 SIGN-OFF 없이는 port-to-rust 가 거부.
5. **모든 출력 .md 파일은 UTF-8 BOM + NFC 재포장.**
6. **기존 `.claude/workflows/port-to-rust/` 가 있으면 덮어쓰지 말고 `port-to-rust-v2/` 또는 timestamp suffix.**

---

## bd 통합

```bash
bd create --title "plan-port-to-rust: ${project_name} ${source_lang}→rust" \
  --type task --priority P0 \
  --label port-to-rust --label planning

# 완료 후
./scripts/bd-verify <id> 'ls ${project_path}/.claude/workflows/port-to-rust/*.md | wc -l'
./scripts/bd-close-verified <id> "완료: plan 생성, 11 phase docs + templates"
```

---

## 참조

- 원본 패턴: bun `.claude/workflows/` @ SHA 23427dbc12fdcff30c23a96a3d6a66d62fdc091d
- 분석 문서: `/home/zhugehyuk/2lab.ai/soul/p9/ARTIFACTS/analyses/2026-05-15-bun-claude-workflows-zig-to-rust-port-analysis.md`
- 실행 스킬: `~/2lab.ai/skills/port-to-rust/SKILL.md`
- Karpathy plan-then-execute 패턴: plan 은 cheap+deterministic, execute 는 expensive+parallel.

---

**한 줄 요약: 어떤 언어 → rust 든 입력 받아서 bun 식 50+ phase 워크플로우 디렉토리 생성. 실행은 다음 스킬이.**
