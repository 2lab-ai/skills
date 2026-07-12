import React from "react";
import { useCurrentFrame, spring, interpolate, useVideoConfig } from "remotion";
import { Background } from "../components/Background";
import { useFadeIn } from "../utils/animations";
import type { PyramidData } from "../types";
import { palette, hexToRgba, getTheme } from "../utils/colors";

interface PyramidProps {
  data: PyramidData;
  accentColor?: string;
  themeName?: string;
}

export const Pyramid: React.FC<PyramidProps> = ({ data, accentColor, themeName }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName);
  const accent = accentColor || theme.accent;
  const titleOpacity = useFadeIn(0, 12);

  const levels = data.levels;
  const count = levels.length;
  const variant = data.variant ?? "default";

  // Pyramid dimensions
  const pyramidWidth = 900;
  const pyramidHeight = 600;
  const topWidth = pyramidWidth * 0.2;
  const levelHeight = pyramidHeight / count;

  // Color interpolation
  const getColor = (index: number): string => {
    if (levels[index].color) return levels[index].color!;
    const hueStart = 200; // blue
    const hueEnd = 30; // orange
    const t = index / Math.max(count - 1, 1);
    const hue = hueStart + (hueEnd - hueStart) * t;
    return `hsl(${hue}, 65%, 55%)`;
  };

  return (
    <Background themeName={themeName}>
      <div
        style={{
          display: "flex",
          padding: "60px 80px",
          height: "100%",
          gap: 60,
          alignItems: "center",
        }}
      >
        {/* Pyramid visualization */}
        <div style={{ flex: "0 0 auto", position: "relative" }}>
          <svg width={pyramidWidth} height={pyramidHeight + 20} viewBox={`0 0 ${pyramidWidth} ${pyramidHeight + 20}`}>
            {levels.map((level, i) => {
              // Build from top (index 0) to bottom
              const delay = i * 12 + 12;
              const s = spring({
                frame: Math.max(0, frame - delay),
                fps,
                config: { damping: 18, stiffness: 70 },
              });

              const yTop = i * levelHeight;
              const yBottom = (i + 1) * levelHeight;
              const widthFraction = (i + 1) / count;
              const widthFractionPrev = i / count;

              const xLeftTop = (pyramidWidth - topWidth - (pyramidWidth - topWidth) * widthFractionPrev) / 2;
              const xRightTop = pyramidWidth - xLeftTop;
              const xLeftBottom = (pyramidWidth - topWidth - (pyramidWidth - topWidth) * widthFraction) / 2;
              const xRightBottom = pyramidWidth - xLeftBottom;

              const color = getColor(i);
              const opacity = s;
              const scaleY = interpolate(s, [0, 1], [0.8, 1]);

              const path = `M${xLeftTop},${yTop} L${xRightTop},${yTop} L${xRightBottom},${yBottom} L${xLeftBottom},${yBottom} Z`;

              return (
                <g key={i} style={{ opacity }}>
                  {/* Level shape */}
                  <path
                    d={path}
                    fill={hexToRgba(color, 0.25)}
                    stroke={color}
                    strokeWidth={2}
                  />
                  {/* Level label */}
                  <text
                    x={pyramidWidth / 2}
                    y={yTop + levelHeight / 2 + 6}
                    fill={theme.textPrimary}
                    fontSize={Math.max(16, 24 - count)}
                    fontFamily={theme.headingFont}
                    fontWeight={700}
                    textAnchor="middle"
                    opacity={s}
                  >
                    {level.emoji ? `${level.emoji} ` : ""}{level.label}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Labels / descriptions */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            gap: 12,
          }}
        >
          <h2
            style={{
              color: theme.textPrimary,
              fontSize: 40,
              fontFamily: theme.headingFont,
              fontWeight: 700,
              margin: 0,
              marginBottom: 24,
              opacity: titleOpacity,
              letterSpacing: "-0.02em",
            }}
          >
            {data.title}
          </h2>

          {levels.map((level, i) => {
            if (!level.description) return null;
            const delay = i * 12 + 20;
            const s = spring({
              frame: Math.max(0, frame - delay),
              fps,
              config: { damping: 22, stiffness: 80 },
            });
            const color = getColor(i);

            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: 14,
                  opacity: s,
                  transform: `translateX(${interpolate(s, [0, 1], [20, 0])}px)`,
                }}
              >
                <div
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: 3,
                    background: color,
                    marginTop: 8,
                    flexShrink: 0,
                  }}
                />
                <div>
                  <span
                    style={{
                      color: theme.textPrimary,
                      fontSize: 18,
                      fontFamily: theme.headingFont,
                      fontWeight: 700,
                    }}
                  >
                    {level.label}
                  </span>
                  <span
                    style={{
                      color: theme.textSecondary,
                      fontSize: 16,
                      fontFamily: theme.fontFamily,
                      marginLeft: 8,
                    }}
                  >
                    {level.description}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Background>
  );
};
