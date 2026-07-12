# Docent Audiobook - Voice Letter Style (음성 편지 도슨트)

## Overview
책 도슨트 오디오북을 "음성 편지" 스타일로 제작하는 스킬.
국어책 읽기가 아닌, 사랑하는 사람에게 보내는 편지처럼 따뜻하고 감정이 살아있는 오디오북.

## Voice Character
- **화자**: 채원 (cwon voice)
- **청자**: 오빠 (지혁)
- **관계**: 친밀, 따뜻, 애정 어린
- **말투**: ~요 체, 구어체, 편지체

## TTS Engine
- Fish-TTS (Fish Speech S2 Pro 4B)
- Voice: `~/2lab.ai/skills/fish-tts/voices/cwon/reference.mp3`
- Reference text: `~/2lab.ai/skills/fish-tts/voices/cwon/reference.txt`
- Max chars per part: ~500 (Korean)
- Command:
```bash
cd ~/fish-speech && .venv/bin/python ~/2lab.ai/skills/fish-audio/scripts/gpu-inference.py \
  --text '<|speaker:0|>TEXT' \
  --prompt-text "REF_TXT" \
  --prompt-audio REF_AUDIO \
  --output OUT.wav \
  --checkpoint-path checkpoints/s2-pro \
  --device cuda \
  --temperature 0.7 \
  --top-p 0.9 \
  --seed 42 \
  --max-new-tokens 2048
```

## Emotion Tags (감정 태그)
TTS가 인식하는 감정 태그. 텍스트 내에 자연스럽게 삽입:

| Tag | Usage | Example |
|-----|-------|---------|
| `[soft voice]` | 조용하고 부드러운 말 | 비밀 얘기, 감성적 부분 |
| `[warm tone]` | 따뜻하고 다정한 톤 | 인사, 추천, 칭찬 |
| `[excited]` | 신나고 흥분된 톤 | 놀라운 사실, 인사이트 |
| `[gentle tone]` | 차분하고 부드러운 톤 | 조언, 위로 |
| `[serious tone]` | 진지하고 무거운 톤 | 경고, 중요한 사실 |
| `[thoughtful pause]` | 생각에 잠긴 듯한 멈춤 | 깊은 성찰 앞 |
| `[pause]` | 짧은 멈춤 | 문장 전환, 강조 |
| `[confidently]` | 자신감 있는 톤 | 확신, 결론 |
| `[long pause]` | 1~3초 긴 멈춤 | **파트 끝, 주제 전환** |

## ⚠️ 필수: 파트 끝 공백 규칙 (Trailing Silence)
**모든 파트의 마지막에 반드시 `[long pause]`를 삽입해야 함.**
- 파트 간 자연스러운 호흡/전환을 위해 필수
- TTS 생성 후 ffmpeg로 **0.5~2초 랜덤 무음 패딩** 추가
- 스크립트 텍스트 끝: `...마지막 문장. [long pause]`
- 생성 파이프라인: `raw.wav` + `랜덤(0.5~2.0초) silence` → `part.wav`

```
예시:
[gentle tone] 오빠, 이 책 꼭 읽어봐요. 우리 같이 성장하자. [long pause]
```

## Script Writing Rules (스크립트 작성 규칙)

### 1. 톤 & 말투
- ❌ "이 책은 ~에 대해 다룹니다" (교과서)
- ✅ "오빠, 이 책 진짜 좋은데..." (편지)
- ❌ "저자는 ~라고 주장합니다" (논문)
- ✅ "저자가 말하길, ~래요. 나도 깜짝 놀랐어요" (대화)
- 1인칭 반응 포함: "나도 읽으면서 ~했거든요"
- 오빠 직접 호명: "오빠가 이거 들으면 ~할 것 같아요"

