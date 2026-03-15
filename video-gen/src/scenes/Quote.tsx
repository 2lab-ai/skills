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

  // --- ALL hooks called unconditionally at top level ---
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
  const dividerFade = useFadeIn(25, 20);

  // variant-specific hooks (always called regardless of variant)
  const textFadeLarge = useFadeIn(8, 20);
  const textSlideLarge = useSlideUp(8, 50);
  const typed = useTypewriter(data.quote, 1.2);
  const wordReveal = useWordReveal(data.quote, 4);
  const textFadeDefault = useFadeIn(8, 18);
  const textSlideDefault = useSlideUp(8, 40);

  const cursorBlink = Math.floor(frame / 15) % 2 === 0;

  const baseStyle: React.CSSProperties = {
    color: theme.textPrimary,
    fontFamily: theme.headingFont,
    fontWeight: 600,
    lineHeight: 1.5,
    margin: 0,
    maxWidth: 900,
    textAlign: "center" as const,
  };

  const renderQuoteText = () => {
    switch (variant) {
      case "large":
        return (
          <p
            style={{
              ...baseStyle,
              fontSize: 58,
              fontWeight: 700,
              letterSpacing: "-0.02em",
              opacity: textFadeLarge,
              transform: `translateY(${textSlideLarge}px)`,
            }}
          >
            {data.quote}
          </p>
        );

      case "typewriter":
        return (
          <p
            style={{
              ...baseStyle,
              fontSize: 38,
              fontFamily: theme.monoFont,
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

      case "highlight":
        return (
          <p style={{ ...baseStyle, fontSize: 40 }}>
            {wordReveal.words.map((word, i) => {
              const isVisible = i < wordReveal.visibleCount;
              const isJustRevealed = i === wordReveal.visibleCount - 1;
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

      default:
        return (
          <p
            style={{
              ...baseStyle,
              fontSize: 40,
              fontStyle: "italic",
              opacity: textFadeDefault,
              transform: `translateY(${textSlideDefault}px)`,
            }}
          >
            {data.quote}
          </p>
        );
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
          padding: "0 140px",
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
            fontSize: 140,
            fontFamily: theme.headingFont,
            fontWeight: 800,
            color: accent,
            lineHeight: 0.6,
            opacity: quoteMarkFade * 0.35,
            transform: `translateY(${quoteMarkFloat}px)`,
            textShadow: `0 0 ${40 * glowIntensity}px ${hexToRgba(accent, 0.4)}`,
            userSelect: "none",
            marginBottom: 12,
          }}
        >
          {"\u201C"}
        </div>

        {/* Quote text */}
        {renderQuoteText()}

        {/* Closing quote mark */}
        <div
          style={{
            fontSize: 140,
            fontFamily: theme.headingFont,
            fontWeight: 800,
            color: accent,
            lineHeight: 0.6,
            opacity: quoteMarkFade * 0.35,
            transform: `translateY(${-quoteMarkFloat}px)`,
            textShadow: `0 0 ${40 * glowIntensity}px ${hexToRgba(accent, 0.4)}`,
            userSelect: "none",
            marginTop: 12,
          }}
        >
          {"\u201D"}
        </div>

        {/* Accent divider */}
        <div
          style={{
            width: interpolate(dividerFade, [0, 1], [0, 120]),
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
            fontSize: 24,
            fontFamily: theme.fontFamily,
            fontWeight: 600,
            margin: 0,
            letterSpacing: "0.03em",
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
              fontSize: 18,
              fontFamily: theme.fontFamily,
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
