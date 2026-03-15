import React from "react";
import {
  useCurrentFrame,
  spring,
  interpolate,
  useVideoConfig,
  Easing,
} from "remotion";
import { Background } from "../components/Background";
import {
  useFadeIn,
  useStaggered,
  useStaggeredSlideLeft,
  useStaggeredSlideRight,
  useRevealLine,
} from "../utils/animations";
import type { TimelineData } from "../types";
import { palette, hexToRgba, getTheme } from "../utils/colors";

interface TimelineProps {
  data: TimelineData;
  accentColor?: string;
  themeName?: string;
}

export const Timeline: React.FC<TimelineProps> = ({
  data,
  accentColor,
  themeName,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName);
  const accent = accentColor || theme.accent;

  const variant = data.variant ?? "default";
  const titleFade = useFadeIn(0, 12);

  // Connecting line draws down progressively
  const lineProgress = interpolate(
    frame,
    [10, 10 + data.events.length * 20],
    [0, 100],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) }
  );

  if (variant === "horizontal") {
    return (
      <Background background={theme.background}>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            padding: "80px 80px",
            height: "100%",
          }}
        >
          {/* Title */}
          <h2
            style={{
              color: theme.textPrimary,
              fontSize: 52,
              fontWeight: 700,
              marginBottom: 60,
              opacity: titleFade,
              letterSpacing: "-0.02em",
            }}
          >
            {data.title}
          </h2>

          {/* Horizontal timeline */}
          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              flex: 1,
              position: "relative",
              paddingTop: 40,
            }}
          >
            {/* Horizontal connecting line */}
            <div
              style={{
                position: "absolute",
                top: 59,
                left: 0,
                height: 3,
                width: `${lineProgress}%`,
                background: `linear-gradient(90deg, ${accent}, ${hexToRgba(accent, 0.3)})`,
                borderRadius: 2,
              }}
            />

            {data.events.map((event, i) => {
              const delay = i * 15 + 10;
              const s = spring({
                frame: frame - delay,
                fps,
                config: { damping: 15, stiffness: 80 },
              });
              const opacity = interpolate(s, [0, 1], [0, 1]);
              const slideY = interpolate(s, [0, 1], [30, 0]);

              return (
                <div
                  key={i}
                  style={{
                    flex: 1,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: 16,
                    opacity,
                    transform: `translateY(${slideY}px)`,
                  }}
                >
                  {/* Dot */}
                  <div
                    style={{
                      width: 20,
                      height: 20,
                      borderRadius: 10,
                      background: accent,
                      boxShadow: `0 0 20px ${hexToRgba(accent, 0.5)}`,
                      zIndex: 2,
                    }}
                  />

                  {/* Emoji */}
                  {event.emoji && (
                    <span style={{ fontSize: 36 }}>{event.emoji}</span>
                  )}

                  {/* Date badge */}
                  <span
                    style={{
                      background: hexToRgba(accent, 0.15),
                      border: `1px solid ${hexToRgba(accent, 0.3)}`,
                      color: accent,
                      padding: "4px 14px",
                      borderRadius: 8,
                      fontSize: 16,
                      fontWeight: 600,
                    }}
                  >
                    {event.date}
                  </span>

                  {/* Title */}
                  <h4
                    style={{
                      color: theme.textPrimary,
                      fontSize: 22,
                      fontWeight: 700,
                      margin: 0,
                      textAlign: "center",
                    }}
                  >
                    {event.title}
                  </h4>

                  {/* Description */}
                  {event.description && (
                    <p
                      style={{
                        color: theme.textSecondary,
                        fontSize: 17,
                        margin: 0,
                        textAlign: "center",
                        lineHeight: 1.4,
                        maxWidth: 180,
                      }}
                    >
                      {event.description}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </Background>
    );
  }

  // Vertical / alternating timeline
  const isAlternating = variant === "alternating";

  return (
    <Background background={theme.background}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          padding: "70px 100px",
          height: "100%",
        }}
      >
        {/* Title */}
        <h2
          style={{
            color: theme.textPrimary,
            fontSize: 52,
            fontWeight: 700,
            marginBottom: 40,
            opacity: titleFade,
            letterSpacing: "-0.02em",
            textAlign: isAlternating ? "center" : "left",
          }}
        >
          {data.title}
        </h2>

        {/* Timeline container */}
        <div
          style={{
            position: "relative",
            flex: 1,
            display: "flex",
            flexDirection: "column",
            gap: 8,
            paddingLeft: isAlternating ? 0 : 50,
          }}
        >
          {/* Vertical connecting line */}
          <div
            style={{
              position: "absolute",
              left: isAlternating ? "50%" : 14,
              top: 0,
              width: 3,
              height: `${lineProgress}%`,
              background: `linear-gradient(180deg, ${accent}, ${hexToRgba(accent, 0.2)})`,
              borderRadius: 2,
              transform: isAlternating ? "translateX(-1.5px)" : "none",
            }}
          />

          {data.events.map((event, i) => {
            const delay = i * 14 + 10;
            const s = spring({
              frame: frame - delay,
              fps,
              config: { damping: 18, stiffness: 90 },
            });
            const opacity = interpolate(s, [0, 1], [0, 1]);

            const isLeft = isAlternating && i % 2 === 0;
            const isRight = isAlternating && i % 2 !== 0;
            const slideX = isAlternating
              ? interpolate(s, [0, 1], [isLeft ? -50 : 50, 0])
              : 0;
            const slideY = isAlternating
              ? 0
              : interpolate(s, [0, 1], [20, 0]);

            // Dot scale animation
            const dotScale = spring({
              frame: frame - delay,
              fps,
              config: { damping: 8, stiffness: 200, mass: 0.5 },
            });

            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: 24,
                  opacity,
                  transform: isAlternating
                    ? `translateX(${slideX}px)`
                    : `translateY(${slideY}px)`,
                  position: "relative",
                  flexDirection: isLeft ? "row-reverse" : "row",
                  justifyContent: isAlternating ? "center" : "flex-start",
                  minHeight: 80,
                }}
              >
                {/* Content card (left side for alternating) */}
                {isAlternating && (
                  <div style={{ flex: 1, display: "flex", justifyContent: isLeft ? "flex-end" : "flex-start" }}>
                    <div
                      style={{
                        background: hexToRgba(theme.textPrimary, 0.04),
                        border: `1px solid ${hexToRgba(theme.textPrimary, 0.08)}`,
                        borderRadius: theme.borderRadius,
                        padding: "20px 24px",
                        maxWidth: 380,
                      }}
                    >
                      {/* Emoji + Date row */}
                      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                        {event.emoji && <span style={{ fontSize: 28 }}>{event.emoji}</span>}
                        <span
                          style={{
                            background: hexToRgba(accent, 0.15),
                            border: `1px solid ${hexToRgba(accent, 0.3)}`,
                            color: accent,
                            padding: "3px 12px",
                            borderRadius: 6,
                            fontSize: 15,
                            fontWeight: 600,
                          }}
                        >
                          {event.date}
                        </span>
                      </div>
                      <h4
                        style={{
                          color: theme.textPrimary,
                          fontSize: 24,
                          fontWeight: 700,
                          margin: 0,
                          marginBottom: event.description ? 6 : 0,
                        }}
                      >
                        {event.title}
                      </h4>
                      {event.description && (
                        <p
                          style={{
                            color: theme.textSecondary,
                            fontSize: 18,
                            margin: 0,
                            lineHeight: 1.4,
                          }}
                        >
                          {event.description}
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* Dot */}
                <div
                  style={{
                    width: 30,
                    height: 30,
                    borderRadius: 15,
                    background: accent,
                    boxShadow: `0 0 24px ${hexToRgba(accent, 0.5)}`,
                    flexShrink: 0,
                    zIndex: 2,
                    transform: `scale(${interpolate(dotScale, [0, 1], [0, 1])})`,
                    position: isAlternating ? "relative" : "absolute",
                    left: isAlternating ? undefined : -50,
                    top: isAlternating ? undefined : 4,
                  }}
                />

                {/* Content card (default vertical - right side) */}
                {!isAlternating && (
                  <div
                    style={{
                      background: hexToRgba(theme.textPrimary, 0.04),
                      border: `1px solid ${hexToRgba(theme.textPrimary, 0.08)}`,
                      borderRadius: theme.borderRadius,
                      padding: "18px 24px",
                      flex: 1,
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                      {event.emoji && <span style={{ fontSize: 26 }}>{event.emoji}</span>}
                      <span
                        style={{
                          background: hexToRgba(accent, 0.15),
                          border: `1px solid ${hexToRgba(accent, 0.3)}`,
                          color: accent,
                          padding: "3px 12px",
                          borderRadius: 6,
                          fontSize: 15,
                          fontWeight: 600,
                        }}
                      >
                        {event.date}
                      </span>
                    </div>
                    <h4
                      style={{
                        color: theme.textPrimary,
                        fontSize: 24,
                        fontWeight: 700,
                        margin: 0,
                        marginBottom: event.description ? 6 : 0,
                      }}
                    >
                      {event.title}
                    </h4>
                    {event.description && (
                      <p
                        style={{
                          color: theme.textSecondary,
                          fontSize: 18,
                          margin: 0,
                          lineHeight: 1.4,
                        }}
                      >
                        {event.description}
                      </p>
                    )}
                  </div>
                )}

                {/* Spacer for the other side in alternating */}
                {isAlternating && <div style={{ flex: 1 }} />}
              </div>
            );
          })}
        </div>
      </div>
    </Background>
  );
};
