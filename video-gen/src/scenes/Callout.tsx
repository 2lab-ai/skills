import React from "react";
import { useCurrentFrame, spring, interpolate, useVideoConfig } from "remotion";
import { Background } from "../components/Background";
import type { CalloutData } from "../types";
import { palette, hexToRgba, getTheme } from "../utils/colors";

interface CalloutProps {
  data: CalloutData;
  accentColor?: string;
  themeName?: string;
}

const VARIANTS: Record<string, { icon: string; color: string; bg: string; border: string }> = {
  info: { icon: "i", color: "#3b82f6", bg: "rgba(59,130,246,0.08)", border: "rgba(59,130,246,0.25)" },
  tip: { icon: "?", color: "#10b981", bg: "rgba(16,185,129,0.08)", border: "rgba(16,185,129,0.25)" },
  warning: { icon: "!", color: "#f59e0b", bg: "rgba(245,158,11,0.08)", border: "rgba(245,158,11,0.25)" },
  danger: { icon: "X", color: "#ef4444", bg: "rgba(239,68,68,0.08)", border: "rgba(239,68,68,0.25)" },
  success: { icon: "O", color: "#10b981", bg: "rgba(16,185,129,0.08)", border: "rgba(16,185,129,0.25)" },
  quote: { icon: '"', color: "#8b5cf6", bg: "rgba(139,92,246,0.08)", border: "rgba(139,92,246,0.25)" },
};

const EMOJIS: Record<string, string> = {
  info: "\u2139\ufe0f",
  tip: "\ud83d\udca1",
  warning: "\u26a0\ufe0f",
  danger: "\ud83d\uded1",
  success: "\u2705",
  quote: "\ud83d\udcac",
};

export const Callout: React.FC<CalloutProps> = ({ data, accentColor, themeName }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName);
  const variant = VARIANTS[data.variant ?? "info"] || VARIANTS.info;
  const emoji = data.emoji ?? EMOJIS[data.variant ?? "info"] ?? EMOJIS.info;
  const color = data.color ?? variant.color;

  const slideS = spring({
    frame: Math.max(0, frame - 8),
    fps,
    config: { damping: 18, stiffness: 80 },
  });
  const translateX = interpolate(slideS, [0, 1], [-60, 0]);
  const opacity = slideS;

  const contentS = spring({
    frame: Math.max(0, frame - 18),
    fps,
    config: { damping: 22, stiffness: 70 },
  });

  return (
    <Background themeName={themeName}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "100%",
          padding: "80px 140px",
        }}
      >
        <div
          style={{
            width: "100%",
            maxWidth: 1200,
            background: variant.bg,
            border: `2px solid ${variant.border}`,
            borderLeft: `6px solid ${color}`,
            borderRadius: 20,
            padding: "60px 70px",
            display: "flex",
            flexDirection: "column",
            gap: 28,
            transform: `translateX(${translateX}px)`,
            opacity,
          }}
        >
          {/* Header with emoji + type badge */}
          <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
            <span style={{ fontSize: 52 }}>{emoji}</span>
            <span
              style={{
                color,
                fontSize: 18,
                fontFamily: theme.fontFamily,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.1em",
                background: hexToRgba(color, 0.15),
                padding: "6px 18px",
                borderRadius: 8,
              }}
            >
              {data.label ?? data.variant ?? "info"}
            </span>
          </div>

          {/* Title */}
          {data.title && (
            <h2
              style={{
                color: theme.textPrimary,
                fontSize: 40,
                fontFamily: theme.headingFont,
                fontWeight: 700,
                margin: 0,
                letterSpacing: "-0.02em",
                opacity: contentS,
              }}
            >
              {data.title}
            </h2>
          )}

          {/* Content */}
          <p
            style={{
              color: theme.textSecondary,
              fontSize: 26,
              fontFamily: theme.fontFamily,
              fontWeight: 400,
              lineHeight: 1.7,
              margin: 0,
              opacity: contentS,
              transform: `translateY(${interpolate(contentS, [0, 1], [10, 0])}px)`,
            }}
          >
            {data.content}
          </p>

          {/* Footer note */}
          {data.footer && (
            <p
              style={{
                color: hexToRgba(theme.textSecondary, 0.6),
                fontSize: 18,
                fontFamily: theme.fontFamily,
                fontStyle: "italic",
                margin: 0,
                marginTop: 8,
                opacity: interpolate(frame, [35, 50], [0, 1], { extrapolateRight: "clamp" }),
              }}
            >
              {data.footer}
            </p>
          )}
        </div>
      </div>
    </Background>
  );
};
