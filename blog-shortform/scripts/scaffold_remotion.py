#!/usr/bin/env python3
"""captions.json + public/images/* + public/audio/voice.mp3 → Remotion v4 프로젝트 스캐폴드.

세로 1080×1920 / 30fps. 컷별 이미지 시퀀스 + 통합 오디오 트랙 + 자막.
remotion-video-builder의 "메인 mp4 1개" 구조 대신, 컷별 <Img> 슬라이드 + Ken Burns로 구성.

사용 예:
    python3 scaffold_remotion.py <project_dir>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import quote

try:
    import requests
except ImportError:
    requests = None  # QR 다운로드 실패 시 graceful degrade


PACKAGE_JSON = """{
  "name": "blog-shortform",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "remotion studio",
    "build": "remotion render src/index.ts BlogShortform out/video.mp4"
  },
  "dependencies": {
    "@remotion/cli": "^4.0.0",
    "remotion": "^4.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "typescript": "^5.4.0"
  }
}
"""

TSCONFIG_JSON = """{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"]
}
"""

REMOTION_CONFIG_TS = """import {Config} from "@remotion/cli/config";
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
"""

INDEX_TS = """import {registerRoot} from "remotion";
import {RemotionRoot} from "./Root";
registerRoot(RemotionRoot);
"""

ROOT_TSX = """import {Composition} from "remotion";
import {BlogShortform} from "./compositions/BlogShortform";
import {TOTAL_FRAMES, FPS, WIDTH, HEIGHT} from "./data/scenes";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="BlogShortform"
    component={BlogShortform}
    durationInFrames={TOTAL_FRAMES}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
  />
);
"""

SPEECH_CAPTION_TSX = """import React from "react";
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from "remotion";

type Speaker = "A" | "B";

const SPEAKER_COLOR: Record<Speaker, string> = {
  A: "#FFB57A",
  B: "#7AC8FF",
};

const SPEAKER_GLOW: Record<Speaker, string> = {
  A: "rgba(255, 145, 80, 0.55)",
  B: "rgba(90, 175, 255, 0.55)",
};

const SPEAKER_LABEL: Record<Speaker, string> = {
  A: "Rosa",
  B: "Joon",
};

const splitWords = (text: string): string[] =>
  text
    .split(/(\\s+)/)
    .filter((tok) => tok.replace(/\\s+/g, "").length > 0);

type SpeechCaptionProps = {
  text: string;
  speaker: Speaker;
  startSec: number;
  endSec: number;
};

