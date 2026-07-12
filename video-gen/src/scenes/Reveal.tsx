import React from "react";
import { useCurrentFrame, spring, interpolate, useVideoConfig } from "remotion";
import { Background } from "../components/Background";
import type { RevealData } from "../types";
import { palette, hexToRgba, getTheme } from "../utils/colors";

interface RevealProps {
  data: RevealData;
  accentColor?: string;
  themeName?: string;
}

export const Reveal: React.FC<RevealProps> = ({ data, accentColor, themeName }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName);
  const accent = accentColor || theme.accent;

  const revealDelay = Math.round(fps * (data.delay ?? 2)); // seconds before reveal
  const isRevealed = frame >= revealDelay;

  // Pre-reveal: suspense elements
  const preOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });

  // Dots animation (suspense)
  const dotCount = 3;
  const dotFrame = Math.floor(frame * 0.1) % (dotCount + 1);
  const dots = ".".repeat(Math.min(dotFrame, dotCount));

  // Reveal animation
  const revealS = spring({
    frame: isRevealed ? frame - revealDelay : 0,
    fps,
    config: { damping: 12, stiffness: 100 },
  });
  const revealScale = interpolate(revealS, [0, 1], [3, 1]);
  const revealOpacity = revealS;

  // Particle burst on reveal
  const particles = Array.from({ length: 12 }).map((_, i) => {
    const angle = (i / 12) * Math.PI * 2;
    const distance = interpolate(revealS, [0, 1], [0, 200 + Math.random() * 100]);
    const x = Math.cos(angle) * distance;
    const y = Math.sin(angle) * distance;
    const size = interpolate(revealS, [0, 0.5, 1], [0, 8, 2]);
    const particleOpacity = interpolate(revealS, [0, 0.3, 1], [0, 1, 0]);
    return { x, y, size, opacity: particleOpacity };
  });

  // Flash effect
  const flashOpacity = isRevealed
    ? interpolate(frame - revealDelay, [0, 3, 10], [0, 0.6, 0], { extrapolateRight: "clamp" })
    : 0;

  return (
    <Background themeName={themeName}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          height: "100%",
          position: "relative",
        }}
      >
        {/* Flash overlay */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: accent,
            opacity: flashOpacity,
            pointerEvents: "none",
          }}
        />

        {/* Pre-reveal label */}
        {data.preLabel && (
          <span
            style={{
              color: theme.textSecondary,
              fontSize: 28,
              fontFamily: theme.fontFamily,
              fontWeight: 500,
              textTransform: "uppercase",
              letterSpacing: "0.15em",
              marginBottom: 40,
              opacity: preOpacity,
            }}
          >
            {data.preLabel}{!isRevealed ? dots : ""}
          </span>
        )}

        {/* Main reveal area */}
        <div style={{ position: "relative" }}>
          {/* Particle burst */}
          {isRevealed &&
            particles.map((p, i) => (
              <div
                key={i}
                style={{
                  position: "absolute",
                  left: "50%",
                  top: "50%",
                  width: p.size,
                  height: p.size,
                  borderRadius: "50%",
                  background: accent,
                  opacity: p.opacity,
                  transform: `translate(${p.x - p.size / 2}px, ${p.y - p.size / 2}px)`,
                  pointerEvents: "none",
                }}
              />
            ))}

          {!isRevealed ? (
            // Mystery placeholder
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: 300,
                height: 200,
              }}
            >
              <span
                style={{
                  color: hexToRgba(accent, 0.4),
                  fontSize: 120,
                  fontFamily: theme.headingFont,
                  fontWeight: 800,
                }}
              >
                ?
              </span>
            </div>
          ) : (
            // Revealed content
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 16,
                transform: `scale(${revealScale})`,
                opacity: revealOpacity,
              }}
            >
              {data.emoji && (
                <span style={{ fontSize: 80, marginBottom: 8 }}>{data.emoji}</span>
              )}
              <span
                style={{
                  color: accent,
                  fontSize: data.valueFontSize ?? 120,
                  fontFamily: theme.headingFont,
                  fontWeight: 800,
                  letterSpacing: "-0.04em",
                  textAlign: "center",
                  lineHeight: 1.1,
                }}
              >
                {data.value}
              </span>
              {data.unit && (
                <span
                  style={{
                    color: theme.textSecondary,
                    fontSize: 32,
                    fontFamily: theme.fontFamily,
                    fontWeight: 500,
                  }}
                >
                  {data.unit}
                </span>
              )}
            </div>
          )}
        </div>

        {/* Post-reveal subtitle */}
        {data.subtitle && isRevealed && (
          <p
            style={{
              color: theme.textSecondary,
              fontSize: 28,
              fontFamily: theme.fontFamily,
              fontWeight: 400,
              marginTop: 50,
              textAlign: "center",
              maxWidth: 800,
              lineHeight: 1.5,
              opacity: interpolate(
                frame - revealDelay,
                [10, 30],
                [0, 1],
                { extrapolateRight: "clamp" }
              ),
            }}
          >
            {data.subtitle}
          </p>
        )}
      </div>
    </Background>
  );
};
