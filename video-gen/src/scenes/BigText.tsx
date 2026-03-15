import React from "react";
import {
  useCurrentFrame,
  spring,
  interpolate,
  useVideoConfig,
} from "remotion";
import { Background } from "../components/Background";
import {
  useFadeIn,
  useSlideUp,
  useElasticScale,
  useShake,
  useGlow,
  usePulse,
} from "../utils/animations";
import type { BigTextData } from "../types";
import { palette, hexToRgba, getTheme } from "../utils/colors";

interface BigTextProps {
  data: BigTextData;
  accentColor?: string;
  themeName?: string;
}

export const BigText: React.FC<BigTextProps> = ({
  data,
  accentColor,
  themeName,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName);
  const accent = accentColor || theme.accent;

  const variant = data.variant ?? "impact";

  // Entry animation
  const entrySpring = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 80 },
  });
  const entryOpacity = interpolate(entrySpring, [0, 0.5], [0, 1], {
    extrapolateRight: "clamp",
  });
  const entryScale = interpolate(entrySpring, [0, 1], [0.85, 1]);

  // Emoji animations
  const emojiFade = useFadeIn(0, 12);
  const emojiScale = useElasticScale(0);

  // Subtitle animations
  const subtitleFade = useFadeIn(15, 15);
  const subtitleSlide = useSlideUp(15, 25);

  // Glow for certain variants
  const glowIntensity = useGlow(80);

  // Variant-specific hooks (always called unconditionally)
  const gradientPulse = usePulse(100);
  const outlineSpring = spring({
    frame: Math.max(0, frame - 5),
    fps,
    config: { damping: 15, stiffness: 70 },
  });
  const outlineStrokeWidth = interpolate(outlineSpring, [0, 1], [0, 3]);

  // Base text styles shared across variants
  const baseTextStyle: React.CSSProperties = {
    fontFamily: theme.headingFont,
    fontSize: 110,
    fontWeight: 900,
    lineHeight: 1.05,
    letterSpacing: "-0.04em",
    margin: 0,
    textAlign: "center",
    maxWidth: 1060,
    textTransform: "uppercase",
  };

  const renderText = () => {
    switch (variant) {
      // -----------------------------------------------------------
      // IMPACT: Bold white text, clean fade-in with scale
      // -----------------------------------------------------------
      case "impact": {
        return (
          <h1
            style={{
              ...baseTextStyle,
              color: theme.textPrimary,
              opacity: entryOpacity,
              transform: `scale(${entryScale})`,
              textShadow: `0 4px 40px ${hexToRgba("#000", 0.5)}`,
            }}
          >
            {data.text}
          </h1>
        );
      }

      // -----------------------------------------------------------
      // GRADIENT: Text filled with a colorful gradient
      // -----------------------------------------------------------
      case "gradient": {
        return (
          <h1
            style={{
              ...baseTextStyle,
              background: `linear-gradient(135deg, ${accent}, ${theme.accentAlt}, ${accent})`,
              backgroundSize: "200% 200%",
              backgroundPosition: `${50 + Math.sin(frame / 40) * 30}% ${50 + Math.cos(frame / 50) * 30}%`,
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
              opacity: entryOpacity,
              transform: `scale(${entryScale * gradientPulse})`,
              filter: `drop-shadow(0 0 ${20 * glowIntensity}px ${hexToRgba(accent, 0.3)})`,
            }}
          >
            {data.text}
          </h1>
        );
      }

      // -----------------------------------------------------------
      // OUTLINE: Stroke-only text, no fill
      // -----------------------------------------------------------
      case "outline": {
        return (
          <h1
            style={{
              ...baseTextStyle,
              color: "transparent",
              WebkitTextStroke: `${outlineStrokeWidth}px ${accent}`,
              opacity: entryOpacity,
              transform: `scale(${entryScale})`,
              filter: `drop-shadow(0 0 ${15 * glowIntensity}px ${hexToRgba(accent, 0.25)})`,
            }}
          >
            {data.text}
          </h1>
        );
      }

      // -----------------------------------------------------------
      // GLITCH: Multi-layered offset text with color channels
      // -----------------------------------------------------------
      case "glitch": {
        // Glitch offset that flickers (deterministic based on frame)
        const glitchCycle = Math.floor(frame / 4) % 8;
        const isGlitching = glitchCycle < 2;

        // Deterministic pseudo-random based on frame for consistent render
        const seed = Math.sin(frame * 0.73) * 43758.5453;
        const detOffsetX = isGlitching ? ((seed % 6) - 3) : 0;
        const detOffsetY = isGlitching ? (((seed * 1.3) % 4) - 2) : 0;

        return (
          <div style={{ position: "relative", opacity: entryOpacity, transform: `scale(${entryScale})` }}>
            {/* Red channel layer (offset) */}
            <h1
              style={{
                ...baseTextStyle,
                color: hexToRgba("#ff0040", 0.7),
                position: "absolute",
                left: -3 + detOffsetX,
                top: detOffsetY,
                zIndex: 1,
                mixBlendMode: "screen",
              }}
            >
              {data.text}
            </h1>

            {/* Cyan channel layer (offset opposite) */}
            <h1
              style={{
                ...baseTextStyle,
                color: hexToRgba("#00ffff", 0.7),
                position: "absolute",
                left: 3 - detOffsetX,
                top: -detOffsetY,
                zIndex: 1,
                mixBlendMode: "screen",
              }}
            >
              {data.text}
            </h1>

            {/* Main white text layer */}
            <h1
              style={{
                ...baseTextStyle,
                color: theme.textPrimary,
                position: "relative",
                zIndex: 2,
                textShadow: isGlitching
                  ? `${detOffsetX}px ${detOffsetY}px 0 ${hexToRgba("#ff0040", 0.5)}, ${-detOffsetX}px ${-detOffsetY}px 0 ${hexToRgba("#00ffff", 0.5)}`
                  : "none",
              }}
            >
              {data.text}
            </h1>

            {/* Scan line overlay during glitch */}
            {isGlitching && (
              <div
                style={{
                  position: "absolute",
                  inset: -20,
                  background: `repeating-linear-gradient(0deg, transparent, transparent 3px, ${hexToRgba("#000", 0.08)} 3px, ${hexToRgba("#000", 0.08)} 4px)`,
                  zIndex: 3,
                  pointerEvents: "none",
                }}
              />
            )}
          </div>
        );
      }

      default:
        return (
          <h1
            style={{
              ...baseTextStyle,
              color: theme.textPrimary,
              opacity: entryOpacity,
              transform: `scale(${entryScale})`,
            }}
          >
            {data.text}
          </h1>
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
          padding: "0 80px",
          textAlign: "center",
          position: "relative",
        }}
      >
        {/* Background glow for gradient/outline variants */}
        {(variant === "gradient" || variant === "outline") && (
          <div
            style={{
              position: "absolute",
              width: 600,
              height: 600,
              borderRadius: "50%",
              background: `radial-gradient(circle, ${hexToRgba(accent, 0.08 * glowIntensity)}, transparent 70%)`,
              filter: "blur(60px)",
              opacity: entryOpacity,
            }}
          />
        )}

        {/* Optional emoji above */}
        {data.emoji && (
          <div
            style={{
              fontSize: 72,
              marginBottom: 20,
              opacity: emojiFade,
              transform: `scale(${interpolate(emojiScale, [0, 1], [0, 1])})`,
              zIndex: 1,
            }}
          >
            {data.emoji}
          </div>
        )}

        {/* Main text */}
        <div style={{ zIndex: 1 }}>{renderText()}</div>

        {/* Optional subtitle */}
        {data.subtitle && (
          <p
            style={{
              color: theme.textSecondary,
              fontFamily: theme.fontFamily,
              fontSize: 28,
              fontWeight: 500,
              margin: 0,
              marginTop: 24,
              opacity: subtitleFade,
              transform: `translateY(${subtitleSlide}px)`,
              letterSpacing: "0.01em",
              zIndex: 1,
            }}
          >
            {data.subtitle}
          </p>
        )}
      </div>
    </Background>
  );
};
