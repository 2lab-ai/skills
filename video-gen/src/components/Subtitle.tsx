import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import type { SubtitleCue } from "../types";
import { hexToRgba, palette } from "../utils/colors";

type SubtitleStyle = "box" | "stroke" | "minimal";

interface SubtitleProps {
  subtitles: SubtitleCue[];
  style?: React.CSSProperties;
  variant?: SubtitleStyle;
}

export const Subtitle: React.FC<SubtitleProps> = ({
  subtitles,
  style: customStyle,
  variant = "stroke",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTimeMs = (frame / fps) * 1000;

  const currentCue = subtitles.find(
    (cue) => currentTimeMs >= cue.startMs && currentTimeMs <= cue.endMs,
  );

  if (!currentCue) return null;

  const cueProgressMs = currentTimeMs - currentCue.startMs;
  const cueDurationMs = currentCue.endMs - currentCue.startMs;

  // Spring entrance for each new cue
  const cueFrame = Math.floor((cueProgressMs / 1000) * fps);
  const enterSpring = spring({
    frame: cueFrame,
    fps,
    config: { damping: 200, stiffness: 400 },
    durationInFrames: 8,
  });

  // Fade out near end
  const fadeOut = interpolate(cueProgressMs, [cueDurationMs - 200, cueDurationMs], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const opacity = Math.min(enterSpring, fadeOut);
  const scale = interpolate(enterSpring, [0, 1], [0.85, 1]);
  const translateY = interpolate(enterSpring, [0, 1], [15, 0]);

  if (variant === "stroke") {
    return (
      <div
        style={{
          position: "absolute",
          bottom: 80,
          left: "50%",
          transform: `translateX(-50%) translateY(${translateY}px) scale(${scale})`,
          zIndex: 100,
          opacity,
          maxWidth: 1400,
          textAlign: "center",
          ...customStyle,
        }}
      >
        {/* Layer 1: Stroke (behind) */}
        <div style={{ position: "relative" }}>
          <span
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              color: "transparent",
              fontSize: 44,
              fontWeight: 800,
              lineHeight: 1.4,
              letterSpacing: "-0.02em",
              WebkitTextStroke: "12px rgba(0,0,0,0.9)",
              paintOrder: "stroke fill",
            }}
          >
            {currentCue.text}
          </span>

          {/* Layer 2: Fill (front) */}
          <span
            style={{
              position: "relative",
              color: palette.white,
              fontSize: 44,
              fontWeight: 800,
              lineHeight: 1.4,
              letterSpacing: "-0.02em",
              textShadow: "0 2px 8px rgba(0,0,0,0.5)",
            }}
          >
            {currentCue.text}
          </span>
        </div>
      </div>
    );
  }

  if (variant === "minimal") {
    return (
      <div
        style={{
          position: "absolute",
          bottom: 80,
          left: "50%",
          transform: `translateX(-50%) translateY(${translateY}px)`,
          zIndex: 100,
          opacity,
          maxWidth: 1200,
          textAlign: "center",
          ...customStyle,
        }}
      >
        <span
          style={{
            color: palette.white,
            fontSize: 36,
            fontWeight: 600,
            lineHeight: 1.5,
            letterSpacing: "-0.01em",
            textShadow: "0 2px 20px rgba(0,0,0,0.8), 0 0 40px rgba(0,0,0,0.5)",
          }}
        >
          {currentCue.text}
        </span>
      </div>
    );
  }

  // variant === "box" (original style)
  return (
    <div
      style={{
        position: "absolute",
        bottom: 80,
        left: "50%",
        transform: `translateX(-50%) translateY(${translateY}px)`,
        zIndex: 100,
        ...customStyle,
      }}
    >
      <div
        style={{
          background: hexToRgba("#000000", 0.75),
          backdropFilter: "blur(12px)",
          padding: "14px 32px",
          borderRadius: 12,
          opacity,
          maxWidth: 1200,
          textAlign: "center",
        }}
      >
        <span
          style={{
            color: palette.white,
            fontSize: 32,
            fontWeight: 500,
            lineHeight: 1.5,
            letterSpacing: "-0.02em",
          }}
        >
          {currentCue.text}
        </span>
      </div>
    </div>
  );
};
