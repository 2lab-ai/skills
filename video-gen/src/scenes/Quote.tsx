import React from "react";
import {
  useCurrentFrame,
  spring,
  interpolate,
  useVideoConfig,
  Easing,
} from "remotion";
import { Background } from "../components/Background";
import {
  useFadeIn,
  useSlideUp,
  useTypewriter,
  useWordReveal,
  useFloat,
  useGlow,
} from "../utils/animations";
import type { QuoteData } from "../types";
import { palette, hexToRgba, getTheme } from "../utils/colors";

interface QuoteProps {
  data: QuoteData;
  accentColor?: string;
  themeName?: string;
}

export const Quote: React.FC<QuoteProps> = ({ data, accentColor, themeName }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName);
  const accent = accentColor || theme.accent;

  const variant = data.variant ?? "default";

  // --- shared animations ---
  const quoteMarkFade = useFadeIn(0, 20);
  const quoteMarkFloat = useFloat(100, 6);
  const authorSlideUp = useSlideUp(30, 30);
  const authorFade = useFadeIn(30, 15);
  const sourceFade = useFadeIn(40, 15);
  const emojiFade = useFadeIn(0, 12);
  const emojiScale = spring({
    frame,
    fps,
    config: { damping: 8, stiffness: 120, mass: 0.6 },
  });
  const glowIntensity = useGlow(90);

  // --- variant-specific text rendering ---
  const renderQuoteText = () => {
    const baseStyle: React.CSSProperties = {
      color: theme.textPrimary,
      fontWeight: 600,
      lineHeight: 1.5,
      margin: 0,
      maxWidth: 1000,
      textAlign: "center" as const,
    };

    switch (variant) {
      case "large": {
        const textFade = useFadeIn(8, 20);
        const textSlide = useSlideUp(8, 50);
        return (
          <p
            style={{
              ...baseStyle,
              fontSize: 64,
              fontWeight: 700,
              letterSpacing: "-0.02em",
              opacity: textFade,
              transform: `translateY(${textSlide}px)`,
            }}
          >
            {data.quote}
          </p>
        );
      }

      case "typewriter": {
        const typed = useTypewriter(data.quote, 1.2);
        const cursorBlink = Math.floor(frame / 15) % 2 === 0;
        return (
          <p
            style={{
              ...baseStyle,
              fontSize: 42,
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            {typed}
            <span
              style={{
                opacity: cursorBlink ? 1 : 0,
                color: accent,
                fontWeight: 300,
              }}
            >
              |
            </span>
          </p>
        );
      }

      case "highlight": {
        const { words, visibleCount } = useWordReveal(data.quote, 4);
        return (
          <p style={{ ...baseStyle, fontSize: 44 }}>
            {words.map((word, i) => {
              const isVisible = i < visibleCount;
              const isJustRevealed = i === visibleCount - 1;
              return (
                <span key={i}>
                  <span
                    style={{
                      opacity: isVisible ? 1 : 0.15,
                      background: isJustRevealed
                        ? hexToRgba(accent, 0.25)
                        : "transparent",
                      padding: isJustRevealed ? "2px 6px" : "0",
                      borderRadius: 4,
                      transition: "all 0.2s",
                    }}
                  >
                    {word}
                  </span>{" "}
                </span>
              );
            })}
          </p>
        );
      }

      default: {
        // "default" -- centered fade-in
        const textFade = useFadeIn(8, 18);
        const textSlide = useSlideUp(8, 40);
        return (
          <p
            style={{
              ...baseStyle,
              fontSize: 44,
              fontStyle: "italic",
              opacity: textFade,
              transform: `translateY(${textSlide}px)`,
            }}
          >
            {data.quote}
          </p>
        );
      }
    }
  };

  return (
    <Background background={theme.background}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          height: "100%",
          padding: "0 120px",
          textAlign: "center",
          position: "relative",
        }}
      >
        {/* Optional emoji */}
        {data.emoji && (
          <div
            style={{
              fontSize: 72,
              marginBottom: 24,
              opacity: emojiFade,
              transform: `scale(${interpolate(emojiScale, [0, 1], [0.3, 1])})`,
            }}
          >
            {data.emoji}
          </div>
        )}

        {/* Opening quote mark */}
        <div
          style={{
            fontSize: 160,
            fontWeight: 800,
            color: accent,
            lineHeight: 0.6,
            opacity: quoteMarkFade * 0.4,
            transform: `translateY(${quoteMarkFloat}px)`,
            textShadow: `0 0 ${40 * glowIntensity}px ${hexToRgba(accent, 0.4)}`,
            userSelect: "none",
            marginBottom: 16,
          }}
        >
          {"\u201C"}
        </div>

        {/* Quote text */}
        {renderQuoteText()}

        {/* Closing quote mark */}
        <div
          style={{
            fontSize: 160,
            fontWeight: 800,
            color: accent,
            lineHeight: 0.6,
            opacity: quoteMarkFade * 0.4,
            transform: `translateY(${-quoteMarkFloat}px)`,
            textShadow: `0 0 ${40 * glowIntensity}px ${hexToRgba(accent, 0.4)}`,
            userSelect: "none",
            marginTop: 16,
          }}
        >
          {"\u201D"}
        </div>

        {/* Accent divider */}
        <div
          style={{
            width: interpolate(useFadeIn(25, 20), [0, 1], [0, 120]),
            height: 3,
            background: `linear-gradient(90deg, transparent, ${accent}, transparent)`,
            margin: "32px 0",
            borderRadius: 2,
          }}
        />

        {/* Author */}
        <p
          style={{
            color: accent,
            fontSize: 28,
            fontWeight: 700,
            margin: 0,
            letterSpacing: "0.02em",
            opacity: authorFade,
            transform: `translateY(${authorSlideUp}px)`,
          }}
        >
          {"\u2014 "}{data.author}
        </p>

        {/* Source */}
        {data.source && (
          <p
            style={{
              color: theme.textSecondary,
              fontSize: 20,
              fontWeight: 400,
              margin: 0,
              marginTop: 8,
              opacity: sourceFade,
            }}
          >
            {data.source}
          </p>
        )}
      </div>
    </Background>
  );
};
