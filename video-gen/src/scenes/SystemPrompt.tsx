import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
import { Background } from "../components/Background";
import { getTheme } from "../utils/colors";
import type { SystemPromptData } from "../types";

interface Props {
  data: SystemPromptData;
  accentColor?: string;
  themeName?: string;
}

export const SystemPrompt: React.FC<Props> = ({
  data,
  accentColor,
  themeName,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName || "bigbrain");

  const prefix = data.prefix ?? ">>";
  const textColor = data.textColor ?? "#d4a050";
  const prefixColor = data.textColor
    ? `${data.textColor}99`
    : "#a07030";
  const bg = data.background ?? "#1a0c0c";
  const flipLastLine = data.flipLastLine ?? false;

  // Overall container fade-in
  const containerOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Stagger interval: ~1 second between each line reveal
  const staggerFrames = Math.round(fps * 1);

  return (
    <Background background={bg} themeName={themeName}>
      <AbsoluteFill
        style={{
          opacity: containerOpacity,
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            paddingLeft: 80,
            paddingRight: 80,
            height: "100%",
            fontFamily: theme.monoFont,
            gap: 4,
          }}
        >
          {data.lines.map((line, i) => {
            const lineDelay = i * staggerFrames;
            const isLastLine = i === data.lines.length - 1;

            // Spring for this line's entrance
            const lineSpring = spring({
              frame: Math.max(0, frame - lineDelay),
              fps,
              config: {
                damping: 18,
                stiffness: 80,
                mass: 0.8,
              },
            });

            // Only render once the line's delay has passed
            if (frame < lineDelay) return null;

            // Opacity: fade in from 0 to 1
            const opacity = interpolate(lineSpring, [0, 1], [0, 1]);

            // Slide from left: starts 30px to the left, settles at 0
            const translateX = interpolate(lineSpring, [0, 1], [-30, 0]);

            // Flip effect for last line (after it has fully appeared)
            const flipDelay = lineDelay + Math.round(fps * 0.8);
            const shouldFlip = flipLastLine && isLastLine && frame >= flipDelay;
            const flipProgress = shouldFlip
              ? spring({
                  frame: frame - flipDelay,
                  fps,
                  config: {
                    damping: 14,
                    stiffness: 120,
                  },
                })
              : 0;
            const scaleY = shouldFlip
              ? interpolate(flipProgress, [0, 1], [1, -1])
              : 1;

            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "baseline",
                  gap: 12,
                  opacity,
                  transform: `translateX(${translateX}px) scaleY(${scaleY})`,
                  transformOrigin: "left center",
                  lineHeight: 1.8,
                }}
              >
                {/* Prefix */}
                <span
                  style={{
                    color: prefixColor,
                    fontSize: 28,
                    fontWeight: 700,
                    flexShrink: 0,
                    userSelect: "none",
                  }}
                >
                  {prefix}
                </span>

                {/* Line text */}
                <span
                  style={{
                    color: textColor,
                    fontSize: 30,
                    fontWeight: 500,
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                  }}
                >
                  {line}
                </span>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </Background>
  );
};
