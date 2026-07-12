#!/usr/bin/env python3
"""
Cohere STT Benchmark: Generate 100 TTS samples via fish-tts, transcribe with Cohere, measure WER.

Usage:
  python benchmark.py --generate    # Step 1: Generate 100 TTS audio samples
  python benchmark.py --transcribe  # Step 2: Transcribe all samples
  python benchmark.py --evaluate    # Step 3: Calculate WER / recognition rate
  python benchmark.py --all         # Run all steps

Output: ~/2lab.ai/skills/cohere-stt/output/benchmark_results.json
"""

import argparse
import json
import os
import subprocess
import sys
import time
import re
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = SKILL_DIR / "output" / "benchmark"
SAMPLES_FILE = SKILL_DIR / "output" / "benchmark_samples.json"
RESULTS_FILE = SKILL_DIR / "output" / "benchmark_results.json"
FISH_TTS_SCRIPT = "/home/zhugehyuk/2lab.ai/skills/fish-tts/scripts/fish-tts.sh"
VENV_PYTHON = "/home/zhugehyuk/.cohere-stt-venv/bin/python"
INFERENCE_SCRIPT = SKILL_DIR / "scripts" / "inference.py"

# 100 Korean test sentences - diverse topics, lengths, styles
KOREAN_SENTENCES = [
    # Basic greetings and daily conversation (1-10)
    "안녕하세요, 오늘 날씨가 참 좋네요.",
    "감사합니다. 다음에 또 뵙겠습니다.",
    "오늘 저녁에 뭐 먹을까요?",
    "내일 오전 열 시에 회의가 있습니다.",
    "죄송합니다, 다시 한번 말씀해 주시겠어요?",
    "주말에 가족들이랑 여행 갈 거예요.",
    "이번 주 금요일까지 보고서를 제출해야 합니다.",
    "커피 한 잔 하실래요?",
    "지금 몇 시인지 알려주세요.",
    "오랜만이에요! 잘 지내셨어요?",

    # Technology and AI (11-20)
    "인공지능 기술이 빠르게 발전하고 있습니다.",
    "딥러닝 모델의 파라미터 수가 수십억 개에 달합니다.",
    "자연어 처리 분야에서 트랜스포머 아키텍처가 혁신을 가져왔습니다.",
    "음성 인식 기술은 이제 사람과 비슷한 수준에 도달했습니다.",
    "텍스트를 음성으로 변환하는 기술을 TTS라고 합니다.",
    "GPU 메모리가 부족하면 배치 크기를 줄여야 합니다.",
    "오픈소스 프로젝트에 기여하는 것은 매우 의미 있는 일입니다.",
    "데이터 전처리 과정이 모델 성능에 큰 영향을 미칩니다.",
    "클라우드 컴퓨팅으로 서버 관리 비용을 절감할 수 있습니다.",
    "블록체인 기술은 탈중앙화된 신뢰 시스템을 제공합니다.",

    # Business and economy (21-30)
    "올해 매출이 전년 대비 삼십 퍼센트 증가했습니다.",
    "투자 포트폴리오를 다양화하는 것이 리스크 관리의 기본입니다.",
    "스타트업 생태계에서 시리즈 A 투자를 유치하는 것이 중요합니다.",
    "글로벌 공급망 문제가 제조업에 영향을 미치고 있습니다.",
    "분기별 실적 발표에서 영업이익이 크게 개선되었습니다.",
    "고객 만족도 조사 결과를 바탕으로 서비스를 개선하겠습니다.",
    "마케팅 전략을 재수립하여 시장 점유율을 높이겠습니다.",
    "원자재 가격 상승으로 인해 제품 가격 인상이 불가피합니다.",
    "신규 채용 공고를 다음 주에 올릴 예정입니다.",
    "재무제표 분석 결과 현금 흐름이 안정적입니다.",

    # Science and education (31-40)
    "양자 컴퓨터는 기존 컴퓨터로는 풀 수 없는 문제를 해결할 수 있습니다.",
    "핵융합 에너지는 미래 에너지원으로 주목받고 있습니다.",
    "유전자 편집 기술인 크리스퍼는 의학 혁명을 이끌고 있습니다.",
    "화성 탐사 프로젝트가 이십삼십 년대에 본격화될 전망입니다.",
    "기후 변화로 인해 전 세계적으로 이상 기후가 증가하고 있습니다.",
    "수학적 사고력은 논리적 문제 해결에 필수적입니다.",
    "대학원 과정에서는 독립적인 연구 능력이 요구됩니다.",
    "과학적 방법론은 가설 설정, 실험, 검증의 과정을 따릅니다.",
    "생물 다양성 보전을 위한 국제적 협력이 필요합니다.",
    "통계학은 데이터 기반 의사 결정의 핵심 도구입니다.",

    # Culture and daily life (41-50)
    "한국 드라마가 전 세계적으로 인기를 얻고 있습니다.",
    "김치찌개는 한국의 대표적인 가정식 메뉴입니다.",
    "서울의 대중교통 시스템은 매우 효율적입니다.",
    "독서는 창의력과 사고력을 키우는 좋은 습관입니다.",
    "운동을 꾸준히 하면 건강을 유지할 수 있습니다.",
    "전통 시장에서 신선한 식재료를 구입할 수 있습니다.",
    "봄에는 벚꽃 구경을 하러 많은 사람들이 공원에 모입니다.",
    "요즘 재택근무가 보편화되면서 생활 패턴이 변했습니다.",
    "한글은 과학적으로 설계된 문자 체계입니다.",
    "추석에는 가족들이 모여 송편을 빚습니다.",

    # Numbers and technical terms (51-60)
    "전화번호는 영일공 이삼사오 육칠팔구입니다.",
    "총 비용은 삼백오십만 원이 될 것으로 예상됩니다.",
    "서버 응답 시간이 이백 밀리초 이내여야 합니다.",
    "파이썬 삼점십이 버전에서 새로운 기능이 추가되었습니다.",
    "메모리 사용량이 십육 기가바이트를 초과하지 않도록 관리해야 합니다.",
    "API 요청 속도를 초당 백 회로 제한하겠습니다.",
    "섭씨 영하 오 도에서 실험을 진행했습니다.",
    "데이터베이스에 약 오백만 건의 레코드가 저장되어 있습니다.",
    "네트워크 대역폭은 기가비트 이더넷을 사용합니다.",
    "배터리 용량이 오천 밀리암페어아워입니다.",

    # Complex sentences (61-70)
    "비록 시간이 오래 걸리더라도 정확하게 작업하는 것이 중요합니다.",
    "만약 내일 비가 온다면 실내에서 운동할 계획입니다.",
    "그 프로젝트가 성공할 수 있었던 이유는 팀원들의 협력 덕분입니다.",
    "기술적 한계를 극복하기 위해서는 창의적인 접근이 필요합니다.",
    "경제 성장과 환경 보호를 동시에 추구하는 것이 지속 가능한 발전입니다.",
    "인공지능이 인간의 일자리를 대체할 것이라는 우려가 있지만 새로운 직업도 창출될 것입니다.",
    "교육 시스템을 개혁하지 않으면 미래 사회에 필요한 인재를 양성하기 어렵습니다.",
    "글로벌 팬데믹 이후 원격 의료 서비스에 대한 수요가 급증했습니다.",
    "빅데이터 분석을 통해 소비자 행동 패턴을 예측할 수 있습니다.",
    "자율주행 자동차가 상용화되면 교통사고가 크게 줄어들 것으로 기대됩니다.",

    # Mixed Korean-English (71-80)
    "이번 업데이트에서 유저 인터페이스를 대폭 개선했습니다.",
    "머신러닝 파이프라인을 최적화하여 트레이닝 시간을 단축했습니다.",
    "프론트엔드는 리액트로, 백엔드는 노드제이에스로 개발했습니다.",
    "도커 컨테이너를 사용하여 배포 환경을 표준화했습니다.",
    "깃허브에서 풀 리퀘스트를 통해 코드 리뷰를 진행합니다.",
    "트랜스포머 모델의 어텐션 메커니즘은 시퀀스 내 관계를 학습합니다.",
    "클라우드 서비스를 활용하여 스케일링 문제를 해결했습니다.",
    "에이피아이 게이트웨이를 통해 마이크로서비스 간 통신을 관리합니다.",
    "디브옵스 문화를 도입하여 개발과 운영의 간격을 좁혔습니다.",
    "데이터 레이크에서 필요한 데이터를 추출하여 분석합니다.",

    # Short phrases (81-90)
    "네, 알겠습니다.",
    "잠시만 기다려주세요.",
    "괜찮습니다, 걱정 마세요.",
    "정말요? 대단하네요!",
    "그건 좀 어려울 것 같아요.",
    "다시 한번 확인해 보겠습니다.",
    "좋은 아이디어네요.",
    "내일 다시 연락드리겠습니다.",
    "수고하셨습니다.",
    "감사합니다, 도움이 많이 되었습니다.",

    # Longer narrative (91-100)
    "오늘 아침에 일어나서 커피를 마시면서 뉴스를 봤는데 흥미로운 기사가 많았습니다.",
    "지난주에 새로운 프로젝트를 시작했는데 팀원들 모두 의욕적으로 참여하고 있습니다.",
    "이번 달 목표는 사용자 수를 두 배로 늘리는 것입니다.",
    "회의에서 결정된 사항을 정리하여 모든 관련자에게 공유하겠습니다.",
    "기술 면접에서는 알고리즘과 자료구조에 대한 이해가 중요합니다.",
    "새로운 버전의 소프트웨어를 출시하기 전에 충분한 테스트가 필요합니다.",
    "고객의 피드백을 반영하여 제품을 지속적으로 개선하고 있습니다.",
    "올해 목표를 달성하기 위해 분기별로 진행 상황을 점검하겠습니다.",
    "인공지능 윤리에 대한 논의가 학계와 산업계 모두에서 활발히 이루어지고 있습니다.",
    "프로그래밍을 배우는 가장 좋은 방법은 직접 코드를 작성하고 실행해 보는 것입니다.",
]


