import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
} from "remotion";
import {
  Hero, List, Grid, Code, Flow, Chat, Stat,
  Quote, Timeline, Comparison, Emoji, ImageScene, BigText,
} from "./scenes";
import { Subtitle } from "./components/Subtitle";
import type {
  VideoConfig,
  SceneConfig,
  TTSMetadata,
  HeroData,
  ListData,
  GridData,
  CodeData,
  FlowData,
  ChatData,
  StatData,
  QuoteData,
  TimelineData,
  ComparisonData,
  EmojiData,
  ImageData,
  BigTextData,
  SubtitleCue,
} from "./types";

interface CompositionProps {
  config: VideoConfig;
  ttsData: TTSMetadata[];
}

function renderScene(scene: SceneConfig, accentColor: string, globalTheme?: string) {
  const themeName = scene.theme || globalTheme;
  const props = { accentColor, themeName };

  switch (scene.type) {
    case "hero":
      return <Hero data={scene.data as unknown as HeroData} {...props} />;
    case "list":
      return <List data={scene.data as unknown as ListData} {...props} />;
    case "grid":
      return <Grid data={scene.data as unknown as GridData} {...props} />;
    case "code":
      return <Code data={scene.data as unknown as CodeData} {...props} />;
    case "flow":
      return <Flow data={scene.data as unknown as FlowData} {...props} />;
    case "chat":
      return <Chat data={scene.data as unknown as ChatData} {...props} />;
    case "stat":
      return <Stat data={scene.data as unknown as StatData} {...props} />;
    case "quote":
      return <Quote data={scene.data as unknown as QuoteData} {...props} />;
    case "timeline":
      return <Timeline data={scene.data as unknown as TimelineData} {...props} />;
    case "comparison":
      return <Comparison data={scene.data as unknown as ComparisonData} {...props} />;
    case "emoji":
      return <Emoji data={scene.data as unknown as EmojiData} {...props} />;
    case "image":
      return <ImageScene data={scene.data as unknown as ImageData} {...props} />;
    case "bigtext":
      return <BigText data={scene.data as unknown as BigTextData} {...props} />;
    default:
      return (
        <AbsoluteFill
          style={{
            background: "#0f0f23",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "white",
            fontSize: 40,
          }}
        >
          Unknown scene type: {scene.type}
        </AbsoluteFill>
      );
  }
}

// Scene wrapper that handles entrance + exit animations
const SceneWrapper: React.FC<{
  scene: SceneConfig;
  durationFrames: number;
  children: React.ReactNode;
}> = ({ scene, durationFrames, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const exitType = scene.exit || "none";
  const exitDuration = 12; // frames

  // Exit animation
  let exitOpacity = 1;
  let exitTransform = "none";
  let exitFilter = "none";

  if (exitType !== "none") {
    const exitStart = durationFrames - exitDuration;
    const progress = interpolate(frame, [exitStart, durationFrames], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

    switch (exitType) {
      case "fadeOut":
        exitOpacity = 1 - progress;
        break;
      case "blurOut":
        exitOpacity = 1 - progress * 0.5;
        exitFilter = `blur(${progress * 25}px)`;
        break;
      case "zoomOut":
        exitOpacity = 1 - progress;
        exitTransform = `scale(${1 + progress * 0.2})`;
        break;
      case "slideOutLeft":
        exitOpacity = 1 - progress;
        exitTransform = `translateX(${-progress * 100}px)`;
        break;
      case "slideOutUp":
        exitOpacity = 1 - progress;
        exitTransform = `translateY(${-progress * 60}px)`;
        break;
    }
  }

  return (
    <AbsoluteFill
      style={{
        opacity: exitOpacity,
        transform: exitTransform,
        filter: exitFilter,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};

export const VideoComposition: React.FC<CompositionProps> = ({ config, ttsData }) => {
  const { fps } = useVideoConfig();

  // Calculate frame offsets for each scene
  let currentFrame = 0;
  const sceneLayouts: Array<{
    scene: SceneConfig;
    tts: TTSMetadata | undefined;
    startFrame: number;
    durationFrames: number;
    subtitles: SubtitleCue[];
  }> = [];

  for (const scene of config.scenes) {
    const tts = ttsData.find((t) => t.sceneId === scene.id);
    const durationMs = tts?.durationMs ?? (scene.durationInSeconds ?? 5) * 1000;
    // Add 500ms padding after each scene for breathing room
    const totalMs = durationMs + 500;
    const durationFrames = Math.ceil((totalMs / 1000) * fps);

    sceneLayouts.push({
      scene,
      tts,
      startFrame: currentFrame,
      durationFrames,
      subtitles: tts?.subtitles ?? [],
    });

    currentFrame += durationFrames;
  }

  const accentColor = config.defaultStyle.accentColor;
  const globalTheme = config.theme;
  const subtitleVariant = config.subtitleVariant || "stroke";

  return (
    <AbsoluteFill>
      {sceneLayouts.map((layout) => (
        <Sequence
          key={layout.scene.id}
          from={layout.startFrame}
          durationInFrames={layout.durationFrames}
          name={`${layout.scene.type}: ${layout.scene.id}`}
        >
          <SceneWrapper
            scene={layout.scene}
            durationFrames={layout.durationFrames}
          >
            {renderScene(
              layout.scene,
              layout.scene.style?.accentColor ?? accentColor,
              globalTheme,
            )}
          </SceneWrapper>

          {/* Audio */}
          {layout.tts && (
            <Audio src={staticFile(`tts/${layout.tts.audioFile}`)} />
          )}

          {/* Subtitles */}
          {layout.subtitles.length > 0 && (
            <Subtitle subtitles={layout.subtitles} variant={subtitleVariant} />
          )}
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
