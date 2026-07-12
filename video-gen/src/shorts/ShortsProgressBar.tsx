import React from "react";
import { ShortsThemeColors, SHORTS_THEMES } from "./ShortsConfig";

interface ShortsProgressBarProps {
  progress: number; // 0-1
  scale: number;
  height?: number;
  theme?: ShortsThemeColors;
}

export const ShortsProgressBar: React.FC<ShortsProgressBarProps> = ({
  progress,
  scale,
  height = 4,
  theme: themeProp,
}) => {
  const theme = themeProp || SHORTS_THEMES.midnight;

  return (
    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        right: 0,
        height: height * scale,
        background: `${theme.text}10`,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          width: `${progress * 100}%`,
          height: "100%",
          background: `linear-gradient(90deg, ${theme.primary}, ${theme.accent})`,
          boxShadow: `0 0 10px ${theme.primary}50`,
        }}
      />
    </div>
  );
};
