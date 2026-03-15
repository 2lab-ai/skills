import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { Background } from "../components/Background";
import type { HeroData } from "../types";
import { palette, hexToRgba, getTheme } from "../utils/colors";

interface HeroProps {
  data: HeroData;
  accentColor?: string;
  themeName?: string;
}

export const Hero: React.FC<HeroProps> = ({ data, accentColor, themeName }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName);
  const accent = accentColor || theme.accent;

  const titleSpring = spring({ frame, fps, config: { damping: 15, stiffness: 80 } });
  const subtitleSpring = spring({ frame: frame - 12, fps, config: { damping: 18, stiffness: 90 } });
  const badgeSpring = spring({ frame: frame - 5, fps, config: { damping: 20, stiffness: 100 } });

  const lineWidth = interpolate(titleSpring, [0, 1], [0, 200]);

  return (
    <Background>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          height: "100%",
          padding: "0 140px",
          textAlign: "center",
        }}
      >
        {/* Badge */}
        {data.badge && (
          <div
            style={{
              opacity: badgeSpring,
              transform: `scale(${interpolate(badgeSpring, [0, 1], [0.8, 1])})`,
              marginBottom: 24,
            }}
          >
            <span
              style={{
                background: hexToRgba(accent, 0.15),
                border: `1px solid ${hexToRgba(accent, 0.3)}`,
                color: accent,
                padding: "8px 24px",
                borderRadius: 100,
                fontSize: 22,
                fontWeight: 600,
                letterSpacing: "0.05em",
                textTransform: "uppercase",
              }}
            >
              {data.badge}
            </span>
          </div>
        )}

        {/* Title */}
        <h1
          style={{
            color: theme.textPrimary,
            fontSize: 76,
            fontFamily: theme.headingFont,
            fontWeight: 800,
            lineHeight: 1.15,
            letterSpacing: "-0.03em",
            margin: 0,
            opacity: titleSpring,
            transform: `translateY(${interpolate(titleSpring, [0, 1], [30, 0])}px)`,
          }}
        >
          {data.title}
        </h1>

        {/* Accent line */}
        <div
          style={{
            width: lineWidth,
            height: 4,
            background: `linear-gradient(90deg, transparent, ${accent}, transparent)`,
            borderRadius: 2,
            margin: "20px 0",
          }}
        />

        {/* Subtitle */}
        {data.subtitle && (
          <p
            style={{
              color: theme.textSecondary,
              fontSize: 28,
              fontFamily: theme.fontFamily,
              fontWeight: 400,
              lineHeight: 1.6,
              margin: 0,
              maxWidth: 800,
              opacity: subtitleSpring,
              transform: `translateY(${interpolate(subtitleSpring, [0, 1], [20, 0])}px)`,
            }}
          >
            {data.subtitle}
          </p>
        )}
      </div>
    </Background>
  );
};
