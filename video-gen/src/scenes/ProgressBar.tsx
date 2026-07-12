import React from "react";
import {
  useCurrentFrame,
  spring,
  interpolate,
  useVideoConfig,
} from "remotion";
import { Background } from "../components/Background";
import type { ProgressBarData } from "../types";
import { getTheme, hexToRgba, neuralPalette } from "../utils/colors";

interface ProgressBarProps {
  data: ProgressBarData;
  accentColor?: string;
  themeName?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  data,
  accentColor,
  themeName,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName || "neural");
  const accent = accentColor || neuralPalette.orange;

  const shouldAnimate = data.animate !== false;

  // Fill animation
  const fillSpring = spring({
    frame,
    fps,
    config: { damping: 30, stiffness: 40 },
  });
  const fillPercent = shouldAnimate
    ? interpolate(fillSpring, [0, 1], [0, data.percent])
    : data.percent;

  // Fade in
  const fadeIn = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Number counter
  const displayPercent = Math.round(fillPercent);

  // Big text animation
  const bigTextSpring = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 80 },
  });
  const bigTextScale = interpolate(bigTextSpring, [0, 1], [0.8, 1]);
  const bigTextOpacity = interpolate(bigTextSpring, [0, 0.5], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Label fade
  const labelFade = interpolate(frame, [20, 35], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <Background background={neuralPalette.bg}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          height: "100%",
          padding: "80px 120px",
          fontFamily: theme.monoFont,
          opacity: fadeIn,
        }}
      >
        {/* Title */}
        <div
          style={{
            color: accent,
            fontSize: 36,
            fontWeight: 700,
            letterSpacing: "0.1em",
            marginBottom: 40,
            textTransform: "uppercase",
          }}
        >
          {data.title}
        </div>

        {/* Optional big text above bar */}
        {data.bigText && (
          <div
            style={{
              color: theme.textPrimary,
              fontSize: 48,
              fontWeight: 600,
              marginBottom: 30,
              opacity: bigTextOpacity,
              transform: `scale(${bigTextScale})`,
            }}
          >
            {data.bigText}
          </div>
        )}

        {/* Progress bar container */}
        <div
          style={{
            width: "80%",
            maxWidth: 900,
            position: "relative",
          }}
        >
          {/* Outer border */}
          <div
            style={{
              border: `1.5px solid ${hexToRgba("#ffffff", 0.25)}`,
              borderRadius: 4,
              padding: 3,
              background: "transparent",
            }}
          >
            {/* Fill */}
            <div
              style={{
                height: 220,
                width: `${fillPercent}%`,
                background: accent,
                borderRadius: 2,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                position: "relative",
                overflow: "hidden",
              }}
            >
              {/* Percentage text on fill */}
              {fillPercent > 15 && (
                <span
                  style={{
                    color: "#ffffff",
                    fontSize: 72,
                    fontWeight: 300,
                    fontStyle: "italic",
                    zIndex: 1,
                  }}
                >
                  {displayPercent}%
                </span>
              )}
            </div>
          </div>

          {/* Small percentage when bar is small */}
          {fillPercent <= 15 && (
            <div
              style={{
                color: neuralPalette.textDim,
                fontSize: 32,
                textAlign: "center",
                marginTop: 12,
              }}
            >
              {displayPercent}%
            </div>
          )}
        </div>

        {/* Optional label below */}
        {data.label && (
          <div
            style={{
              color: neuralPalette.textDim,
              fontSize: 24,
              marginTop: 24,
              opacity: labelFade,
              letterSpacing: "0.02em",
            }}
          >
            {data.label}
          </div>
        )}
      </div>
    </Background>
  );
};
