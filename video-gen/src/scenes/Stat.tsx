import React from "react";
import { useCurrentFrame, spring, interpolate, useVideoConfig } from "remotion";
import { Background } from "../components/Background";
import { useFadeIn } from "../utils/animations";
import type { StatData } from "../types";
import { palette, hexToRgba } from "../utils/colors";

interface StatProps {
  data: StatData;
  accentColor?: string;
}

const AnimatedNumber: React.FC<{
  value: string | number;
  delay: number;
}> = ({ value, delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (typeof value === "number") {
    const s = spring({
      frame: frame - delay,
      fps,
      config: { damping: 30, stiffness: 60 },
    });
    const animatedValue = Math.round(interpolate(s, [0, 1], [0, value]));
    return <>{animatedValue.toLocaleString()}</>;
  }

  return <>{value}</>;
};

export const Stat: React.FC<StatProps> = ({ data, accentColor }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = accentColor || palette.accent;
  const titleOpacity = useFadeIn(0, 12);
  const cols = data.stats.length <= 2 ? data.stats.length : data.stats.length <= 4 ? 2 : 3;

  return (
    <Background>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          padding: "80px 120px",
          height: "100%",
        }}
      >
        <h2
          style={{
            color: palette.white,
            fontSize: 52,
            fontWeight: 700,
            marginBottom: 60,
            opacity: titleOpacity,
            letterSpacing: "-0.02em",
          }}
        >
          {data.title}
        </h2>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: `repeat(${cols}, 1fr)`,
            gap: 32,
            flex: 1,
            alignContent: "center",
          }}
        >
          {data.stats.map((stat, i) => {
            const delay = i * 10 + 10;
            const s = spring({
              frame: frame - delay,
              fps,
              config: { damping: 18, stiffness: 90 },
            });
            const opacity = interpolate(s, [0, 1], [0, 1]);
            const scale = interpolate(s, [0, 1], [0.9, 1]);

            return (
              <div
                key={i}
                style={{
                  background: hexToRgba(palette.white, 0.04),
                  border: `1px solid ${hexToRgba(palette.white, 0.08)}`,
                  borderRadius: 24,
                  padding: "48px 40px",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: 12,
                  opacity,
                  transform: `scale(${scale})`,
                }}
              >
                {/* Value */}
                <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
                  <span
                    style={{
                      color: accent,
                      fontSize: 64,
                      fontWeight: 800,
                      letterSpacing: "-0.03em",
                    }}
                  >
                    <AnimatedNumber value={stat.value} delay={delay} />
                  </span>
                  {stat.unit && (
                    <span
                      style={{
                        color: palette.gray300,
                        fontSize: 28,
                        fontWeight: 500,
                      }}
                    >
                      {stat.unit}
                    </span>
                  )}
                </div>

                {/* Label */}
                <span
                  style={{
                    color: palette.gray300,
                    fontSize: 24,
                    fontWeight: 500,
                    textAlign: "center",
                  }}
                >
                  {stat.label}
                </span>

                {/* Change indicator */}
                {stat.change && (
                  <span
                    style={{
                      color: stat.change.startsWith("+") ? palette.success : stat.change.startsWith("-") ? palette.error : palette.gray300,
                      fontSize: 20,
                      fontWeight: 600,
                      background: stat.change.startsWith("+")
                        ? hexToRgba(palette.success, 0.1)
                        : stat.change.startsWith("-")
                        ? hexToRgba(palette.error, 0.1)
                        : "transparent",
                      padding: "4px 14px",
                      borderRadius: 8,
                    }}
                  >
                    {stat.change}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </Background>
  );
};
