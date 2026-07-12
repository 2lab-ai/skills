import React from "react";
import { useCurrentFrame, spring, interpolate, useVideoConfig } from "remotion";
import { Background } from "../components/Background";
import { useFadeIn } from "../utils/animations";
import type { MapData } from "../types";
import { palette, hexToRgba, getTheme } from "../utils/colors";

interface MapProps {
  data: MapData;
  accentColor?: string;
  themeName?: string;
}

// Simplified world map SVG path (continents outline)
const WORLD_PATH =
  "M165,85 L170,80 L180,82 L185,78 L195,80 L200,75 L210,78 L215,73 L220,76 L230,72 L240,75 L250,70 L260,73 L270,68 L280,72 L290,75 L300,70 L310,74 L320,70 L330,73 L340,68 L350,72 L355,68 L360,72 L365,75 L370,80 L375,85 L370,90 L365,95 L360,100 L370,105 L375,110 L370,115 L365,120 L370,130 L365,135 L360,140 L355,145 L350,140 L345,135 L340,130 L335,125 L330,130 L325,135 L320,140 L315,145 L310,140 L305,135 L300,130 L295,135 L290,140 L285,145 L280,140 L275,135 L270,130 L265,125 L260,130 L255,140 L250,145 L245,150 L240,155 L235,150 L230,145 L225,140 L220,135 L215,130 L210,125 L205,120 L200,115 L195,110 L190,105 L185,100 L180,95 L175,90 Z M400,70 L420,65 L440,68 L460,65 L480,70 L500,68 L520,72 L540,68 L560,72 L570,78 L575,85 L570,92 L565,98 L570,105 L575,112 L570,118 L565,125 L560,130 L550,135 L540,130 L530,128 L520,132 L510,128 L500,125 L490,130 L480,135 L470,138 L460,142 L450,138 L440,135 L430,130 L420,125 L410,120 L405,115 L400,110 L395,105 L400,95 L395,88 Z M580,90 L600,85 L620,88 L640,85 L660,90 L670,95 L680,100 L685,110 L680,120 L675,130 L670,140 L660,145 L650,148 L640,152 L630,155 L620,158 L610,155 L600,150 L590,145 L585,140 L580,130 L575,120 L580,110 L575,100 Z";

// Mercator-like projection (lon/lat → x/y on 800x400 canvas)
const project = (lon: number, lat: number): [number, number] => {
  const x = ((lon + 180) / 360) * 800;
  const y = ((90 - lat) / 180) * 400;
  return [x, y];
};

export const Map: React.FC<MapProps> = ({ data, accentColor, themeName }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName);
  const accent = accentColor || theme.accent;
  const titleOpacity = useFadeIn(0, 12);

  return (
    <Background themeName={themeName}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          padding: "60px 100px",
          height: "100%",
        }}
      >
        <h2
          style={{
            color: theme.textPrimary,
            fontSize: 44,
            fontFamily: theme.headingFont,
            fontWeight: 700,
            marginBottom: 40,
            opacity: titleOpacity,
            letterSpacing: "-0.02em",
          }}
        >
          {data.title}
        </h2>

        {/* Map container */}
        <div
          style={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            position: "relative",
          }}
        >
          <svg width={800} height={400} viewBox="0 0 800 400">
            {/* World outline */}
            <path
              d={WORLD_PATH}
              fill={hexToRgba(palette.white, 0.04)}
              stroke={hexToRgba(palette.white, 0.12)}
              strokeWidth={1}
            />

            {/* Grid lines */}
            {[0, 100, 200, 300, 400, 500, 600, 700, 800].map((x) => (
              <line
                key={`vl-${x}`}
                x1={x}
                y1={0}
                x2={x}
                y2={400}
                stroke={hexToRgba(palette.white, 0.03)}
                strokeWidth={0.5}
              />
            ))}
            {[0, 80, 160, 240, 320, 400].map((y) => (
              <line
                key={`hl-${y}`}
                x1={0}
                y1={y}
                x2={800}
                y2={y}
                stroke={hexToRgba(palette.white, 0.03)}
                strokeWidth={0.5}
              />
            ))}

            {/* Points */}
            {data.points.map((point, i) => {
              const delay = i * 10 + 15;
              const s = spring({
                frame: Math.max(0, frame - delay),
                fps,
                config: { damping: 15, stiffness: 120 },
              });
              const [px, py] = project(point.lon, point.lat);
              const color = point.color || accent;
              const size = (point.size ?? 1) * 8;
              const pulsePhase = Math.sin((frame - delay) * 0.08) * 0.3 + 0.7;

              return (
                <g key={i}>
                  {/* Pulse ring */}
                  <circle
                    cx={px}
                    cy={py}
                    r={size * 2.5 * s}
                    fill="none"
                    stroke={hexToRgba(color, 0.2 * pulsePhase)}
                    strokeWidth={1.5}
                  />
                  {/* Dot */}
                  <circle
                    cx={px}
                    cy={py}
                    r={size * s}
                    fill={color}
                    opacity={s}
                  />
                  {/* Label */}
                  {point.label && (
                    <text
                      x={px}
                      y={py - size - 10}
                      fill={theme.textPrimary}
                      fontSize={14}
                      fontFamily={theme.fontFamily}
                      fontWeight={600}
                      textAnchor="middle"
                      opacity={s}
                    >
                      {point.label}
                    </text>
                  )}
                </g>
              );
            })}

            {/* Connection lines between points */}
            {data.connections?.map((conn, i) => {
              const fromPt = data.points[conn[0]];
              const toPt = data.points[conn[1]];
              if (!fromPt || !toPt) return null;
              const [x1, y1] = project(fromPt.lon, fromPt.lat);
              const [x2, y2] = project(toPt.lon, toPt.lat);
              const delay = Math.max(conn[0], conn[1]) * 10 + 25;
              const lineS = spring({
                frame: Math.max(0, frame - delay),
                fps,
                config: { damping: 30, stiffness: 60 },
              });
              const cx = (x1 + x2) / 2;
              const cy2 = Math.min(y1, y2) - 40;
              return (
                <path
                  key={`conn-${i}`}
                  d={`M${x1},${y1} Q${cx},${cy2} ${x2},${y2}`}
                  fill="none"
                  stroke={hexToRgba(accent, 0.4)}
                  strokeWidth={1.5}
                  strokeDasharray={`${lineS * 500} 500`}
                />
              );
            })}
          </svg>
        </div>

        {/* Legend */}
        {data.legend && (
          <div
            style={{
              display: "flex",
              gap: 24,
              justifyContent: "center",
              marginTop: 20,
              opacity: interpolate(frame, [20, 35], [0, 1], { extrapolateRight: "clamp" }),
            }}
          >
            {data.legend.map((item, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <div
                  style={{
                    width: 12,
                    height: 12,
                    borderRadius: "50%",
                    background: item.color || accent,
                  }}
                />
                <span
                  style={{
                    color: theme.textSecondary,
                    fontSize: 16,
                    fontFamily: theme.fontFamily,
                  }}
                >
                  {item.label}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </Background>
  );
};
