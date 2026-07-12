import React, { useMemo } from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";
import { Background } from "../components/Background";
import { getTheme, bigbrainPalette } from "../utils/colors";
import type { TrainingDataData } from "../types";

interface Props {
  data: TrainingDataData;
  accentColor?: string;
  themeName?: string;
}

/**
 * TrainingData scene — @realbigbrainai style
 *
 * Chaotic scrolling multi-color monospace text representing AI training data.
 * Matrix meets terminal boot sequence. Lines scroll upward continuously with
 * staggered entry, cycling through neon colors on a black background.
 * Optional garble/corruption effect at the end of the scene.
 */
export const TrainingData: React.FC<Props> = ({
  data,
  accentColor,
  themeName,
}) => {
  const frame = useCurrentFrame();
  const { height, durationInFrames } = useVideoConfig();
  const theme = getTheme(themeName || "bigbrain");

  const speed = data.speed ?? 1;
  const bg = data.background ?? "#000000";
  const garble = data.garbleAtEnd ?? false;
  const lines = data.lines;
  const trainingColors = bigbrainPalette.trainingColors;

  // Line height for consistent spacing
  const LINE_HEIGHT = 38;

  // Assign deterministic colors and indents per line
  const processedLines = useMemo(() => {
    return lines.map((line, i) => ({
      text: line.text,
      color: line.color || trainingColors[i % trainingColors.length],
      indent: line.indent ?? Math.floor(Math.abs(Math.sin(i * 73.17) * 6)),
    }));
  }, [lines, trainingColors]);

  // Scroll offset: lines move upward over the duration
  // Speed factor controls how fast lines scroll
  const scrollOffset = frame * speed * 3.5;

  // Fade-in for the whole scene
  const fadeIn = interpolate(frame, [0, 10], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Garble effect: last 20% of frames
  const garbleThreshold = durationInFrames * 0.8;
  const isGarbling = garble && frame > garbleThreshold;
  const garbleProgress = isGarbling
    ? interpolate(
        frame,
        [garbleThreshold, durationInFrames],
        [0, 1],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      )
    : 0;

  // Garble: increasing text-shadow blur
  const garbleBlur = garbleProgress * 12;
  // Garble: increasingly chaotic opacity flicker
  const garbleFlicker =
    isGarbling
      ? 0.7 + Math.sin(frame * 3.7) * garbleProgress * 0.3
      : 1;

  return (
    <Background background={bg}>
      <AbsoluteFill
        style={{
          overflow: "hidden",
          opacity: fadeIn,
        }}
      >
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: 0,
            bottom: 0,
            padding: "0 40px",
          }}
        >
          {processedLines.map((line, i) => {
            // Each line's Y position: starts below viewport, scrolls upward
            const baseY = i * LINE_HEIGHT - scrollOffset + height;

            // Skip lines that are far off-screen for performance
            if (baseY < -LINE_HEIGHT * 2 || baseY > height + LINE_HEIGHT * 2) {
              return null;
            }

            // Stagger: each line fades in slightly after the previous
            const staggerDelay = i * 0.8;
            const lineFrame = Math.max(0, frame - staggerDelay);
            const lineOpacity = interpolate(lineFrame, [0, 6], [0, 1], {
              extrapolateRight: "clamp",
            });

            // Per-line garble offsets (deterministic pseudo-random)
            const garbleOffsetX = isGarbling
              ? Math.sin(frame * 0.7 + i * 17.3) * garbleProgress * 30
              : 0;
            const garbleOffsetY = isGarbling
              ? Math.cos(frame * 0.5 + i * 11.1) * garbleProgress * 8
              : 0;

            // Per-line garble: random character substitution for some lines
            let displayText = line.text;
            if (isGarbling && garbleProgress > 0.4) {
              const corruptionRate = (garbleProgress - 0.4) / 0.6; // 0 to 1 in last 60% of garble zone
              const chars = displayText.split("");
              for (let c = 0; c < chars.length; c++) {
                const corruptSeed = Math.sin(frame * 0.3 + i * 31.7 + c * 7.3);
                if (corruptSeed > 1 - corruptionRate * 0.6) {
                  const glitchChars = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`01";
                  const idx = Math.floor(
                    Math.abs(Math.sin(frame * 0.2 + c * 13.1) * glitchChars.length)
                  ) % glitchChars.length;
                  chars[c] = glitchChars[idx];
                }
              }
              displayText = chars.join("");
            }

            // Garble color shift: some lines shift to random palette colors
            let displayColor = line.color;
            if (isGarbling && garbleProgress > 0.5) {
              const colorShiftSeed = Math.sin(frame * 0.4 + i * 23.7);
              if (colorShiftSeed > 0.3) {
                const shiftIdx =
                  Math.floor(Math.abs(colorShiftSeed * 100)) %
                  trainingColors.length;
                displayColor = trainingColors[shiftIdx];
              }
            }

            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  top: baseY + garbleOffsetY,
                  left: 40 + line.indent * 16 + garbleOffsetX,
                  right: 40,
                  fontSize: 28,
                  fontFamily: theme.monoFont,
                  fontWeight: 400,
                  color: displayColor,
                  opacity: lineOpacity * garbleFlicker,
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  lineHeight: `${LINE_HEIGHT}px`,
                  textShadow: isGarbling
                    ? `0 0 ${garbleBlur}px ${displayColor}, 0 0 ${garbleBlur * 2}px ${displayColor}`
                    : "none",
                  willChange: "transform",
                }}
              >
                {displayText}
              </div>
            );
          })}
        </div>

        {/* Vignette overlay: top and bottom fade to black for cleaner scroll edges */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: 120,
            background:
              "linear-gradient(180deg, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0) 100%)",
            pointerEvents: "none",
            zIndex: 2,
          }}
        />
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            height: 120,
            background:
              "linear-gradient(0deg, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0) 100%)",
            pointerEvents: "none",
            zIndex: 2,
          }}
        />

        {/* Garble: full-screen noise overlay at high corruption */}
        {isGarbling && garbleProgress > 0.7 && (
          <div
            style={{
              position: "absolute",
              inset: 0,
              zIndex: 3,
              background: `rgba(0, 0, 0, ${(garbleProgress - 0.7) * 0.5})`,
              pointerEvents: "none",
            }}
          />
        )}
      </AbsoluteFill>
    </Background>
  );
};
