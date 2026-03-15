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

const RemotionRoot: React.FC = () => {
  const totalFrames = calculateTotalFrames(config, ttsData);

  return (
    <>
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
