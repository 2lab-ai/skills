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
  usePulse,
  useFloat,
} from "../utils/animations";
import type { EmojiData } from "../types";
import { palette, hexToRgba, getTheme } from "../utils/colors";

interface EmojiProps {
  data: EmojiData;
  accentColor?: string;
  themeName?: string;
}

export const Emoji: React.FC<EmojiProps> = ({ data, accentColor, themeName }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName);
  const accent = accentColor || theme.accent;

  const emojiSize = data.size ?? 240;
  const animateType = data.animate ?? "bounce";

  // Entry animation for the emoji
  const entrySpring = spring({
    frame,
    fps,
    config: { damping: 10, stiffness: 120, mass: 0.7 },
  });
  const entryOpacity = interpolate(entrySpring, [0, 0.4], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Text animations
  const titleFade = useFadeIn(12, 15);
  const titleSlide = useSlideUp(12, 30);
  const subtitleFade = useFadeIn(20, 15);
  const subtitleSlide = useSlideUp(20, 25);

  // Animation-specific values
  const elasticScale = useElasticScale(0);
  const pulseScale = usePulse(50);
  const floatY = useFloat(70, 15);

  // Spin rotation (continuous after entry)
  const spinRotation = interpolate(
    frame,
    [0, 120],
    [0, 360],
    { extrapolateRight: "extend" }
  );
  const spinEntryScale = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  // Compute emoji transform and scale based on animation type
  const getEmojiTransform = (): string => {
    switch (animateType) {
      case "bounce":
        return `scale(${interpolate(elasticScale, [0, 1], [0, 1])})`;
      case "spin":
        return `scale(${spinEntryScale}) rotate(${spinRotation}deg)`;
      case "pulse":
        return `scale(${entrySpring * pulseScale})`;
      case "float":
        return `scale(${entrySpring}) translateY(${floatY * entrySpring}px)`;
      case "none":
      default:
        return `scale(${entrySpring})`;
    }
  };

  // Background glow behind emoji
  const glowPulse = usePulse(80);

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
        {/* Glow behind emoji */}
        <div
          style={{
            position: "absolute",
            width: emojiSize * 1.8,
            height: emojiSize * 1.8,
            borderRadius: "50%",
            background: `radial-gradient(circle, ${hexToRgba(accent, 0.12 * glowPulse)}, transparent 70%)`,
            filter: "blur(40px)",
            opacity: entryOpacity,
          }}
        />

        {/* Subtitle (above) -- only if there is also a title (below) */}
        {data.subtitle && data.title && (
          <p
            style={{
              color: theme.textSecondary,
              fontSize: 28,
              fontWeight: 500,
              margin: 0,
              marginBottom: 24,
              opacity: subtitleFade,
              transform: `translateY(${-subtitleSlide}px)`,
              letterSpacing: "0.02em",
            }}
          >
            {data.subtitle}
          </p>
        )}

        {/* The emoji */}
        <div
          style={{
            fontSize: emojiSize,
            lineHeight: 1,
            opacity: entryOpacity,
            transform: getEmojiTransform(),
            zIndex: 1,
            filter:
              animateType === "bounce"
                ? `drop-shadow(0 ${8 * entrySpring}px ${20 * entrySpring}px ${hexToRgba("#000", 0.3)})`
                : undefined,
          }}
        >
          {data.emoji}
        </div>

        {/* Title (below) */}
        {data.title && (
          <h2
            style={{
              color: theme.textPrimary,
              fontSize: 48,
              fontWeight: 700,
              margin: 0,
              marginTop: 32,
              opacity: titleFade,
              transform: `translateY(${titleSlide}px)`,
              letterSpacing: "-0.02em",
            }}
          >
            {data.title}
          </h2>
        )}

        {/* Subtitle (below) -- when there is no title, subtitle goes below */}
        {data.subtitle && !data.title && (
          <p
            style={{
              color: theme.textSecondary,
              fontSize: 30,
              fontWeight: 500,
              margin: 0,
              marginTop: 24,
              opacity: subtitleFade,
              transform: `translateY(${subtitleSlide}px)`,
            }}
          >
            {data.subtitle}
          </p>
        )}
      </div>
    </Background>
  );
};
