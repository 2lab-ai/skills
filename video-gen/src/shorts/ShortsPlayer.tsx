import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
  interpolate,
  OffthreadVideo,
} from "remotion";
import {
  SHORTS_LAYOUT,
  SHORTS_THEMES,
  SHORTS_FONTS,
  ShortsStoryboard,
  ShortsBeat,
  ShortsThemeColors,
  TransitionType,
} from "./ShortsConfig";
import { ShortsVisualArea } from "./ShortsVisualArea";
import { AnimatedCaptions, SimpleAnimatedCaptions } from "./AnimatedCaptions";
import { ShortsProgressBar } from "./ShortsProgressBar";

interface ShortsPlayerProps {
  storyboard: ShortsStoryboard;
  audioFiles?: Record<string, string>; // beatId -> audio filename
}

export const ShortsPlayer: React.FC<ShortsPlayerProps> = ({
  storyboard,
  audioFiles,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const currentTime = frame / fps;

  // Theme resolution
  const theme = SHORTS_THEMES[storyboard.theme || "midnight"];

  // Scale factor for responsive sizing
  const scaleX = width / SHORTS_LAYOUT.width;
  const scaleY = height / SHORTS_LAYOUT.height;
  const scale = Math.min(scaleX, scaleY);

  // Find current and previous beat
  const currentBeatIndex = storyboard.beats.findIndex(
    (b) => currentTime >= b.start_seconds && currentTime < b.end_seconds
  );
  const currentBeat = currentBeatIndex >= 0 ? storyboard.beats[currentBeatIndex] : null;
  const prevBeat = currentBeatIndex > 0 ? storyboard.beats[currentBeatIndex - 1] : null;

  // Total progress
  const totalProgress = currentTime / storyboard.total_duration_seconds;

  // Transition calculations
  const transitionDuration = 0.3; // seconds
  let beatLocalTime = 0;
  let transitionProgress = 1; // 1 = fully entered
  let exitProgress = 0; // 0 = not exiting

  if (currentBeat) {
    beatLocalTime = currentTime - currentBeat.start_seconds;
    const beatDuration = currentBeat.end_seconds - currentBeat.start_seconds;

    // Entry transition
    transitionProgress = interpolate(
      beatLocalTime,
      [0, transitionDuration],
      [0, 1],
      { extrapolateRight: "clamp" }
    );

    // Exit transition (prepare for next beat)
    const timeToEnd = beatDuration - beatLocalTime;
    if (timeToEnd < transitionDuration) {
      exitProgress = interpolate(
        timeToEnd,
        [0, transitionDuration],
        [1, 0],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      );
    }
  }

  const transition = currentBeat?.transition || "fade";

  return (
    <AbsoluteFill
      style={{
        background: buildBackground(theme, currentTime),
        overflow: "hidden",
      }}
    >
      {/* Animated background layers */}
      <BackgroundEffect
        frame={frame}
        fps={fps}
        scale={scale}
        theme={theme}
        currentTime={currentTime}
        beatIndex={currentBeatIndex}
      />

      {/* Background video layer (behind visuals) */}
      {currentBeat?.visual?.video_src && (
        <BeatVideoBackground
          beat={currentBeat}
          frame={frame}
          fps={fps}
          scale={scale}
          theme={theme}
          enterProgress={transitionProgress}
          exitProgress={exitProgress}
        />
      )}

      {/* Visual area with transitions */}
      {currentBeat && (
        <AbsoluteFill
          style={applyTransition(transition, transitionProgress, exitProgress)}
        >
          <ShortsVisualArea
            beat={currentBeat}
            frame={frame - Math.floor(currentBeat.start_seconds * fps)}
            fps={fps}
            scale={scale}
            theme={theme}
          />
        </AbsoluteFill>
      )}

      {/* Captions overlay at bottom */}
      {currentBeat && (
        <>
          {currentBeat.word_timestamps && currentBeat.word_timestamps.length > 0 ? (
            <AnimatedCaptions
              text={currentBeat.caption_text}
              wordTimestamps={currentBeat.word_timestamps}
              currentTime={currentTime}
              beatStartTime={currentBeat.start_seconds}
              scale={scale}
              theme={theme}
            />
          ) : (
            <SimpleAnimatedCaptions
              text={currentBeat.caption_text}
              currentTime={currentTime}
              beatStartTime={currentBeat.start_seconds}
              beatDuration={currentBeat.end_seconds - currentBeat.start_seconds}
              scale={scale}
              theme={theme}
            />
          )}
        </>
      )}

      {/* Progress bar */}
      <ShortsProgressBar progress={totalProgress} scale={scale} theme={theme} />

      {/* Audio tracks per beat */}
      {audioFiles &&
        storyboard.beats.map((beat) => {
          const audioFile = audioFiles[beat.id];
          if (!audioFile) return null;
          const startFrame = Math.floor(beat.start_seconds * fps);
          const durationFrames = Math.ceil(
            (beat.end_seconds - beat.start_seconds) * fps
          );
          return (
            <Sequence
              key={beat.id}
              from={startFrame}
              durationInFrames={durationFrames}
            >
              <Audio src={staticFile(`tts/${audioFile}`)} volume={1} />
            </Sequence>
          );
        })}

      {/* Single voiceover if provided */}
      {storyboard.voiceover_path && (
        <Audio src={staticFile(storyboard.voiceover_path)} volume={1} />
      )}
    </AbsoluteFill>
  );
};

// ── Background builder ──────────────────────────────────
function buildBackground(theme: ShortsThemeColors, time: number): string {
  const shift = Math.sin(time * 0.3) * 5;
  const mid = theme.backgroundGradientMid || theme.backgroundGradientEnd;
  return `linear-gradient(${170 + shift}deg, ${theme.background} 0%, ${mid} 50%, ${theme.backgroundGradientEnd} 100%)`;
}

// ── Transition effects ──────────────────────────────────
function applyTransition(
  type: TransitionType,
  enter: number,
  exit: number
): React.CSSProperties {
  const opacity = interpolate(enter, [0, 1], [0, 1]) * interpolate(exit, [0, 1], [1, 0]);

  switch (type) {
    case "fade":
      return { opacity };

    case "zoom":
      const zoomScale = interpolate(enter, [0, 1], [1.15, 1]) * interpolate(exit, [0, 1], [1, 0.9]);
      return { opacity, transform: `scale(${zoomScale})` };

    case "slide_up":
      const slideY = interpolate(enter, [0, 1], [60, 0]) + interpolate(exit, [0, 1], [0, -60]);
      return { opacity, transform: `translateY(${slideY}px)` };

    case "blur":
      const blur = interpolate(enter, [0, 1], [12, 0]) + interpolate(exit, [0, 1], [0, 12]);
      return { opacity, filter: `blur(${blur}px)` };

    case "glitch":
      const glitchX = (1 - enter) * (Math.random() > 0.5 ? 8 : -8);
      return {
        opacity,
        transform: `translateX(${glitchX}px)`,
        filter: enter < 0.5 ? `hue-rotate(${(1 - enter) * 90}deg)` : "none",
      };

    case "cut":
    default:
      return { opacity: enter > 0.05 ? 1 : 0 };
  }
}

// ── Animated background with themed effects ──────────────
const BackgroundEffect: React.FC<{
  frame: number;
  fps: number;
  scale: number;
  theme: ShortsThemeColors;
  currentTime: number;
  beatIndex: number;
}> = ({ frame, fps, scale, theme, currentTime, beatIndex }) => {
  const time = frame / fps;
  const glowOpacity = 0.4 + Math.sin(time * 0.6) * 0.15;
  const glow2Opacity = 0.2 + Math.sin(time * 0.4 + 2) * 0.1;

  // Glow position shifts with beats
  const glowY = 30 + Math.sin(beatIndex * 1.5 + time * 0.3) * 10;
  const glow2Y = 65 + Math.cos(beatIndex * 0.8 + time * 0.2) * 8;

  return (
    <>
      {/* Primary radial glow */}
      <div
        style={{
          position: "absolute",
          top: `${glowY}%`,
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: 700 * scale,
          height: 700 * scale,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${theme.primary}15 0%, ${theme.primary}08 30%, transparent 70%)`,
          opacity: glowOpacity,
          filter: `blur(${50 * scale}px)`,
        }}
      />

      {/* Secondary accent glow */}
      <div
        style={{
          position: "absolute",
          top: `${glow2Y}%`,
          left: `${40 + Math.sin(time * 0.5) * 15}%`,
          transform: "translate(-50%, -50%)",
          width: 500 * scale,
          height: 500 * scale,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${theme.accent}10 0%, transparent 65%)`,
          opacity: glow2Opacity,
          filter: `blur(${60 * scale}px)`,
        }}
      />

      {/* Subtle noise grain overlay */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: `
            radial-gradient(circle at ${50 + Math.sin(time * 0.7) * 20}% ${30 + Math.cos(time * 0.5) * 15}%, ${theme.primary}04 0%, transparent 50%),
            radial-gradient(circle at ${50 + Math.cos(time * 0.6) * 25}% ${70 + Math.sin(time * 0.4) * 10}%, ${theme.secondary}03 0%, transparent 40%)
          `,
          opacity: 0.8,
        }}
      />

      {/* Subtle horizontal lines */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: `repeating-linear-gradient(
            0deg,
            transparent,
            transparent ${3 * scale}px,
            ${theme.text}01 ${3 * scale}px,
            ${theme.text}01 ${3.5 * scale}px
          )`,
          opacity: 0.3,
        }}
      />
    </>
  );
};

