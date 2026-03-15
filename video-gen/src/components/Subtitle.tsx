import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import type { SubtitleCue } from "../types";
import { hexToRgba, palette } from "../utils/colors";

interface SubtitleProps {
  subtitles: SubtitleCue[];
  style?: React.CSSProperties;
}

export const Subtitle: React.FC<SubtitleProps> = ({ subtitles, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTimeMs = (frame / fps) * 1000;

  const currentCue = subtitles.find(
    (cue) => currentTimeMs >= cue.startMs && currentTimeMs <= cue.endMs
  );

  if (!currentCue) return null;

  const cueProgressMs = currentTimeMs - currentCue.startMs;
  const cueDurationMs = currentCue.endMs - currentCue.startMs;

  // Fade in/out
  const fadeIn = interpolate(cueProgressMs, [0, 200], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fadeOut = interpolate(cueProgressMs, [cueDurationMs - 200, cueDurationMs], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const opacity = Math.min(fadeIn, fadeOut);

  return (
    <div
      style={{
        position: "absolute",
        bottom: 80,
        left: "50%",
        transform: "translateX(-50%)",
        zIndex: 100,
        ...style,
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
