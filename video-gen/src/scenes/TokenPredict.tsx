import React from "react";
import {
  useCurrentFrame,
  spring,
  interpolate,
  useVideoConfig,
} from "remotion";
import { Background } from "../components/Background";
import type { TokenPredictData } from "../types";
import { getTheme, hexToRgba, neuralPalette } from "../utils/colors";

interface TokenPredictProps {
  data: TokenPredictData;
  accentColor?: string;
  themeName?: string;
}

export const TokenPredict: React.FC<TokenPredictProps> = ({
  data,
  accentColor,
  themeName,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName || "neural");
  const accent = accentColor || neuralPalette.orange;

  const words = data.sentence.split(" ");
  const animate = data.animate ?? "highlight-walk";

  // Which word is highlighted
  const highlightIdx =
    animate === "highlight-walk"
      ? Math.min(Math.floor(frame / 12), words.length - 1)
      : data.highlightIndex ?? words.length - 1;

  // Overall fade in
  const fadeIn = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Bar chart section fade
  const barFade = interpolate(frame, [8, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  const maxProb = Math.max(
    ...data.predictions.map((p) => p.probability),
    1
  );

  return (
    <Background background={neuralPalette.bg}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          height: "100%",
          padding: "80px 60px",
          fontFamily: theme.monoFont,
          opacity: fadeIn,
        }}
      >
        {/* Main sentence with word highlighting */}
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "10px",
            alignItems: "baseline",
            marginBottom: 80,
            lineHeight: 1.4,
          }}
        >
          {words.map((word, i) => {
            const isHighlighted = i === highlightIdx;
            const isRevealed =
              animate === "reveal" ? i <= highlightIdx : true;

            const wordSpring = spring({
              frame: Math.max(0, frame - i * 4),
              fps,
              config: { damping: 20, stiffness: 100 },
            });
            const wordOpacity =
              animate === "reveal"
                ? isRevealed
                  ? interpolate(wordSpring, [0, 1], [0, 1])
                  : 0
                : 1;

            return (
              <span
                key={i}
                style={{
                  fontSize: 52,
                  fontWeight: 500,
                  color: isHighlighted
                    ? neuralPalette.bg
                    : hexToRgba(neuralPalette.textWarm, isRevealed ? 0.9 : 0.3),
                  background: isHighlighted ? accent : "transparent",
                  padding: isHighlighted ? "4px 8px" : "4px 0",
                  opacity: wordOpacity,
                  transition: "background 0.1s",
                }}
              >
                {word}
              </span>
            );
          })}
        </div>

        {/* Probability bar chart */}
        <div
          style={{
            opacity: barFade,
            fontFamily: theme.monoFont,
          }}
        >
          <div
            style={{
              color: neuralPalette.textDim,
              fontSize: 22,
              marginBottom: 16,
            }}
          >
            P(next token):
          </div>

          {data.predictions.map((pred, i) => {
            const barSpring = spring({
              frame: Math.max(0, frame - 12 - i * 5),
              fps,
              config: { damping: 25, stiffness: 80 },
            });
            const barWidth = interpolate(
              barSpring,
              [0, 1],
              [0, (pred.probability / maxProb) * 500]
            );

            const isTop = i === 0;

            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 16,
                  marginBottom: 6,
                  fontSize: 20,
                }}
              >
                <span
                  style={{
                    color: neuralPalette.textWarm,
                    width: 100,
                    textAlign: "left",
                  }}
                >
                  {pred.token}
                </span>
                <div
                  style={{
                    height: 18,
                    width: barWidth,
                    background: isTop
                      ? accent
                      : hexToRgba(neuralPalette.textWarm, 0.25),
                    borderRadius: 2,
                  }}
                />
                <span
                  style={{
                    color: isTop
                      ? neuralPalette.textWarm
                      : neuralPalette.textDim,
                    fontSize: 18,
                  }}
                >
                  {pred.probability}%
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </Background>
  );
};
