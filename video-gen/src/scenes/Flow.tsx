import React from "react";
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import { Background } from "../components/Background";
import { useFadeIn } from "../utils/animations";
import type { FlowData } from "../types";
import { palette, hexToRgba } from "../utils/colors";

interface FlowProps {
  data: FlowData;
  accentColor?: string;
}

export const Flow: React.FC<FlowProps> = ({ data, accentColor }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = accentColor || palette.accent;
  const titleOpacity = useFadeIn(0, 12);
  const isHorizontal = (data.direction ?? "horizontal") === "horizontal";
  const steps = data.steps;

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
            display: "flex",
            flexDirection: isHorizontal ? "row" : "column",
            alignItems: isHorizontal ? "flex-start" : "stretch",
            justifyContent: "center",
            gap: isHorizontal ? 16 : 24,
            flex: 1,
            paddingBottom: 60,
          }}
        >
          {steps.map((step, i) => {
            const delay = i * 12 + 10;
            const s = spring({ frame: frame - delay, fps, config: { damping: 18, stiffness: 90 } });
            const opacity = interpolate(s, [0, 1], [0, 1]);
            const translateY = interpolate(s, [0, 1], [20, 0]);

            // Arrow between steps
            const arrowDelay = delay + 6;
            const arrowOpacity = interpolate(frame - arrowDelay, [0, 10], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });

            return (
              <React.Fragment key={i}>
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: 16,
                    flex: 1,
                    opacity,
                    transform: `translateY(${translateY}px)`,
                  }}
                >
                  {/* Step number circle */}
                  <div
                    style={{
                      width: 64,
                      height: 64,
                      borderRadius: 32,
                      background: `linear-gradient(135deg, ${accent}, ${hexToRgba(accent, 0.6)})`,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      boxShadow: `0 0 30px ${hexToRgba(accent, 0.3)}`,
                    }}
                  >
                    <span
                      style={{
                        color: palette.white,
                        fontSize: 28,
                        fontWeight: 800,
                      }}
                    >
                      {i + 1}
                    </span>
                  </div>

                  {/* Step label */}
                  <h3
                    style={{
                      color: palette.white,
                      fontSize: 26,
                      fontWeight: 700,
                      textAlign: "center",
                      margin: 0,
                    }}
                  >
                    {step.label}
                  </h3>

                  {/* Step description */}
                  {step.description && (
                    <p
                      style={{
                        color: palette.gray300,
                        fontSize: 20,
                        textAlign: "center",
                        margin: 0,
                        lineHeight: 1.5,
                        maxWidth: 220,
                      }}
                    >
                      {step.description}
                    </p>
                  )}
                </div>

                {/* Arrow */}
                {i < steps.length - 1 && (
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      opacity: arrowOpacity,
                      alignSelf: "center",
                      padding: isHorizontal ? "0" : "0 0",
                    }}
                  >
                    <span
                      style={{
                        color: accent,
                        fontSize: 36,
                        fontWeight: 300,
                      }}
                    >
                      {isHorizontal ? "→" : "↓"}
                    </span>
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </Background>
  );
};
