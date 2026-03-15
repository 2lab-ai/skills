import React from "react";
import { Composition, registerRoot } from "remotion";
import { VideoComposition } from "./VideoComposition";
import type { VideoConfig, TTSMetadata } from "./types";

// These will be loaded from generated files at render time
import configData from "../public/render-config.json";
import ttsMetaData from "../public/tts-metadata.json";

const config = configData as VideoConfig;
const ttsData = ttsMetaData as TTSMetadata[];

// Calculate total duration from TTS data
function calculateTotalFrames(cfg: VideoConfig, tts: TTSMetadata[]): number {
  let totalMs = 0;
  for (const scene of cfg.scenes) {
    const ttsMeta = tts.find((t) => t.sceneId === scene.id);
    const durationMs = ttsMeta?.durationMs ?? (scene.durationInSeconds ?? 5) * 1000;
    totalMs += durationMs + 500; // +500ms padding per scene
  }
  return Math.ceil((totalMs / 1000) * cfg.fps);
}

// ---------------------------------------------------------------------------
// @font-face declarations for all fonts in public/fonts/
// Remotion serves the public/ directory at root, so paths are /fonts/...
// Using font-display: block because video rendering requires fonts to be
// fully loaded before any frame is painted.
// ---------------------------------------------------------------------------
const fontFaceCSS = `
/* ── Pretendard (woff2) ── */
@font-face {
  font-family: 'Pretendard';
  font-weight: 100;
  font-style: normal;
  font-display: block;
  src: url('/fonts/Pretendard-Thin.woff2') format('woff2');
}
@font-face {
  font-family: 'Pretendard';
  font-weight: 200;
  font-style: normal;
  font-display: block;
  src: url('/fonts/Pretendard-ExtraLight.woff2') format('woff2');
}
@font-face {
  font-family: 'Pretendard';
  font-weight: 300;
  font-style: normal;
  font-display: block;
  src: url('/fonts/Pretendard-Light.woff2') format('woff2');
}
@font-face {
  font-family: 'Pretendard';
  font-weight: 400;
  font-style: normal;
  font-display: block;
  src: url('/fonts/Pretendard-Regular.woff2') format('woff2');
}
@font-face {
  font-family: 'Pretendard';
  font-weight: 500;
  font-style: normal;
  font-display: block;
  src: url('/fonts/Pretendard-Medium.woff2') format('woff2');
}
@font-face {
  font-family: 'Pretendard';
  font-weight: 600;
  font-style: normal;
  font-display: block;
  src: url('/fonts/Pretendard-SemiBold.woff2') format('woff2');
}
@font-face {
  font-family: 'Pretendard';
  font-weight: 700;
  font-style: normal;
  font-display: block;
  src: url('/fonts/Pretendard-Bold.woff2') format('woff2');
}
@font-face {
  font-family: 'Pretendard';
  font-weight: 800;
  font-style: normal;
  font-display: block;
  src: url('/fonts/Pretendard-ExtraBold.woff2') format('woff2');
}
@font-face {
  font-family: 'Pretendard';
  font-weight: 900;
  font-style: normal;
  font-display: block;
  src: url('/fonts/Pretendard-Black.woff2') format('woff2');
}

/* ── Inter (woff2) ── */
@font-face {
  font-family: 'Inter';
  font-weight: 400;
  font-style: normal;
  font-display: block;
  src: url('/fonts/Inter-Regular.woff2') format('woff2');
}
@font-face {
  font-family: 'Inter';
  font-weight: 500;
  font-style: normal;
  font-display: block;
  src: url('/fonts/Inter-Medium.woff2') format('woff2');
}
@font-face {
  font-family: 'Inter';
  font-weight: 600;
  font-style: normal;
  font-display: block;
  src: url('/fonts/Inter-SemiBold.woff2') format('woff2');
}
@font-face {
  font-family: 'Inter';
  font-weight: 700;
  font-style: normal;
  font-display: block;
  src: url('/fonts/Inter-Bold.woff2') format('woff2');
}

/* ── JetBrains Mono (woff2) ── */
@font-face {
  font-family: 'JetBrains Mono';
  font-weight: 400;
  font-style: normal;
  font-display: block;
  src: url('/fonts/JetBrainsMono-Regular.woff2') format('woff2');
}
@font-face {
  font-family: 'JetBrains Mono';
  font-weight: 700;
  font-style: normal;
  font-display: block;
  src: url('/fonts/JetBrainsMono-Bold.woff2') format('woff2');
}

/* ── Variable fonts (truetype) ── */
@font-face {
  font-family: 'Noto Sans KR';
  font-weight: 100 900;
  font-style: normal;
  font-display: block;
  src: url('/fonts/NotoSansKR-Variable.ttf') format('truetype');
}
@font-face {
  font-family: 'Noto Serif KR';
  font-weight: 100 900;
  font-style: normal;
  font-display: block;
  src: url('/fonts/NotoSerifKR-Variable.ttf') format('truetype');
}
@font-face {
  font-family: 'Playfair Display';
  font-weight: 100 900;
  font-style: normal;
  font-display: block;
  src: url('/fonts/PlayfairDisplay-Variable.ttf') format('truetype');
}
@font-face {
  font-family: 'Space Grotesk';
  font-weight: 100 900;
  font-style: normal;
  font-display: block;
  src: url('/fonts/SpaceGrotesk-Variable.ttf') format('truetype');
}
@font-face {
  font-family: 'DM Sans';
  font-weight: 100 900;
  font-style: normal;
  font-display: block;
  src: url('/fonts/DMSans-Variable.ttf') format('truetype');
}
@font-face {
  font-family: 'Outfit';
  font-weight: 100 900;
  font-style: normal;
  font-display: block;
  src: url('/fonts/Outfit-Variable.ttf') format('truetype');
}
`;

const RemotionRoot: React.FC = () => {
  const totalFrames = calculateTotalFrames(config, ttsData);

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: fontFaceCSS }} />
      <Composition
        id="VideoComposition"
        component={VideoComposition}
        durationInFrames={totalFrames}
        fps={config.fps}
        width={config.width}
        height={config.height}
        defaultProps={{
          config,
          ttsData,
        }}
      />
    </>
  );
};

registerRoot(RemotionRoot);
