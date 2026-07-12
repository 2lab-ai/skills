import React from "react";
import { useCurrentFrame, interpolate, useVideoConfig } from "remotion";
import { Background } from "../components/Background";
import type { TypewriterData } from "../types";
import { palette, hexToRgba, getTheme } from "../utils/colors";

interface TypewriterProps {
  data: TypewriterData;
  accentColor?: string;
  themeName?: string;
}

export const Typewriter: React.FC<TypewriterProps> = ({ data, accentColor, themeName }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName);
  const accent = accentColor || theme.accent;

  const speed = data.speed ?? 2; // chars per frame
  const text = data.text;
  const charsVisible = Math.min(Math.floor(frame * speed), text.length);
  const visibleText = text.slice(0, charsVisible);
  const isComplete = charsVisible >= text.length;

  // Cursor blink
  const cursorVisible = isComplete ? Math.floor(frame * 0.06) % 2 === 0 : true;

  // Fade in container
  const containerOpacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" });

  const fontSize = data.fontSize ?? 48;
  const variant = data.variant ?? "default";

  const getFontStyle = () => {
    switch (variant) {
      case "mono":
        return { fontFamily: theme.monoFont || "JetBrains Mono, monospace", fontWeight: 400 };
      case "handwriting":
        return { fontFamily: theme.fontFamily, fontWeight: 300, fontStyle: "italic" as const };
      case "bold":
        return { fontFamily: theme.headingFont, fontWeight: 800 };
      default:
        return { fontFamily: theme.fontFamily, fontWeight: 400 };
    }
  };

  const fontStyle = getFontStyle();

  return (
    <Background themeName={themeName}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: data.align ?? "center",
          justifyContent: "center",
          height: "100%",
          padding: "80px 140px",
          opacity: containerOpacity,
        }}
      >
        {/* Author / label */}
        {data.label && (
          <span
            style={{
              color: accent,
              fontSize: 20,
              fontFamily: theme.fontFamily,
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.12em",
              marginBottom: 30,
              opacity: interpolate(frame, [5, 20], [0, 1], { extrapolateRight: "clamp" }),
            }}
          >
            {data.label}
          </span>
        )}

        {/* Main text */}
        <div
          style={{
            ...fontStyle,
            color: theme.textPrimary,
            fontSize,
            lineHeight: 1.6,
            textAlign: data.align ?? "center",
            maxWidth: 1400,
          }}
        >
          {visibleText}
          <span
            style={{
              display: "inline-block",
              width: variant === "mono" ? "0.6em" : "3px",
              height: "1.1em",
              background: cursorVisible ? accent : "transparent",
              marginLeft: 4,
              verticalAlign: "text-bottom",
              transition: "background 0.1s",
            }}
          />
        </div>

        {/* Attribution */}
        {data.attribution && isComplete && (
          <span
            style={{
              color: theme.textSecondary,
              fontSize: 22,
              fontFamily: theme.fontFamily,
              fontWeight: 400,
              marginTop: 40,
              opacity: interpolate(
                frame,
                [Math.ceil(text.length / speed), Math.ceil(text.length / speed) + 20],
                [0, 1],
                { extrapolateRight: "clamp" }
              ),
            }}
          >
            — {data.attribution}
          </span>
        )}
      </div>
    </Background>
  );
};