// ── Beat Video Background ──────────────────────────────────
// Renders a background video behind any visual type when video_src is present
const BeatVideoBackground: React.FC<{
  beat: ShortsBeat;
  frame: number;
  fps: number;
  scale: number;
  theme: ShortsThemeColors;
  enterProgress: number;
  exitProgress: number;
}> = ({ beat, frame, fps, scale, theme, enterProgress, exitProgress }) => {
  const videoSrc = beat.visual.video_src ? staticFile(beat.visual.video_src) : null;
  if (!videoSrc) return null;

  const videoOpacity = beat.visual.video_opacity ?? 0.4;
  const videoStart = beat.visual.video_start ?? 0;
  const beatLocalFrame = frame - Math.floor(beat.start_seconds * fps);

  // Fade video in/out with beat transitions
  const fadeIn = interpolate(enterProgress, [0, 1], [0, videoOpacity], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(exitProgress, [0, 1], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const finalOpacity = fadeIn * fadeOut;

  // Subtle slow zoom for cinematic feel
  const zoomProgress = interpolate(beatLocalFrame, [0, fps * 8], [1.0, 1.08], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      {/* Video layer */}
      <OffthreadVideo
        src={videoSrc}
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          minWidth: "100%",
          minHeight: "100%",
          width: "auto",
          height: "auto",
          transform: `translate(-50%, -50%) scale(${zoomProgress})`,
          objectFit: "cover",
          opacity: finalOpacity,
        }}
        startFrom={Math.floor(videoStart * fps)}
        muted
      />

      {/* Top gradient scrim */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: "30%",
          background: `linear-gradient(to bottom, ${theme.background}dd, transparent)`,
          opacity: finalOpacity > 0 ? 1 : 0,
        }}
      />

      {/* Bottom gradient scrim (stronger for caption readability) */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: "40%",
          background: `linear-gradient(to top, ${theme.background}ee, ${theme.background}88, transparent)`,
          opacity: finalOpacity > 0 ? 1 : 0,
        }}
      />

      {/* Vignette overlay */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          boxShadow: `inset 0 0 ${180 * scale}px ${60 * scale}px ${theme.background}80`,
          opacity: finalOpacity > 0 ? 1 : 0,
        }}
      />
    </AbsoluteFill>
  );
};
