import React from "react";
import { useCurrentFrame, spring, interpolate, useVideoConfig } from "remotion";
import { Background } from "../components/Background";
import type { CountdownData } from "../types";
import { palette, hexToRgba, getTheme } from "../utils/colors";

interface CountdownProps {
  data: CountdownData;
  accentColor?: string;
  themeName?: string;
}

export const Countdown: React.FC<CountdownProps> = ({ data, accentColor, themeName }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName);
  const accent = accentColor || theme.accent;

  const from = data.from ?? 5;
  const to = data.to ?? 0;
  const framesPerCount = Math.round(fps * (data.speed ?? 1));
  const totalCounts = Math.abs(from - to) + 1;
  const direction = from > to ? -1 : 1;

  // Current number
  const countIndex = Math.min(Math.floor(frame / framesPerCount), totalCounts - 1);
  const currentNumber = from + countIndex * direction;
  const isFinished = countIndex >= totalCounts - 1;

  // Per-number animation
  const localFrame = frame - countIndex * framesPerCount;
  const scaleS = spring({
    frame: localFrame,
    fps,
    config: { damping: 12, stiffness: 200 },
  });
  const scale = interpolate(scaleS, [0, 1], [2.5, 1]);
  const opacity = interpolate(scaleS, [0, 1], [0.3, 1]);

  // Final reveal
  const finalS = spring({
    frame: isFinished ? localFrame : 0,
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  // Ring animation
  const progress = countIndex / Math.max(totalCounts - 1, 1);
  const circumference = 2 * Math.PI * 200;
  const dashOffset = circumference * (1 - progress * scaleS);

  return (
    <Background themeName={themeName}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          height: "100%",
          gap: 40,
        }}
      >
        {/* Title */}
        {data.title && (
          <h2
            style={{
              color: theme.textSecondary,
              fontSize: 32,
              fontFamily: theme.fontFamily,
              fontWeight: 500,
              textTransform: "uppercase",
              letterSpacing: "0.15em",
              opacity: interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" }),
            }}
          >
            {data.title}
          </h2>
        )}

        {/* Ring + Number */}
        <div style={{ position: "relative", width: 440, height: 440 }}>
          <svg
            width={440}
            height={440}
            viewBox="0 0 440 440"
            style={{ position: "absolute", top: 0, left: 0 }}
          >
            {/* Background ring */}
            <circle
              cx={220}
              cy={220}
              r={200}
              fill="none"
              stroke={hexToRgba(palette.white, 0.06)}
              strokeWidth={6}
            />
            {/* Progress ring */}
            <circle
              cx={220}
              cy={220}
              r={200}
              fill="none"
              stroke={accent}
              strokeWidth={6}
              strokeDasharray={circumference}
              strokeDashoffset={dashOffset}
              strokeLinecap="round"
              transform="rotate(-90 220 220)"
            />
          </svg>

          {/* Number */}
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {isFinished && data.revealText ? (
              <span
                style={{
                  color: accent,
                  fontSize: 80,
                  fontFamily: theme.headingFont,
                  fontWeight: 800,
                  transform: `scale(${interpolate(finalS, [0, 1], [0.5, 1])})`,
                  opacity: finalS,
                  textAlign: "center",
                  lineHeight: 1.2,
                }}
              >
                {data.revealText}
              </span>
            ) : (
              <span
                style={{
                  color: theme.textPrimary,
                  fontSize: 180,
                  fontFamily: theme.headingFont,
                  fontWeight: 800,
                  transform: `scale(${scale})`,
                  opacity,
                  letterSpacing: "-0.05em",
                }}
              >
                {currentNumber}
              </span>
            )}
          </div>
        </div>

        {/* Subtitle */}
        {data.subtitle && (
          <p
            style={{
              color: theme.textSecondary,
              fontSize: 24,
              fontFamily: theme.fontFamily,
              fontWeight: 400,
              opacity: isFinished ? finalS : 0.6,
            }}
          >
            {isFinished && data.revealSubtitle ? data.revealSubtitle : data.subtitle}
          </p>
        )}
      </div>
    </Background>
  );
};
