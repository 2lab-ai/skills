import React from "react";
import { interpolate, useVideoConfig } from "remotion";
import { SHORTS_COLORS, SHORTS_FONTS, WordTimestamp, ShortsThemeColors, SHORTS_THEMES } from "./ShortsConfig";

interface AnimatedCaptionsProps {
  text: string;
  wordTimestamps: WordTimestamp[];
  currentTime: number;
  beatStartTime: number;
  scale: number;
  theme?: ShortsThemeColors;
}

const WORDS_PER_CHUNK = 3;

export const AnimatedCaptions: React.FC<AnimatedCaptionsProps> = ({
  text,
  wordTimestamps,
  currentTime,
  beatStartTime,
  scale,
  theme: themeProp,
}) => {
  const theme = themeProp || SHORTS_THEMES.midnight;
  const { fps } = useVideoConfig();

  // Find current word index
  let currentWordIndex = -1;
  for (let i = 0; i < wordTimestamps.length; i++) {
    if (
      currentTime >= wordTimestamps[i].start_seconds &&
      currentTime < wordTimestamps[i].end_seconds
    ) {
      currentWordIndex = i;
      break;
    }
  }

  // If no word active, find closest future word
  if (currentWordIndex === -1) {
    for (let i = 0; i < wordTimestamps.length; i++) {
      if (currentTime < wordTimestamps[i].start_seconds) {
        currentWordIndex = Math.max(0, i - 1);
        break;
      }
    }
    if (currentWordIndex === -1) {
      currentWordIndex = wordTimestamps.length - 1;
    }
  }

  // Determine which chunk to display (3 words at a time)
  const chunkIndex = Math.floor(currentWordIndex / WORDS_PER_CHUNK);
  const chunkStart = chunkIndex * WORDS_PER_CHUNK;
  const chunkEnd = Math.min(chunkStart + WORDS_PER_CHUNK, wordTimestamps.length);
  const visibleWords = wordTimestamps.slice(chunkStart, chunkEnd);

  // Fade in
  const beatLocalTime = currentTime - beatStartTime;
  const fadeIn = interpolate(beatLocalTime, [0, 0.15], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        right: 0,
        height: 280 * scale,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        opacity: fadeIn,
        background: `linear-gradient(transparent 0%, rgba(0,0,0,0.5) 25%, rgba(0,0,0,0.8) 100%)`,
        padding: `${12 * scale}px ${30 * scale}px`,
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          gap: 28 * scale,
          alignItems: "center",
          justifyContent: "center",
          flexWrap: "wrap",
        }}
      >
        {visibleWords.map((wt, i) => {
          const globalIndex = chunkStart + i;
          const isActive = globalIndex === currentWordIndex;
          const isPast = globalIndex < currentWordIndex;

          return (
            <CaptionWord
              key={`${chunkIndex}-${i}`}
              word={wt.word}
              isActive={isActive}
              isPast={isPast}
              isFuture={!isActive && !isPast}
              scale={scale}
              fps={fps}
              theme={theme}
            />
          );
        })}
      </div>
    </div>
  );
};

interface CaptionWordProps {
  word: string;
  isActive: boolean;
  isPast: boolean;
  isFuture: boolean;
  scale: number;
  fps: number;
  theme: ShortsThemeColors;
}

const CaptionWord: React.FC<CaptionWordProps> = ({
  word,
  isActive,
  isPast,
  isFuture,
  scale,
  theme,
}) => {
  const color = isActive
    ? theme.primary
    : isPast
    ? theme.text
    : theme.textMuted;

  const fontWeight = isActive ? 800 : isPast ? 600 : 500;
  const transform = isActive ? "scale(1.15)" : "scale(1.0)";
  const textShadow = isActive
    ? `0 0 24px ${theme.primary}, 0 0 48px ${theme.primary}30`
    : isPast
    ? `0 2px 8px rgba(0,0,0,0.5)`
    : "none";

  return (
    <span
      style={{
        fontFamily: SHORTS_FONTS.heading,
        fontSize: 40 * scale,
        fontWeight,
        color,
        textTransform: "uppercase",
        letterSpacing: "0.04em",
        transform,
        textShadow,
        whiteSpace: "nowrap",
      }}
    >
      {word}
    </span>
  );
};

// Simple fallback: typewriter style captions (when no word timestamps)
export const SimpleAnimatedCaptions: React.FC<{
  text: string;
  currentTime: number;
  beatStartTime: number;
  beatDuration: number;
  scale: number;
  theme?: ShortsThemeColors;
}> = ({ text, currentTime, beatStartTime, beatDuration, scale, theme: themeProp }) => {
  const theme = themeProp || SHORTS_THEMES.midnight;
  const elapsed = currentTime - beatStartTime;
  const progress = Math.min(elapsed / (beatDuration * 0.5), 1);
  const charsToShow = Math.floor(progress * text.length);
  const visibleText = text.substring(0, charsToShow);

  const fadeIn = interpolate(elapsed, [0, 0.15], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        right: 0,
        height: 280 * scale,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: `linear-gradient(transparent 0%, rgba(0,0,0,0.5) 25%, rgba(0,0,0,0.8) 100%)`,
        padding: `${16 * scale}px ${40 * scale}px`,
        opacity: fadeIn,
      }}
    >
      <div
        style={{
          fontFamily: SHORTS_FONTS.heading,
          fontSize: 36 * scale,
          fontWeight: 700,
          color: theme.text,
          textAlign: "center",
          maxWidth: 900 * scale,
          lineHeight: 1.45,
          textShadow: "0 2px 10px rgba(0,0,0,0.7)",
        }}
      >
        {visibleText}
        {progress < 1 && (
          <span
            style={{
              display: "inline-block",
              width: 3 * scale,
              height: 34 * scale,
              backgroundColor: theme.primary,
              marginLeft: 4 * scale,
              opacity: Math.sin(elapsed * 6) > 0 ? 1 : 0,
              verticalAlign: "middle",
            }}
          />
        )}
      </div>
    </div>
  );
};