def normalize_text(text: str) -> str:
    """Normalize text for comparison: remove punctuation, extra spaces, lowercase."""
    # Remove common punctuation
    text = re.sub(r'[.,!?;:"\'\-\(\)\[\]{}]', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate character-level Levenshtein distance."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    prev_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row

    return prev_row[-1]


def character_error_rate(reference: str, hypothesis: str) -> float:
    """Calculate Character Error Rate (CER)."""
    ref = normalize_text(reference)
    hyp = normalize_text(hypothesis)
    if len(ref) == 0:
        return 0.0 if len(hyp) == 0 else 1.0
    distance = levenshtein_distance(ref, hyp)
    return distance / len(ref)


def generate_samples(voices: list[str] = None, limit: int = 100):
    """Generate TTS audio samples using fish-tts."""
    if voices is None:
        voices = ["cwon", "elon"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    samples = []
    sentences = KOREAN_SENTENCES[:limit]

    print(f"[benchmark] Generating {len(sentences)} TTS samples...", file=sys.stderr)

    for i, sentence in enumerate(sentences):
        voice = voices[i % len(voices)]
        output_path = OUTPUT_DIR / f"sample_{i:03d}_{voice}.wav"

        if output_path.exists():
            print(f"  [{i+1}/{len(sentences)}] Skipping (exists): {output_path.name}", file=sys.stderr)
            samples.append({
                "id": i,
                "text": sentence,
                "voice": voice,
                "audio_path": str(output_path),
            })
            continue

        print(f"  [{i+1}/{len(sentences)}] Generating: {voice} - {sentence[:40]}...", file=sys.stderr)

        try:
            result = subprocess.run(
                [FISH_TTS_SCRIPT, sentence, "--voice", voice, "--output", str(output_path)],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                print(f"    ERROR: {result.stderr[:200]}", file=sys.stderr)
                continue

            samples.append({
                "id": i,
                "text": sentence,
                "voice": voice,
                "audio_path": str(output_path),
            })

        except subprocess.TimeoutExpired:
            print(f"    TIMEOUT: Skipping", file=sys.stderr)
        except Exception as e:
            print(f"    ERROR: {e}", file=sys.stderr)

    # Save samples metadata
    with open(SAMPLES_FILE, "w", encoding="utf-8") as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)

    print(f"[benchmark] Generated {len(samples)} samples → {SAMPLES_FILE}", file=sys.stderr)
    return samples


def transcribe_samples(samples: list[dict] = None) -> list[dict]:
    """Transcribe all samples using Cohere STT."""
    if samples is None:
        with open(SAMPLES_FILE, "r") as f:
            samples = json.load(f)

    # Filter to existing files
    valid_samples = [s for s in samples if os.path.isfile(s["audio_path"])]
    if not valid_samples:
        print("[benchmark] No valid audio files found!", file=sys.stderr)
        return []

    audio_paths = [s["audio_path"] for s in valid_samples]

    print(f"[benchmark] Transcribing {len(audio_paths)} files...", file=sys.stderr)

    # Use batch inference
    result = subprocess.run(
        [VENV_PYTHON, str(INFERENCE_SCRIPT), "--json", "--language", "ko", "--compile"] + audio_paths,
        capture_output=True,
        text=True,
        timeout=600,
    )

    if result.returncode != 0:
        print(f"[benchmark] Transcription error: {result.stderr[:500]}", file=sys.stderr)
        return []

    transcription_data = json.loads(result.stdout)

    # Merge transcriptions with samples
    for i, (sample, tr_result) in enumerate(zip(valid_samples, transcription_data["results"])):
        sample["transcription"] = tr_result["text"]
        sample["audio_duration_s"] = tr_result["duration_s"]

    # Save
    with open(SAMPLES_FILE, "w", encoding="utf-8") as f:
        json.dump(valid_samples, f, ensure_ascii=False, indent=2)

    print(f"[benchmark] Transcribed {len(valid_samples)} samples", file=sys.stderr)
    print(f"[benchmark] Stats: {json.dumps(transcription_data.get('stats', {}), indent=2)}", file=sys.stderr)
    return valid_samples


def evaluate_samples(samples: list[dict] = None) -> dict:
    """Calculate WER and recognition rate."""
    if samples is None:
        with open(SAMPLES_FILE, "r") as f:
            samples = json.load(f)

    total = len(samples)
    total_cer = 0.0
    exact_matches = 0
    near_matches = 0  # CER < 0.1
    results = []

    for sample in samples:
        ref = sample["text"]
        hyp = sample.get("transcription", "")

        cer = character_error_rate(ref, hyp)
        is_exact = normalize_text(ref) == normalize_text(hyp)
        is_near = cer < 0.1

        if is_exact:
            exact_matches += 1
        if is_near:
            near_matches += 1
        total_cer += cer

        results.append({
            "id": sample["id"],
            "voice": sample.get("voice", "unknown"),
            "reference": ref,
            "hypothesis": hyp,
            "cer": round(cer, 4),
            "exact_match": is_exact,
            "near_match": is_near,
        })

    avg_cer = total_cer / total if total > 0 else 0
    exact_rate = exact_matches / total if total > 0 else 0
    near_rate = near_matches / total if total > 0 else 0

    summary = {
        "total_samples": total,
        "exact_matches": exact_matches,
        "near_matches_cer_lt_10pct": near_matches,
        "exact_match_rate": round(exact_rate * 100, 1),
        "near_match_rate": round(near_rate * 100, 1),
        "average_cer": round(avg_cer * 100, 2),
        "model": "CohereLabs/cohere-transcribe-03-2026",
        "language": "ko",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Per-voice breakdown
    voices = set(s.get("voice", "unknown") for s in samples)
    voice_stats = {}
    for voice in voices:
        voice_samples = [r for r in results if r["voice"] == voice]
        v_total = len(voice_samples)
        v_cer = sum(r["cer"] for r in voice_samples) / v_total if v_total else 0
        v_exact = sum(1 for r in voice_samples if r["exact_match"])
        v_near = sum(1 for r in voice_samples if r["near_match"])
        voice_stats[voice] = {
            "total": v_total,
            "avg_cer": round(v_cer * 100, 2),
            "exact_rate": round(v_exact / v_total * 100, 1) if v_total else 0,
            "near_rate": round(v_near / v_total * 100, 1) if v_total else 0,
        }

    # Worst performers
    worst = sorted(results, key=lambda r: -r["cer"])[:10]

    report = {
        "summary": summary,
        "voice_stats": voice_stats,
        "worst_10": worst,
        "all_results": results,
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Print summary
    print("\n" + "=" * 60, file=sys.stderr)
    print("COHERE STT BENCHMARK RESULTS", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Total Samples: {total}", file=sys.stderr)
    print(f"Exact Match Rate: {summary['exact_match_rate']}%", file=sys.stderr)
    print(f"Near Match Rate (CER<10%): {summary['near_match_rate']}%", file=sys.stderr)
    print(f"Average CER: {summary['average_cer']}%", file=sys.stderr)
    print(f"\nPer-Voice Breakdown:", file=sys.stderr)
    for voice, stats in voice_stats.items():
        print(f"  {voice}: CER={stats['avg_cer']}%, Exact={stats['exact_rate']}%, Near={stats['near_rate']}%", file=sys.stderr)
    print(f"\nResults saved to: {RESULTS_FILE}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    return report


def main():
    parser = argparse.ArgumentParser(description="Cohere STT Benchmark")
    parser.add_argument("--generate", action="store_true", help="Generate TTS samples")
    parser.add_argument("--transcribe", action="store_true", help="Transcribe samples")
    parser.add_argument("--evaluate", action="store_true", help="Evaluate results")
    parser.add_argument("--all", action="store_true", help="Run all steps")
    parser.add_argument("--limit", type=int, default=100, help="Number of samples")
    parser.add_argument(
        "--voices", nargs="+", default=["cwon", "elon"],
        help="Voices to use (default: cwon elon)"
    )
    args = parser.parse_args()

    if args.all:
        args.generate = args.transcribe = args.evaluate = True

    if not (args.generate or args.transcribe or args.evaluate):
        parser.print_help()
        sys.exit(1)

    if args.generate:
        samples = generate_samples(voices=args.voices, limit=args.limit)

    if args.transcribe:
        samples = transcribe_samples()

    if args.evaluate:
        evaluate_samples()


if __name__ == "__main__":
    main()
