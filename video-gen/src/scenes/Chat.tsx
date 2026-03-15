import React from "react";
import { useCurrentFrame, spring, interpolate, useVideoConfig } from "remotion";
import { Background } from "../components/Background";
import { useFadeIn } from "../utils/animations";
import type { ChatData } from "../types";
import { palette, hexToRgba } from "../utils/colors";

interface ChatProps {
  data: ChatData;
  accentColor?: string;
}

const roleConfig = {
  user: {
    align: "flex-end" as const,
    bg: (accent: string) => `linear-gradient(135deg, ${accent}, ${hexToRgba(accent, 0.7)})`,
    color: palette.white,
    label: "You",
    labelColor: (accent: string) => accent,
  },
  assistant: {
    align: "flex-start" as const,
    bg: () => hexToRgba(palette.white, 0.08),
    color: palette.white,
    label: "AI",
    labelColor: () => palette.gray300,
  },
  system: {
    align: "center" as const,
    bg: () => hexToRgba(palette.warning, 0.1),
    color: palette.warning,
    label: "System",
    labelColor: () => palette.warning,
  },
};

export const Chat: React.FC<ChatProps> = ({ data, accentColor }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = accentColor || palette.accent;
  const titleOpacity = useFadeIn(0, 12);

  return (
    <Background>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          padding: "80px 200px",
          height: "100%",
        }}
      >
        {data.title && (
          <h2
            style={{
              color: palette.white,
              fontSize: 44,
              fontWeight: 700,
              marginBottom: 40,
              opacity: titleOpacity,
              letterSpacing: "-0.02em",
              textAlign: "center",
            }}
          >
            {data.title}
          </h2>
        )}

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 20,
            flex: 1,
            justifyContent: "center",
          }}
        >
          {data.messages.map((msg, i) => {
            const delay = i * 15 + 10;
            const s = spring({
              frame: frame - delay,
              fps,
              config: { damping: 18, stiffness: 90 },
            });
            const opacity = interpolate(s, [0, 1], [0, 1]);
            const translateY = interpolate(s, [0, 1], [30, 0]);
            const config = roleConfig[msg.role];

            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: config.align,
                  opacity,
                  transform: `translateY(${translateY}px)`,
                }}
              >
                <span
                  style={{
                    color: config.labelColor(accent),
                    fontSize: 16,
                    fontWeight: 600,
                    marginBottom: 6,
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                  }}
                >
                  {msg.name || config.label}
                </span>
                <div
                  style={{
                    background: config.bg(accent),
                    padding: "18px 28px",
                    borderRadius: 20,
                    maxWidth: "75%",
                    border:
                      msg.role === "assistant"
                        ? `1px solid ${hexToRgba(palette.white, 0.1)}`
                        : "none",
                  }}
                >
                  <span
                    style={{
                      color: config.color,
                      fontSize: 26,
                      lineHeight: 1.6,
                      fontWeight: 400,
                    }}
                  >
                    {msg.content}
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
