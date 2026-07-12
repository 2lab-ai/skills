import React from "react";
import { useCurrentFrame, spring, interpolate, useVideoConfig } from "remotion";
import { Background } from "../components/Background";
import { useFadeIn } from "../utils/animations";
import type { RadarData } from "../types";
import { palette, hexToRgba, getTheme } from "../utils/colors";

interface RadarProps {
  data: RadarData;
  accentColor?: string;
  themeName?: string;
}

export const Radar: React.FC<RadarProps> = ({ data, accentColor, themeName }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName);
  const accent = accentColor || theme.accent;
  const titleOpacity = useFadeIn(0, 12);

  const axes = data.axes;
  const count = axes.length;
  const cx = 400;
  const cy = 400;
  const maxR = 300;
  const rings = data.rings ?? 5;

  // Animation spring
  const s = spring({
    frame: Math.max(0, frame - 15),
    fps,
    config: { damping: 20, stiffness: 60 },
  });

  // Calculate polygon points
  const getPoint = (index: number, value: number, scale: number = 1) => {
    const angle = (Math.PI * 2 * index) / count - Math.PI / 2;
    const r = (value / 100) * maxR * scale;
    return {
      x: cx + r * Math.cos(angle),
      y: cy + r * Math.sin(angle),
    };
  };

  const polygonPoints = axes
    .map((axis, i) => {
      const p = getPoint(i, axis.value, s);
      return `${p.x},${p.y}`;
    })
    .join(" ");

  // Second dataset if exists
  const hasCompare = !!data.compareAxes;
  const comparePoints = hasCompare
    ? data.compareAxes!
        .map((axis, i) => {
          const p = getPoint(i, axis.value, s);
          return `${p.x},${p.y}`;
        })
        .join(" ")
    : "";

  return (
    <Background themeName={themeName}>
      <div
        style={{
          display: "flex",
          padding: "60px 100px",
          height: "100%",
          gap: 60,
          alignItems: "center",
        }}
      >
        {/* Chart */}
        <div style={{ flex: "0 0 800px", position: "relative" }}>
          <svg width={800} height={800} viewBox="0 0 800 800">
            {/* Grid rings */}
            {Array.from({ length: rings }).map((_, ringIdx) => {
              const ringR = (maxR * (ringIdx + 1)) / rings;
              const ringPoints = Array.from({ length: count })
                .map((_, i) => {
                  const angle = (Math.PI * 2 * i) / count - Math.PI / 2;
                  return `${cx + ringR * Math.cos(angle)},${cy + ringR * Math.sin(angle)}`;
                })
                .join(" ");
              return (
                <polygon
                  key={`ring-${ringIdx}`}
                  points={ringPoints}
                  fill="none"
                  stroke={hexToRgba(palette.white, 0.08)}
                  strokeWidth={1}
                />
              );
            })}

            {/* Axis lines */}
            {axes.map((_, i) => {
              const p = getPoint(i, 100);
              return (
                <line
                  key={`axis-${i}`}
                  x1={cx}
                  y1={cy}
                  x2={p.x}
                  y2={p.y}
                  stroke={hexToRgba(palette.white, 0.1)}
                  strokeWidth={1}
                />
              );
            })}

            {/* Compare polygon */}
            {hasCompare && (
              <polygon
                points={comparePoints}
                fill={hexToRgba(palette.gray400, 0.15)}
                stroke={palette.gray400}
                strokeWidth={2}
                strokeDasharray="6 4"
              />
            )}

            {/* Main polygon */}
            <polygon
              points={polygonPoints}
              fill={hexToRgba(accent, 0.2)}
              stroke={accent}
              strokeWidth={3}
            />

            {/* Data points */}
            {axes.map((axis, i) => {
              const p = getPoint(i, axis.value, s);
              return (
                <circle
                  key={`dot-${i}`}
                  cx={p.x}
                  cy={p.y}
                  r={6}
                  fill={accent}
                  stroke={theme.cardBg || "#0f0f23"}
                  strokeWidth={3}
                />
              );
            })}

            {/* Axis labels */}
            {axes.map((axis, i) => {
              const labelR = maxR + 40;
              const angle = (Math.PI * 2 * i) / count - Math.PI / 2;
              const lx = cx + labelR * Math.cos(angle);
              const ly = cy + labelR * Math.sin(angle);
              return (
                <text
                  key={`label-${i}`}
                  x={lx}
                  y={ly}
                  fill={theme.textPrimary}
                  fontSize={20}
                  fontFamily={theme.fontFamily}
                  fontWeight={600}
                  textAnchor="middle"
                  dominantBaseline="middle"
                >
                  {axis.label}
                </text>
              );
            })}
          </svg>
        </div>

        {/* Legend / Title */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 24 }}>
          <h2
            style={{
              color: theme.textPrimary,
              fontSize: 44,
              fontFamily: theme.headingFont,
              fontWeight: 700,
              opacity: titleOpacity,
              margin: 0,
              letterSpacing: "-0.02em",
            }}
          >
            {data.title}
          </h2>

          {/* Legend items */}
          <div style={{ display: "flex", flexDirection: "column", gap: 16, marginTop: 20 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div
                style={{
                  width: 16,
                  height: 16,
                  borderRadius: 4,
                  background: accent,
                }}
              />
              <span
                style={{
                  color: theme.textSecondary,
                  fontSize: 20,
                  fontFamily: theme.fontFamily,
                }}
              >
                {data.label ?? "Current"}
              </span>
            </div>
            {hasCompare && (
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div
                  style={{
                    width: 16,
                    height: 16,
                    borderRadius: 4,
                    background: palette.gray400,
                  }}
                />
                <span
                  style={{
                    color: theme.textSecondary,
                    fontSize: 20,
                    fontFamily: theme.fontFamily,
                  }}
                >
                  {data.compareLabel ?? "Previous"}
                </span>
              </div>
            )}
          </div>

          {/* Axis values */}
          <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 20 }}>
            {axes.map((axis, i) => {
              const delay = i * 8 + 20;
              const barS = spring({
                frame: Math.max(0, frame - delay),
                fps,
                config: { damping: 25, stiffness: 80 },
              });
              return (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <span
                    style={{
                      color: theme.textSecondary,
                      fontSize: 16,
                      fontFamily: theme.fontFamily,
                      width: 100,
                      textAlign: "right",
                    }}
                  >
                    {axis.label}
                  </span>
                  <div
                    style={{
                      flex: 1,
                      height: 8,
                      background: hexToRgba(palette.white, 0.06),
                      borderRadius: 4,
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        width: `${axis.value * barS}%`,
                        height: "100%",
                        background: accent,
                        borderRadius: 4,
                      }}
                    />
                  </div>
                  <span
                    style={{
                      color: accent,
                      fontSize: 16,
                      fontFamily: theme.headingFont,
                      fontWeight: 700,
                      width: 40,
                    }}
                  >
                    {Math.round(axis.value * barS)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </Background>
  );
};