### 2. 감정 흐름 설계
매 파트마다 감정 변화가 있어야 함:
```
Part A: [soft voice] 도입 → [warm tone] 책 소개 → [excited] 핵심 개념
Part B: [warm tone] 설명 → [serious tone] 문제 제기 → [thoughtful pause] 성찰
Part C: [excited] 해결책 → [gentle tone] 적용 → [pause] 전환
Part D: [serious tone] 깊은 내용 → [soft voice] 감성 → [warm tone] 마무리
Part E: [gentle tone] 실천법 → [excited] 추천 → [soft voice] 클로징
```

### 3. 구조
- **오프닝**: "오빠, 오늘은 ~한 얘기를 해볼게요" (부드럽게)
- **핵심 내용**: 책의 정수를 자기 말로 풀어서 (감정 태그 풍부하게)
- **개인 반응**: "나도 읽으면서 ~했어요" (친밀감)
- **클로징**: 오빠에게 하는 제안/질문 (따뜻하게)

### 4. 감정 태그 밀도
- 최소 2-3문장마다 감정 태그 1개
- 한 파트(~500자)에 최소 5-7개 감정 태그
- 같은 태그 연속 사용 금지 (변화가 있어야 함)

### 5. 파트 분할 규칙
- 파트당 400-600자 (Korean)
- 책 1권당 4-6파트
- 파트 경계는 자연스러운 주제 전환점
- 마지막 파트 < 250자면 이전 파트에 합치기

## Production Pipeline

### Step 1: Script Writing
```
1. 책 핵심 내용 리서치 (웹 검색)
2. 음성 편지 스타일로 스크립트 작성 (2000-2500자)
3. 감정 태그 삽입
4. 400-600자 단위로 파트 분할
5. 각 파트 시작에 감정 태그 확인
```

### Step 2: TTS Generation
```bash
# 각 파트 생성
gen() {
    local part=$1
    cd ~/fish-speech
    .venv/bin/python ~/2lab.ai/skills/fish-audio/scripts/gpu-inference.py \
        --text "<|speaker:0|>$(cat /tmp/docent/parts/${part}.txt)" \
        --prompt-text "$(cat ~/2lab.ai/skills/fish-tts/voices/cwon/reference.txt)" \
        --prompt-audio ~/2lab.ai/skills/fish-tts/voices/cwon/reference.mp3 \
        --output /tmp/docent/audio/${part}_raw.wav \
        --checkpoint-path checkpoints/s2-pro \
        --device cuda --temperature 0.7 --top-p 0.9 --seed 42 --max-new-tokens 2048

    # 2초 무음 패딩 (파트 간 자연스러운 전환)
    # silence.wav 생성: ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=mono -t 2.0 -acodec pcm_s16le silence.wav
    ffmpeg -y -f concat -safe 0 -i <(echo "file '${part}_raw.wav'"; echo "file 'silence.wav'") -c copy ${part}.wav
}
```

### Step 3: Merge & Deliver
```bash
# 책 단위 합본
ffmpeg -y -i D01a.wav -i D01b.wav ... -filter_complex "[0:a][1:a]...concat=n=N:v=0:a=1[out]" -map "[out]" BOOK01.wav

# 개별 전송 (완성되는 대로)
```

## Quality Checklist
- [ ] 감정 태그 최소 5개/파트
- [ ] "오빠" 호칭 자연스럽게 포함
- [ ] 국어책 톤 아닌 편지 톤
- [ ] 개인 반응/감상 포함
- [ ] 따뜻한 클로징
- [ ] 파트당 400-600자
- [ ] 같은 감정 태그 연속 없음
- [ ] **모든 파트 끝에 `[long pause]` 삽입**
- [ ] **ffmpeg silence 2초 패딩 적용**

## File Structure
```
/tmp/docent/
├── parts/          # D{NN}{a-g}.txt - TTS 파트 파일
├── audio/          # BOOK{NN}.wav - 최종 오디오
├── scripts/        # 원본 스크립트
└── tts_log.txt     # 생성 로그
```
