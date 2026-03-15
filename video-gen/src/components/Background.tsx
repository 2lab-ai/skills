import React from "react";
import { useCurrentFrame, interpolate } from "remotion";
import { gradients, hexToRgba, palette } from "../utils/colors";

interface BackgroundProps {
  background?: string;
  children: React.ReactNode;
}

export const Background: React.FC<BackgroundProps> = ({ background, children }) => {
  const frame = useCurrentFrame();

  // Subtle animated gradient shift
  const gradientAngle = interpolate(frame, [0, 300], [135, 145], {
    extrapolateRight: "clamp",
  });

  const bg = background || gradients.darkRadial;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        background: bg,
        position: "relative",
        overflow: "hidden",
        fontFamily: "'Pretendard', 'Noto Sans KR', system-ui, sans-serif",
      }}
    >
      {/* Subtle grid overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `
            linear-gradient(${hexToRgba(palette.accent, 0.03)} 1px, transparent 1px),
            linear-gradient(90deg, ${hexToRgba(palette.accent, 0.03)} 1px, transparent 1px)
          `,
          backgroundSize: "60px 60px",
          opacity: interpolate(frame, [0, 30], [0, 1], { extrapolateRight: "clamp" }),
        }}
      />

      {/* Floating orb */}
      <div
        style={{
          position: "absolute",
          width: 400,
          height: 400,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${hexToRgba(palette.accent, 0.08)}, transparent 70%)`,
          top: `${30 + Math.sin(frame / 60) * 5}%`,
          right: `${10 + Math.cos(frame / 80) * 3}%`,
          filter: "blur(60px)",
        }}
      />

      {/* Content */}
      <div style={{ position: "relative", zIndex: 1, width: "100%", height: "100%" }}>
        {children}
      </div>
    </div>
  );
};
