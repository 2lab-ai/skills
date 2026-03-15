import React from "react";
import { useCurrentFrame, interpolate } from "remotion";
import { hexToRgba, getTheme } from "../utils/colors";

interface BackgroundProps {
  background?: string;
  themeName?: string;
  children: React.ReactNode;
}

export const Background: React.FC<BackgroundProps> = ({ background, themeName, children }) => {
  const frame = useCurrentFrame();
  const theme = getTheme(themeName);
  const bg = background || theme.background;
  const showGrid = theme.overlayGrid;
  const showOrb = theme.orbEffect;
  const accent = theme.accent;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        background: bg,
        position: "relative",
        overflow: "hidden",
        fontFamily: theme.fontFamily,
      }}
    >
      {/* Subtle grid overlay (theme-dependent) */}
      {showGrid && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage: `
              linear-gradient(${hexToRgba(accent, 0.03)} 1px, transparent 1px),
              linear-gradient(90deg, ${hexToRgba(accent, 0.03)} 1px, transparent 1px)
            `,
            backgroundSize: "60px 60px",
            opacity: interpolate(frame, [0, 30], [0, 1], { extrapolateRight: "clamp" }),
          }}
        />
      )}

      {/* Floating orb (theme-dependent) */}
      {showOrb && (
        <div
          style={{
            position: "absolute",
            width: 400,
            height: 400,
            borderRadius: "50%",
            background: `radial-gradient(circle, ${hexToRgba(accent, 0.08)}, transparent 70%)`,
            top: `${30 + Math.sin(frame / 60) * 5}%`,
            right: `${10 + Math.cos(frame / 80) * 3}%`,
            filter: "blur(60px)",
          }}
        />
      )}

      {/* Second orb for depth */}
      {showOrb && (
        <div
          style={{
            position: "absolute",
            width: 300,
            height: 300,
            borderRadius: "50%",
            background: `radial-gradient(circle, ${hexToRgba(theme.accentAlt, 0.06)}, transparent 70%)`,
            bottom: `${20 + Math.cos(frame / 70) * 4}%`,
            left: `${5 + Math.sin(frame / 90) * 3}%`,
            filter: "blur(80px)",
          }}
        />
      )}

      {/* Content */}
      <div style={{ position: "relative", zIndex: 1, width: "100%", height: "100%" }}>
        {children}
      </div>
    </div>
  );
};
