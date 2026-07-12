---
name: yt-dub
description: YouTube 영상을 한국어로 더빙해서 원본 영상에 다시 붙이는 스킬. STT는 faster-whisper (local GPU), 번역은 Codex/Claude 서브에이전트, TTS는 fish-tts (cwon=여성/elon=남성, 화자 피치로 자동 분기). 외부 유료 API 0개. dubyduby (SihyunAdventure/dubyduby) 의 6-stage 파이프라인을 차용해 KO 더빙용으로 재설계.
---

# yt-dub — YouTube → Korean Dub

## TL;DR
```bash
~/2lab.ai/skills/yt-dub/scripts/dub.sh "https://youtu.be/<VIDEO_ID>"
# → ~/yt-dub-projects/<video_id>/6_final/dubbed_video.mp4
```

## 무엇을 하는가
1. **다운로드**: yt-dlp 로 원본 mp4 + mp3 추출
2. **STT**: faster-whisper `large-v3` GPU, word-level timestamp + VAD
3. **번역**: Codex(`codex exec`) → JSON 한 줄짜리 sentences.json (대안: Gemini/Claude 서브에이전트)
4. **화자 분석**: librosa.pyin 으로 utterance 별 median f0 → 165 Hz 경계로 cwon(여) / elon(남) 자동 매핑
5. **TTS**: fish-tts (`http://blade-4090:9999`) cwon / elon 음성 합성, 44.1k → 16-bit WAV
6. **타이밍 매치**: 각 utterance 를 원본 token 의 start_ms 에 anchor, `atempo` 로 길이 맞춤 (`max=1.6`)
7. **최종 합성**: ffmpeg 로 원본 영상 + 더빙 오디오 mux (원본 BGM/SFX 는 손실됨 — 향후 별도 stem 분리로 보존 예정)

## Dependencies (외부 API 키 0개)

| 도구 | 위치 | 비고 |
|---|---|---|
| yt-dlp | `~/.local/bin/yt-dlp` 2026.03.13 | 다운로드 |
| ffmpeg | `~/.local/bin/ffmpeg` 7.0.2-static | aac/mp3/atempo |
| faster-whisper | `~/2lab.ai/.venv/bin` (pip 1.2.1) | STT, CUDA float16 |
| librosa | `~/2lab.ai/.venv/bin` (0.11.0) | 피치 기반 화자 성별 |
| Codex CLI | `~/2lab.ai/soma/node_modules/.bin/codex` 0.95.0 | OAuth, 번역 |
| fish-tts | `http://blade-4090:9999/api/tts/chunk` | cwon/elon 음성 |

## CLI

```bash
# 풀파이프 (URL → 최종 mp4)
scripts/dub.sh <URL> [--max-seconds 60]

# 단계별 (디버깅 / 재시작용)
scripts/download.sh        <project_dir> <URL>
scripts/transcribe.py      <project_dir> [--model large-v3] [--language auto]
scripts/translate.py       <project_dir> [--engine codex|gemini|claude]
scripts/analyze_speakers.py <project_dir>
scripts/synthesize.py      <project_dir>
scripts/place_timeline.py  <project_dir>
scripts/finalize.sh        <project_dir>
```

## 프로젝트 디렉터리 레이아웃 (dubyduby 차용)

```
~/yt-dub-projects/<video_id>/
├── 1_source/
│   ├── video.mp4        # 원본
│   └── audio.mp3        # 추출
├── 2_transcript/
│   ├── words.json       # faster-whisper word-level
│   └── transcript.md    # 번역 입력용
├── 3_translation/
│   └── sentences.json   # [{i,en,ko,startMs,endMs,speaker?}, ...]
├── 4_synth/
│   ├── speakers.json    # utt → cwon|elon (gender)
│   └── utt-NNN.mp3      # fish-tts 출력 (utt 번호 zero-pad 3)
├── 5_intermediate/
│   ├── placement.json   # {i, startMs, atempo, padBeforeMs}
│   └── dubbed_audio.wav # 최종 트랙 (44.1kHz, mono)
└── 6_final/
    └── dubbed_video.mp4 # 원본 video + dubbed_audio mux
```

## 화자 자동 분기 알고리즘

```
utterance 별 오디오 슬라이스 → librosa.pyin(fmin=80, fmax=400) →
  median_f0 < 165 Hz   → elon (남성)
  median_f0 ≥ 165 Hz   → cwon (여성)
  voiced ratio < 0.15  → 직전 utterance 화자 상속
```

수동 오버라이드: `4_synth/speakers.json` 직접 수정 후 `synthesize.py --resume`

## 핵심 상수 (튜닝 포인트)

| 상수 | 값 | 출처 / 이유 |
|---|---|---|
| `ATEMPO_MAX` | `1.6` | dubyduby — 한국어 1.6배 이상은 듣기 거북함 |
| `ATEMPO_MIN` | `1.0` | 절대 느리게 하지 않음 (원본 mouth-cue 보존) |
| `TRAIL_MS`   | `120` | utt 끝 호흡 여백 |
| `PITCH_BOUNDARY_HZ` | `165` | M/F 경계, 노래/속삭임은 어긋날 수 있음 |

## 알려진 한계

- **BGM/SFX 손실**: 현재는 원본 오디오 트랙을 완전히 대체. 음악 보존하려면 demucs/htdemucs 로 vocals 분리 후 더빙 트랙만 교체 — TODO
- **다화자 한 utterance**: faster-whisper 의 segment 가 두 사람 발화를 합치면 한 목소리로 더빙됨. 해결책: diarization (pyannote) 추가 — TODO
- **자막 SRT 동기화**: 현재는 안 만듦. `--with-srt` 옵션 추가 예정

## 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| `ModuleNotFoundError: faster_whisper` | venv 누락 | `~/2lab.ai/.venv/bin/pip install faster-whisper` |
| `CUDA out of memory` | large-v3 + 다른 GPU 잡 | `--model medium` 또는 `--device cpu` |
| fish-tts 503/cold-start | soma-voice 서비스 down | `ssh blade-4090 systemctl --user start ai.2lab.soma-voice.main.service` |
| Codex `token_expired` | OAuth 만료 | `codex exec --skip-git-repo-check "ping"` 1회 → auto refresh |
| `atempo` 1.6 초과 요구 | 번역이 너무 김 | translator 재호출 시 `aggressive_shorten: true` |

## Reference

원본: https://github.com/SihyunAdventure/dubyduby (MIT)
변경점 vs dubyduby:
- Soniox → faster-whisper (로컬 GPU, API 키 불필요)
- Supertonic → fish-tts (이미 인프라 구축됨)
- 5단계 voice slot → 2-voice (cwon/elon) + pitch gating
- Phase split 제거 → 단일 파이프라인 (translate 단계만 동기 sub-agent)