export const SpeechCaption: React.FC<SpeechCaptionProps> = ({text, speaker, startSec, endSec}) => {
  const frame = useCurrentFrame();
  const {fps, height} = useVideoConfig();

  const sceneDuration = Math.max(endSec - startSec, 0.4);
  const words = splitWords(text);
  const perWord = sceneDuration / words.length;

  const localSec = frame / fps;
  const elapsed = Math.max(0, localSec);

  const entrance = spring({
    frame,
    fps,
    config: {damping: 18, stiffness: 160, mass: 0.6},
    durationInFrames: Math.round(fps * 0.45),
  });

  const cardOpacity = interpolate(entrance, [0, 1], [0, 1]);
  const cardTranslate = interpolate(entrance, [0, 1], [40, 0]);

  const accent = SPEAKER_COLOR[speaker];
  const glow = SPEAKER_GLOW[speaker];

  const fontFamily =
    "'Pretendard', 'Apple SD Gothic Neo', 'Noto Sans KR', system-ui, -apple-system, sans-serif";

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: height * 0.09,
      }}
    >
      <div
        style={{
          position: "relative",
          maxWidth: "88%",
          padding: "26px 38px 28px",
          borderRadius: 28,
          background:
            "linear-gradient(180deg, rgba(15,17,25,0.78) 0%, rgba(8,10,18,0.92) 100%)",
          backdropFilter: "blur(14px)",
          WebkitBackdropFilter: "blur(14px)",
          boxShadow: `0 24px 60px rgba(0,0,0,0.55), 0 0 0 1px rgba(255,255,255,0.06) inset`,
          opacity: cardOpacity,
          transform: `translateY(${cardTranslate}px)`,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            marginBottom: 14,
            justifyContent: "center",
          }}
        >
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: "50%",
              backgroundColor: accent,
              boxShadow: `0 0 14px ${glow}`,
            }}
          />
          <div
            style={{
              fontFamily,
              fontSize: 24,
              fontWeight: 700,
              color: accent,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              opacity: 0.9,
            }}
          >
            {SPEAKER_LABEL[speaker]}
          </div>
        </div>

        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "center",
            alignItems: "baseline",
            gap: "0.32em 0.42em",
            fontFamily,
            fontSize: 60,
            fontWeight: 800,
            lineHeight: 1.28,
            letterSpacing: "-0.01em",
            color: "rgba(255,255,255,0.32)",
            textAlign: "center",
          }}
        >
          {words.map((w, i) => {
            const wStart = i * perWord;
            const wEnd = (i + 1) * perWord;
            const inWindow = elapsed >= wStart && elapsed < wEnd + 0.05;
            const past = elapsed >= wEnd;
            const future = elapsed < wStart;

            const popFrameStart = Math.round(wStart * fps);
            const popProgress = spring({
              frame: frame - popFrameStart,
              fps,
              config: {damping: 12, stiffness: 220, mass: 0.5},
              durationInFrames: Math.round(fps * 0.35),
            });
            const scale = inWindow
              ? interpolate(popProgress, [0, 1], [0.85, 1.18])
              : past
              ? 1.0
              : 0.95;

            const color = future
              ? "rgba(255,255,255,0.28)"
              : inWindow
              ? accent
              : "#FFFFFF";

            const textShadow = inWindow
              ? `0 0 20px ${glow}, 0 0 40px ${glow}, 0 2px 4px rgba(0,0,0,0.6)`
              : past
              ? "0 2px 6px rgba(0,0,0,0.55)"
              : "none";

            return (
              <span
                key={i}
                style={{
                  display: "inline-block",
                  color,
                  textShadow,
                  transform: `scale(${scale})`,
                  transformOrigin: "center bottom",
                  fontWeight: inWindow ? 900 : past ? 800 : 700,
                  WebkitTextStroke: past || inWindow ? "1.5px rgba(0,0,0,0.45)" : "none",
                  whiteSpace: "nowrap",
                  willChange: "transform, color",
                }}
              >
                {w}
              </span>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
"""

BLOG_SHORTFORM_TSX = """import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import {CAPTIONS} from "../data/captions";
import {VOICE_FILE, BGM_FILE, BGM_VOLUME, SOURCE_URL, QR_FILE, FPS} from "../data/scenes";
import {SpeechCaption} from "../components/SpeechCaption";

const KenBurnsImg: React.FC<{src: string; durationFrames: number; dir: number}> = ({
  src,
  durationFrames,
  dir,
}) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, durationFrames], [1.0, 1.08], {
    extrapolateRight: "clamp",
  });
  const translateX = interpolate(frame, [0, durationFrames], [0, dir * 1.5], {
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{overflow: "hidden"}}>
      <Img
        src={staticFile(src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale}) translateX(${translateX}%)`,
        }}
      />
    </AbsoluteFill>
  );
};

const LastCutOverlay: React.FC<{url: string; qr: string | null}> = ({url, qr}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 12], [0, 1], {extrapolateRight: "clamp"});
  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-start",
        alignItems: "center",
        paddingTop: "8%",
        opacity,
      }}
    >
      <div
        style={{
          background: "rgba(255,255,255,0.96)",
          padding: 28,
          borderRadius: 24,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 12,
          boxShadow: "0 16px 48px rgba(0,0,0,0.35)",
          maxWidth: "82%",
        }}
      >
        {qr && (
          <Img
            src={staticFile(qr)}
            style={{width: 280, height: 280, borderRadius: 8}}
          />
        )}
        <div
          style={{
            fontSize: 30,
            fontWeight: 800,
            color: "#1a1a1a",
            fontFamily:
              "system-ui, -apple-system, 'Apple SD Gothic Neo', 'Pretendard', sans-serif",
            textAlign: "center",
          }}
        >
          블로그 본문 보러가기
        </div>
        <div
          style={{
            fontSize: 20,
            color: "#555",
            fontFamily: "monospace",
            maxWidth: 540,
            textAlign: "center",
            wordBreak: "break-all",
            lineHeight: 1.35,
          }}
        >
          {url}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const BlogShortform: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: "#000000"}}>
      <Audio src={staticFile(VOICE_FILE)} />
      {BGM_FILE && <Audio src={staticFile(BGM_FILE)} volume={BGM_VOLUME} loop />}
      {CAPTIONS.map((cap, idx) => {
        const startFrame = Math.round(cap.startSec * FPS);
        const nextStartSec = CAPTIONS[idx + 1]?.startSec ?? cap.endSec;
        const endFrame = Math.round(nextStartSec * FPS);
        const duration = Math.max(1, endFrame - startFrame);
        const dir = idx % 2 === 0 ? 1 : -1;
        const isLast = idx === CAPTIONS.length - 1;
        return (
          <Sequence key={idx} from={startFrame} durationInFrames={duration}>
            <KenBurnsImg src={cap.image} durationFrames={duration} dir={dir} />
            {isLast && SOURCE_URL && (
              <LastCutOverlay url={SOURCE_URL} qr={QR_FILE} />
            )}
            <SpeechCaption
              text={cap.text}
              speaker={cap.speaker}
              startSec={cap.startSec}
              endSec={cap.endSec}
            />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
"""

SCENES_TS_TPL = """export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const TOTAL_SEC = {total_sec};
export const TOTAL_FRAMES = Math.round(TOTAL_SEC * FPS);
export const VOICE_FILE = "audio/voice.mp3";
export const BGM_FILE: string | null = {bgm_value};
export const BGM_VOLUME = 0.15;
export const SOURCE_URL: string = {source_url_ts};
export const QR_FILE: string | null = {qr_value};
"""

CAPTIONS_TS_TPL = """export type Caption = {{
  startSec: number;
  endSec: number;
  text: string;
  speaker: "A" | "B";
  image: string;
}};

export const CAPTIONS: Caption[] = {captions};
"""


def main() -> int:
    p = argparse.ArgumentParser(description="Remotion v4 프로젝트 스캐폴드")
    p.add_argument("project_dir")
    args = p.parse_args()

    project = Path(args.project_dir).resolve()
    captions_path = project / "captions.json"
    if not captions_path.exists():
        sys.stderr.write(f"[error] {captions_path} 없음\n")
        return 5

    data = json.loads(captions_path.read_text(encoding="utf-8"))
    total_sec = data["totalSec"]
    captions = data["captions"]

    voice_mp3 = project / "public" / "audio" / "voice.mp3"
    if not voice_mp3.exists():
        sys.stderr.write(f"[error] {voice_mp3} 없음 (Phase 2 미완료)\n")
        return 5
    for cap in captions:
        img = project / "public" / "images" / f"cut_{cap['index']:02d}.png"
        if not img.exists():
            sys.stderr.write(f"[error] {img} 없음 (Phase 2 미완료)\n")
            return 5

    bgm_mp3 = project / "public" / "audio" / "bgm.mp3"
    bgm_value = '"audio/bgm.mp3"' if bgm_mp3.exists() else "null"
    if bgm_mp3.exists():
        sys.stderr.write(f"[bgm] 발견: {bgm_mp3}\n")

    source_url = (data.get("source") or {}).get("url", "")
    source_url_ts = json.dumps(source_url, ensure_ascii=False)

    qr_png = project / "public" / "qr.png"
    qr_value = "null"
    if source_url:
        if requests is None:
            sys.stderr.write("[warn] requests 미설치 — QR 다운로드 생략\n")
        elif qr_png.exists():
            qr_value = '"qr.png"'
            sys.stderr.write(f"[qr] 기존 파일 재사용: {qr_png}\n")
        else:
            try:
                qr_url = (
                    "https://api.qrserver.com/v1/create-qr-code/"
                    f"?size=560x560&format=png&margin=10&data={quote(source_url, safe='')}"
                )
                resp = requests.get(qr_url, timeout=30)
                resp.raise_for_status()
                qr_png.parent.mkdir(parents=True, exist_ok=True)
                qr_png.write_bytes(resp.content)
                qr_value = '"qr.png"'
                sys.stderr.write(f"[qr] 다운로드: {qr_png}\n")
            except Exception as e:
                sys.stderr.write(f"[warn] QR 다운로드 실패: {e}. URL 텍스트만 표시됩니다.\n")

    cap_ts = [
        {
            "startSec": cap["startSec"],
            "endSec": cap["endSec"],
            "text": cap["text"],
            "speaker": cap["speaker"],
            "image": f"images/cut_{cap['index']:02d}.png",
        }
        for cap in captions
    ]
    captions_json = json.dumps(cap_ts, ensure_ascii=False, indent=2)

    (project / "src" / "compositions").mkdir(parents=True, exist_ok=True)
    (project / "src" / "components").mkdir(parents=True, exist_ok=True)
    (project / "src" / "data").mkdir(parents=True, exist_ok=True)
    (project / "out").mkdir(parents=True, exist_ok=True)

    files = {
        "package.json": PACKAGE_JSON,
        "tsconfig.json": TSCONFIG_JSON,
        "remotion.config.ts": REMOTION_CONFIG_TS,
        "src/index.ts": INDEX_TS,
        "src/Root.tsx": ROOT_TSX,
        "src/data/scenes.ts": SCENES_TS_TPL.format(
            total_sec=total_sec,
            bgm_value=bgm_value,
            source_url_ts=source_url_ts,
            qr_value=qr_value,
        ),
        "src/data/captions.ts": CAPTIONS_TS_TPL.format(captions=captions_json),
        "src/components/SpeechCaption.tsx": SPEECH_CAPTION_TSX,
        "src/compositions/BlogShortform.tsx": BLOG_SHORTFORM_TSX,
    }

    for rel, content in files.items():
        target = project / rel
        target.write_text(content, encoding="utf-8")
        sys.stderr.write(f"[write] {rel} ({len(content)} bytes)\n")

    print(
        json.dumps(
            {
                "project_dir": str(project),
                "total_sec": total_sec,
                "total_frames": round(total_sec * 30),
                "captions_count": len(captions),
                "next_steps": [
                    f"cd {project}",
                    "npm install --prefer-offline",
                    "npm run build",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
