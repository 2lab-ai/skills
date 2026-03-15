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
  useSlideLeft,
  useSlideRight,
  useStaggeredSlideLeft,
  useStaggeredSlideRight,
  useElasticScale,
  useGlow,
} from "../utils/animations";
import type { ComparisonData } from "../types";
import { palette, hexToRgba, getTheme } from "../utils/colors";

interface ComparisonProps {
  data: ComparisonData;
  accentColor?: string;
  themeName?: string;
}

const ComparisonItem: React.FC<{
  text: string;
  index: number;
  side: "left" | "right";
  color: string;
  theme: ReturnType<typeof getTheme>;
}> = ({ text, index, side, color, theme }) => {
  // Always call both hooks unconditionally to satisfy Rules of Hooks
  const slideRight = useStaggeredSlideRight(index, 10);
  const slideLeft = useStaggeredSlideLeft(index, 10);
  const anim = side === "left" ? slideRight : slideLeft;

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 16,
        padding: "14px 20px",
        borderRadius: theme.borderRadius * 0.6,
        background: hexToRgba(color, 0.06),
        border: `1px solid ${hexToRgba(color, 0.12)}`,
        ...anim,
      }}
    >
      <div
        style={{
          width: 8,
          height: 8,
          borderRadius: 4,
          background: color,
          flexShrink: 0,
          boxShadow: `0 0 10px ${hexToRgba(color, 0.5)}`,
        }}
      />
      <span
        style={{
          color: theme.textPrimary,
          fontFamily: theme.fontFamily,
          fontSize: 20,
          fontWeight: 500,
          lineHeight: 1.4,
        }}
      >
        {text}
      </span>
    </div>
  );
};

export const Comparison: React.FC<ComparisonProps> = ({
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

  const leftColor = data.left.color || accent;
  const rightColor = data.right.color || theme.accentAlt;

  // Center divider animation
  const dividerScale = spring({
    frame: Math.max(0, frame - 8),
    fps,
    config: { damping: 12, stiffness: 100 },
  });
  const dividerHeight = interpolate(dividerScale, [0, 1], [0, 100]);

  // VS badge bounce
  const vsBounce = spring({
    frame: Math.max(0, frame - 15),
    fps,
    config: { damping: 6, stiffness: 180, mass: 0.5 },
  });
  const vsGlow = useGlow(70);

  // Before-after arrow
  const arrowProgress = interpolate(
    frame,
    [20, 50],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) }
  );

  // Side header animations
  const leftHeaderSlide = useSlideRight(5, 40);
  const leftHeaderFade = useFadeIn(5, 15);
  const rightHeaderSlide = useSlideLeft(5, 40);
  const rightHeaderFade = useFadeIn(5, 15);

  const isVersus = variant === "versus";
  const isBeforeAfter = variant === "before-after";

  return (
    <Background background={theme.background}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          padding: "70px 80px",
          height: "100%",
        }}
      >
        {/* Title */}
        <h2
          style={{
            color: theme.textPrimary,
            fontSize: 42,
            fontFamily: theme.headingFont,
            fontWeight: 700,
            marginBottom: 36,
            opacity: titleFade,
            letterSpacing: "-0.02em",
            textAlign: "center",
          }}
        >
          {data.title}
        </h2>

        {/* Split layout */}
        <div
          style={{
            display: "flex",
            flex: 1,
            gap: 0,
            alignItems: "stretch",
          }}
        >
          {/* LEFT SIDE */}
          <div
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              gap: 12,
              paddingRight: 40,
            }}
          >
            {/* Left header */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 14,
                marginBottom: 20,
                opacity: leftHeaderFade,
                transform: `translateX(${leftHeaderSlide}px)`,
              }}
            >
              {data.left.emoji && (
                <span style={{ fontSize: 36 }}>{data.left.emoji}</span>
              )}
              <h3
                style={{
                  color: leftColor,
                  fontFamily: theme.headingFont,
                  fontSize: 28,
                  fontWeight: 700,
                  margin: 0,
                }}
              >
                {data.left.title}
              </h3>
            </div>

            {/* Left items */}
            {data.left.items.map((item, i) => (
              <ComparisonItem
                key={i}
                text={item}
                index={i}
                side="left"
                color={leftColor}
                theme={theme}
              />
            ))}
          </div>

          {/* CENTER DIVIDER */}
          <div
            style={{
              width: isVersus ? 80 : 60,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              position: "relative",
            }}
          >
            {/* Divider line */}
            <div
              style={{
                position: "absolute",
                top: 0,
                bottom: 0,
                width: 2,
                background: `linear-gradient(180deg, transparent, ${hexToRgba(theme.textPrimary, 0.15)}, transparent)`,
                clipPath: `inset(${(100 - dividerHeight) / 2}% 0)`,
              }}
            />

            {/* VS / Arrow badge */}
            {isBeforeAfter ? (
              <div
                style={{
                  zIndex: 2,
                  opacity: arrowProgress,
                  transform: `scale(${interpolate(arrowProgress, [0, 1], [0.5, 1])})`,
                }}
              >
                <div
                  style={{
                    width: 50,
                    height: 50,
                    borderRadius: 25,
                    background: `linear-gradient(135deg, ${leftColor}, ${rightColor})`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    boxShadow: `0 0 30px ${hexToRgba(accent, 0.3)}`,
                  }}
                >
                  <span
                    style={{
                      color: "#fff",
                      fontSize: 24,
                      fontWeight: 700,
                    }}
                  >
                    {"\u2192"}
                  </span>
                </div>
              </div>
            ) : (
              <div
                style={{
                  zIndex: 2,
                  transform: `scale(${interpolate(vsBounce, [0, 1], [0, 1])})`,
                }}
              >
                <div
                  style={{
                    width: isVersus ? 72 : 52,
                    height: isVersus ? 72 : 52,
                    borderRadius: isVersus ? 36 : 26,
                    background: `linear-gradient(135deg, ${leftColor}, ${rightColor})`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    boxShadow: `0 0 ${30 + 15 * vsGlow}px ${hexToRgba(accent, 0.4)}`,
                  }}
                >
                  <span
                    style={{
                      color: "#fff",
                      fontFamily: theme.headingFont,
                      fontSize: isVersus ? 22 : 16,
                      fontWeight: 900,
                      letterSpacing: "0.05em",
                    }}
                  >
                    VS
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* RIGHT SIDE */}
          <div
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              gap: 12,
              paddingLeft: 40,
            }}
          >
            {/* Right header */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 14,
                marginBottom: 20,
                opacity: rightHeaderFade,
                transform: `translateX(${rightHeaderSlide}px)`,
              }}
            >
              {data.right.emoji && (
                <span style={{ fontSize: 36 }}>{data.right.emoji}</span>
              )}
              <h3
                style={{
                  color: rightColor,
                  fontFamily: theme.headingFont,
                  fontSize: 28,
                  fontWeight: 700,
                  margin: 0,
                }}
              >
                {data.right.title}
              </h3>
            </div>

            {/* Right items */}
            {data.right.items.map((item, i) => (
              <ComparisonItem
                key={i}
                text={item}
                index={i}
                side="right"
                color={rightColor}
                theme={theme}
              />
            ))}
          </div>
        </div>
      </div>
    </Background>
  );
};
