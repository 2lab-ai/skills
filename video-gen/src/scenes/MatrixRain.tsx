import React, { useMemo } from "react";
import { useCurrentFrame, interpolate, useVideoConfig } from "remotion";
import type { MatrixRainData } from "../types";
import { getTheme, neuralPalette } from "../utils/colors";

interface MatrixRainProps {
  data: MatrixRainData;
  accentColor?: string;
  themeName?: string;
}

const DEFAULT_CHARSET =
  "∂∫∑∏√≈≠≤≥∞θΩπ∇∆αβγδεζηλμν01";

interface Column {
  x: number;
  chars: Array<{ char: string; y: number; size: number; opacity: number }>;
  speed: number;
  offset: number;
}

export const MatrixRain: React.FC<MatrixRainProps> = ({
  data,
  accentColor,
  themeName,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const theme = getTheme(themeName || "neural");
  const color = data.color || neuralPalette.green;
  const numCols = data.columns || 40;
  const speed = data.speed || 1;
  const charset = data.charset || DEFAULT_CHARSET;

  // Generate deterministic columns (seeded by column index)
  const columns = useMemo<Column[]>(() => {
    const cols: Column[] = [];
    const colWidth = width / numCols;

    for (let c = 0; c < numCols; c++) {
      // Deterministic seed per column
      const seed = Math.sin(c * 127.1 + 311.7) * 43758.5453;
      const seedFrac = seed - Math.floor(seed);

      const numChars = 15 + Math.floor(seedFrac * 25);
      const chars: Column["chars"] = [];

      for (let j = 0; j < numChars; j++) {
        const charSeed =
          Math.sin((c * numChars + j) * 73.15 + 91.23) * 43758.5453;
        const charFrac = charSeed - Math.floor(charSeed);
        const charIdx = Math.floor(charFrac * charset.length);

        chars.push({
          char: charset[charIdx] || "∂",
          y: (j / numChars) * (height + 400) - 200,
          size: 14 + Math.floor(charFrac * 12),
          opacity: 0.15 + charFrac * 0.7,
        });
      }

      cols.push({
        x: c * colWidth + colWidth * 0.3,
        chars,
        speed: 1.5 + seedFrac * 3,
        offset: seedFrac * height,
      });
    }

    return cols;
  }, [numCols, width, height, charset]);

  // Overlay text
  const overlayFade = interpolate(frame, [15, 30], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: "#000000",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Rain columns */}
      {columns.map((col, ci) => (
        <div key={ci} style={{ position: "absolute", left: col.x }}>
          {col.chars.map((ch, chi) => {
            const yPos =
              ((ch.y + col.offset + frame * col.speed * speed) %
                (height + 400)) -
              200;

            // Head character is brighter
            const isHead =
              chi === col.chars.length - 1 ||
              (chi > col.chars.length - 4 && chi < col.chars.length);

            // Deterministic "flicker" based on frame and index
            const flickerSeed = Math.sin(
              frame * 0.3 + ci * 17.3 + chi * 7.7
            );
            const flicker = flickerSeed > 0.7 ? 0.3 : 0;

            // Switch char occasionally
            const charSwapSeed = Math.sin(
              frame * 0.1 + ci * 31.2 + chi * 13.3
            );
            const displayChar =
              charSwapSeed > 0.85
                ? charset[
                    Math.floor(
                      Math.abs(charSwapSeed * 43758.5453) % charset.length
                    )
                  ]
                : ch.char;

            return (
              <span
                key={chi}
                style={{
                  position: "absolute",
                  top: yPos,
                  color: isHead ? "#ffffff" : color,
                  fontSize: ch.size,
                  fontFamily: "'JetBrains Mono', monospace",
                  opacity: ch.opacity + flicker,
                  textShadow: isHead
                    ? `0 0 10px ${color}, 0 0 20px ${color}`
                    : `0 0 4px ${color}`,
                  lineHeight: 1,
                }}
              >
                {displayChar}
              </span>
            );
          })}
        </div>
      ))}

      {/* Optional overlay text */}
      {data.overlayText && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 10,
          }}
        >
          <div
            style={{
              color: "#ffffff",
              fontSize: 64,
              fontFamily: theme.monoFont,
              fontWeight: 700,
              textShadow: `0 0 30px ${color}, 0 0 60px ${color}`,
              opacity: overlayFade,
              padding: "20px 60px",
              background: "rgba(0,0,0,0.5)",
              borderRadius: 8,
            }}
          >
            {data.overlayText}
          </div>
        </div>
      )}
    </div>
  );
};
