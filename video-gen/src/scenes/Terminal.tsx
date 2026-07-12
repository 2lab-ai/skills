import React from "react";
import {
  useCurrentFrame,
  interpolate,
  useVideoConfig,
} from "remotion";
import { Background } from "../components/Background";
import type { TerminalData } from "../types";
import { getTheme, neuralPalette } from "../utils/colors";

interface TerminalProps {
  data: TerminalData;
  accentColor?: string;
  themeName?: string;
}

export const Terminal: React.FC<TerminalProps> = ({
  data,
  accentColor,
  themeName,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName || "neural");
  const accent = accentColor || neuralPalette.orange;

  const speed = data.speed ?? 0.5;
  const cursor = data.cursor ?? "block";

  // Fade in
  const fadeIn = interpolate(frame, [0, 10], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Calculate sequential line typing - each line starts AFTER previous finishes
  let cumulativeFrames = 0;
  const lineStates = data.lines.map((line, i) => {
    const lineDelay = line.delay ?? (i === 0 ? 0 : 8);
    const prompt = line.prompt ?? "> ";
    const fullText = prompt + line.text;
    const totalLineChars = fullText.length;

    // Each line starts after the previous line is fully typed + its delay
    const lineStartFrame = cumulativeFrames + lineDelay;
    const framesNeededForLine = Math.ceil(totalLineChars / speed);

    const effectiveFrame = Math.max(0, frame - lineStartFrame);
    const charsTyped = Math.floor(effectiveFrame * speed);
    const clampedChars = Math.min(charsTyped, totalLineChars);

    // This line's total frames = delay + typing time
    cumulativeFrames = lineStartFrame + framesNeededForLine;

    const displayText = fullText.substring(0, clampedChars);
    const isTyping = clampedChars > 0 && clampedChars < totalLineChars;
    const isDone = clampedChars >= totalLineChars;
    const isActive = frame >= lineStartFrame;

    return {
      ...line,
      displayText,
      isTyping,
      isDone,
      isActive,
      prompt,
      fullText,
      clampedChars,
    };
  });

  // Find which line is currently being typed (for cursor)
  const activeLineIdx = lineStates.findIndex((l) => l.isTyping);
  const cursorLineIdx =
    activeLineIdx >= 0
      ? activeLineIdx
      : lineStates.findIndex((l) => !l.isDone && l.isActive);

  // Cursor blink
  const cursorVisible = Math.floor(frame / 15) % 2 === 0;

  const renderCursor = () => {
    if (!cursorVisible) return null;

    switch (cursor) {
      case "block":
        return (
          <span
            style={{
              background: theme.textPrimary,
              color: neuralPalette.bg,
              padding: "0 2px",
            }}
          >
            {" "}
          </span>
        );
      case "underline":
        return (
          <span
            style={{
              borderBottom: `2px solid ${theme.textPrimary}`,
              paddingBottom: 2,
            }}
          >
            {" "}
          </span>
        );
      case "bar":
        return (
          <span
            style={{
              borderLeft: `2px solid ${theme.textPrimary}`,
              marginLeft: 2,
            }}
          >
            {" "}
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <Background background={neuralPalette.bg}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "flex-start",
          padding: "80px 60px",
          height: "100%",
          fontFamily: theme.monoFont,
          opacity: fadeIn,
          gap: 8,
        }}
      >
        {lineStates.map((line, i) => {
          if (!line.isActive && !line.isDone) return null;

          const lineColor = line.color || theme.textPrimary;
          const showCursor =
            i === cursorLineIdx ||
            (cursorLineIdx === -1 && i === lineStates.length - 1 && line.isDone);

          return (
            <div
              key={i}
              style={{
                fontSize: 36,
                color: lineColor,
                lineHeight: 1.6,
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
              }}
            >
              {line.displayText}
              {showCursor && renderCursor()}
            </div>
          );
        })}
      </div>
    </Background>
  );
};
