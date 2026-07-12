// Shorts-specific layout and styling configuration
// v2: Theme system, transitions, enhanced visuals

export const SHORTS_LAYOUT = {
  width: 1080,
  height: 1920,
  visualArea: { top: 0, height: 1920 },
  captionArea: { top: 1920 - 300, height: 300 },
  progressBar: { height: 4 },
  safeArea: { top: 120, bottom: 180, horizontal: 60 },
};

// ── Theme System ──────────────────────────────────────
export type ShortsTheme = "midnight" | "ember" | "aurora" | "ivory" | "neon";

export interface ShortsThemeColors {
  background: string;
  backgroundGradientEnd: string;
  backgroundGradientMid?: string;
  text: string;
  textMuted: string;
  primary: string;
  primaryGlow: string;
  secondary: string;
  accent: string;
  success: string;
  warning: string;
}

export const SHORTS_THEMES: Record<ShortsTheme, ShortsThemeColors> = {
  midnight: {
    background: "#0a0a0f",
    backgroundGradientEnd: "#1a1a2e",
    text: "#ffffff",
    textMuted: "#8a8a9a",
    primary: "#00d4ff",
    primaryGlow: "#00d4ff",
    secondary: "#ff6b35",
    accent: "#a855f7",
    success: "#22c55e",
    warning: "#f59e0b",
  },
  ember: {
    background: "#0f0a08",
    backgroundGradientEnd: "#2a1610",
    text: "#fff5f0",
    textMuted: "#9a8a80",
    primary: "#ff6b35",
    primaryGlow: "#ff8c5a",
    secondary: "#ffd700",
    accent: "#ff3d71",
    success: "#00e676",
    warning: "#ffab00",
  },
  aurora: {
    background: "#060d16",
    backgroundGradientEnd: "#0a1628",
    backgroundGradientMid: "#0d1a2e",
    text: "#e8f4ff",
    textMuted: "#7a9ab5",
    primary: "#7dd3fc",
    primaryGlow: "#38bdf8",
    secondary: "#c084fc",
    accent: "#34d399",
    success: "#6ee7b7",
    warning: "#fbbf24",
  },
  ivory: {
    background: "#f5f0eb",
    backgroundGradientEnd: "#e8e0d8",
    text: "#1a1612",
    textMuted: "#6b5f54",
    primary: "#c05621",
    primaryGlow: "#dd6b20",
    secondary: "#2b6cb0",
    accent: "#6b46c1",
    success: "#276749",
    warning: "#b7791f",
  },
  neon: {
    background: "#0a0014",
    backgroundGradientEnd: "#140028",
    backgroundGradientMid: "#0f001e",
    text: "#ffffff",
    textMuted: "#9080b0",
    primary: "#00ff88",
    primaryGlow: "#00ff88",
    secondary: "#ff00ff",
    accent: "#ffff00",
    success: "#00ff88",
    warning: "#ff6600",
  },
};

// Default colors (backward compatible)
export const SHORTS_COLORS = SHORTS_THEMES.midnight;

export const SHORTS_FONTS = {
  primary: "'Pretendard', 'Inter', -apple-system, sans-serif",
  heading: "'Pretendard', 'Inter', -apple-system, sans-serif",
  display: "'Space Grotesk', 'Pretendard', sans-serif",
  serif: "'Noto Serif KR', 'Playfair Display', serif",
  mono: "'JetBrains Mono', 'SF Mono', Consolas, monospace",
};

// ── Transition Types ──────────────────────────────────
export type TransitionType = "cut" | "fade" | "zoom" | "slide_up" | "blur" | "glitch";

// ── Beat definition for shorts storyboard ─────────────
export interface WordTimestamp {
  word: string;
  start_seconds: number;
  end_seconds: number;
}

export interface ShortsBeat {
  id: string;
  start_seconds: number;
  end_seconds: number;
  visual: {
    type: string;
    primary_text: string;
    secondary_text?: string;
    tertiary_text?: string;
    icon?: string;
    color?: string;
    font?: "primary" | "heading" | "display" | "serif" | "mono";
    emphasis?: "glow" | "underline" | "highlight" | "shake";
    video_src?: string; // Path to video clip for video_clip visual type
    video_opacity?: number; // Background video opacity (0-1, default 0.4)
    video_start?: number; // Start time in seconds within the source video
  };
  caption_text: string;
  word_timestamps?: WordTimestamp[];
  transition?: TransitionType;
}

export interface ShortsStoryboard {
  id: string;
  title: string;
  total_duration_seconds: number;
  beats: ShortsBeat[];
  theme?: ShortsTheme;
  hook_question?: string;
  cta_text?: string;
  voiceover_path?: string;
}
