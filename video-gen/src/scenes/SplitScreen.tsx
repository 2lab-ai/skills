import React from "react";
import { useCurrentFrame, spring, interpolate, useVideoConfig } from "remotion";
import { Background } from "../components/Background";
import { useFadeIn } from "../utils/animations";
import type { SplitScreenData } from "../types";
import { palette, hexToRgba, getTheme } from "../utils/colors";

interface SplitScreenProps {
  data: SplitScreenData;
  accentColor?: string;
  themeName?: string;
}

const Panel: React.FC<{
  panel: SplitScreenData["panels"][0];
  index: number;
  total: number;
  theme: ReturnType<typeof getTheme>;
  accent: string;
  frame: number;
  fps: number;
}> = ({ panel, index, total, theme, accent, frame, fps }) => {
  const delay = index * 10 + 10;
  const s = spring({
    frame: Math.max(0, frame - delay),
    fps,
    config: { damping: 18, stiffness: 80 },
  });

  const slideDir = index === 0 ? -1 : index === total - 1 ? 1 : 0;
  const translateX = interpolate(s, [0, 1], [slideDir * 40, 0]);

  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 24,
        padding: "40px 36px",
        background: panel.background ?? hexToRgba(palette.white, 0.02),
        borderRight: index < total - 1 ? `1px solid ${hexToRgba(palette.white, 0.08)}` : "none",
        opacity: s,
        transform: `translateX(${translateX}px)`,
      }}
    >
      {/* Emoji */}
      {panel.emoji && (
        <span style={{ fontSize: 64, marginBottom: 8 }}>{panel.emoji}</span>
      )}

      {/* Title */}
      <h3
        style={{
          color: panel.accentColor ?? accent,
          fontSize: 32,
          fontFamily: theme.headingFont,
          fontWeight: 700,
          margin: 0,
          textAlign: "center",
          letterSpacing: "-0.02em",
        }}
      >
        {panel.title}
      </h3>

      {/* Content items */}
      {panel.items && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 14,
            marginTop: 12,
          }}
        >
          {panel.items.map((item, i) => {
            const itemDelay = delay + (i + 1) * 6;
            const itemS = spring({
              frame: Math.max(0, frame - itemDelay),
              fps,
              config: { damping: 22, stiffness: 90 },
            });
            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  opacity: itemS,
                  transform: `translateY(${interpolate(itemS, [0, 1], [8, 0])}px)`,
                }}
              >
                <div
                  style={{
                    width: 6,
                    height: 6,
                    borderRadius: "50%",
                    background: panel.accentColor ?? accent,
                    flexShrink: 0,
                  }}
                />
                <span
                  style={{
                    color: theme.textSecondary,
                    fontSize: 22,
                    fontFamily: theme.fontFamily,
                    lineHeight: 1.5,
                  }}
                >
                  {item}
                </span>
              </div>
            );
          })}
        </div>
      )}

      {/* Description */}
      {panel.description && (
        <p
          style={{
            color: theme.textSecondary,
            fontSize: 20,
            fontFamily: theme.fontFamily,
            textAlign: "center",
            lineHeight: 1.6,
            margin: 0,
            marginTop: 8,
          }}
        >
          {panel.description}
        </p>
      )}
    </div>
  );
};

export const SplitScreen: React.FC<SplitScreenProps> = ({ data, accentColor, themeName }) => {
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
          height: "100%",
        }}
      >
        {/* Title */}
        {data.title && (
          <h2
            style={{
              color: theme.textPrimary,
              fontSize: 44,
              fontFamily: theme.headingFont,
              fontWeight: 700,
              padding: "60px 120px 30px",
              margin: 0,
              opacity: titleOpacity,
              letterSpacing: "-0.02em",
            }}
          >
            {data.title}
          </h2>
        )}

        {/* Panels */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: data.direction === "vertical" ? "column" : "row",
          }}
        >
          {data.panels.map((panel, i) => (
            <Panel
              key={i}
              panel={panel}
              index={i}
              total={data.panels.length}
              theme={theme}
              accent={accent}
              frame={frame}
              fps={fps}
            />
          ))}
        </div>
      </div>
    </Background>
  );
};
