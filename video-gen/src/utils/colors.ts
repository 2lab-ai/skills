export const palette = {
  dark: "#0f0f23",
  darkAlt: "#1a1a2e",
  accent: "#00d4ff",
  accentAlt: "#7c3aed",
  success: "#10b981",
  warning: "#f59e0b",
  error: "#ef4444",
  white: "#ffffff",
  gray100: "#f3f4f6",
  gray200: "#e5e7eb",
  gray300: "#d1d5db",
  gray400: "#9ca3af",
  gray500: "#6b7280",
  gray600: "#4b5563",
  gray700: "#374151",
  gray800: "#1f2937",
  gray900: "#111827",
};

export function hexToRgba(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

export const gradients = {
  darkRadial: `radial-gradient(ellipse at 30% 20%, ${hexToRgba("#1e3a5f", 0.4)} 0%, ${palette.dark} 70%)`,
  accent: `linear-gradient(135deg, ${palette.accent}, ${palette.accentAlt})`,
  subtle: `linear-gradient(180deg, ${palette.darkAlt}, ${palette.dark})`,
  warmRadial: `radial-gradient(ellipse at 50% 30%, ${hexToRgba("#5f3a1e", 0.4)} 0%, #1a1008 70%)`,
  coolRadial: `radial-gradient(ellipse at 40% 40%, ${hexToRgba("#1e3a5f", 0.3)} 0%, ${hexToRgba("#2e1a4f", 0.3)} 50%, #0a0a1a 100%)`,
  sunset: `linear-gradient(135deg, #1a0a2e, #2d1b4e, #1a2d4e)`,
  aurora: `linear-gradient(160deg, #0a1628, #0d2137, #0a2818, #0a1628)`,
  neon: `radial-gradient(ellipse at 50% 50%, ${hexToRgba("#ff00ff", 0.1)} 0%, ${hexToRgba("#00ffff", 0.05)} 50%, #0a0a0a 100%)`,
};

// ============================================================
// THEME SYSTEM
// ============================================================

export type ThemeName = "default" | "notion" | "minimal" | "cinematic" | "playful" | "neon" | "warm" | "nature";

export interface Theme {
  name: ThemeName;
  background: string;
  cardBg: string;
  cardBorder: string;
  textPrimary: string;
  textSecondary: string;
  accent: string;
  accentAlt: string;
  fontFamily: string;
  borderRadius: number;
  overlayGrid: boolean;
  orbEffect: boolean;
}

export const themes: Record<ThemeName, Theme> = {
  default: {
    name: "default",
    background: gradients.darkRadial,
    cardBg: hexToRgba(palette.white, 0.04),
    cardBorder: hexToRgba(palette.white, 0.08),
    textPrimary: palette.white,
    textSecondary: palette.gray300,
    accent: "#00d4ff",
    accentAlt: "#7c3aed",
    fontFamily: "'Pretendard', 'Noto Sans KR', system-ui, sans-serif",
    borderRadius: 20,
    overlayGrid: true,
    orbEffect: true,
  },
  notion: {
    name: "notion",
    background: "#191919",
    cardBg: hexToRgba(palette.white, 0.05),
    cardBorder: hexToRgba(palette.white, 0.1),
    textPrimary: "#ebebeb",
    textSecondary: "#999999",
    accent: "#eb5757",
    accentAlt: "#2f80ed",
    fontFamily: "'Pretendard', 'Noto Sans KR', Georgia, serif",
    borderRadius: 8,
    overlayGrid: false,
    orbEffect: false,
  },
  minimal: {
    name: "minimal",
    background: "#fafafa",
    cardBg: "#ffffff",
    cardBorder: "#e5e5e5",
    textPrimary: "#1a1a1a",
    textSecondary: "#737373",
    accent: "#0066ff",
    accentAlt: "#6366f1",
    fontFamily: "'Pretendard', 'Noto Sans KR', 'Helvetica Neue', sans-serif",
    borderRadius: 12,
    overlayGrid: false,
    orbEffect: false,
  },
  cinematic: {
    name: "cinematic",
    background: gradients.coolRadial,
    cardBg: hexToRgba("#ffffff", 0.03),
    cardBorder: hexToRgba("#ffffff", 0.06),
    textPrimary: "#f0e6d2",
    textSecondary: "#a89b8c",
    accent: "#e8a838",
    accentAlt: "#c44b2f",
    fontFamily: "'Pretendard', 'Noto Serif KR', Georgia, serif",
    borderRadius: 4,
    overlayGrid: false,
    orbEffect: true,
  },
  playful: {
    name: "playful",
    background: `linear-gradient(135deg, #1a1040, #2a1050, #1a2060)`,
    cardBg: hexToRgba("#ffffff", 0.08),
    cardBorder: hexToRgba("#ffffff", 0.15),
    textPrimary: "#ffffff",
    textSecondary: "#d4b8ff",
    accent: "#ff6b9d",
    accentAlt: "#c084fc",
    fontFamily: "'Pretendard', 'Noto Sans KR', system-ui, sans-serif",
    borderRadius: 24,
    overlayGrid: false,
    orbEffect: true,
  },
  neon: {
    name: "neon",
    background: "#050505",
    cardBg: hexToRgba("#ffffff", 0.02),
    cardBorder: hexToRgba("#00ffff", 0.2),
    textPrimary: "#ffffff",
    textSecondary: "#888888",
    accent: "#00ffcc",
    accentAlt: "#ff00ff",
    fontFamily: "'Pretendard', 'Noto Sans KR', monospace",
    borderRadius: 2,
    overlayGrid: true,
    orbEffect: true,
  },
  warm: {
    name: "warm",
    background: gradients.warmRadial,
    cardBg: hexToRgba("#ffffff", 0.05),
    cardBorder: hexToRgba("#d4a574", 0.2),
    textPrimary: "#f5e6d3",
    textSecondary: "#c4a882",
    accent: "#ff8c42",
    accentAlt: "#d45b0b",
    fontFamily: "'Pretendard', 'Noto Serif KR', Georgia, serif",
    borderRadius: 16,
    overlayGrid: false,
    orbEffect: true,
  },
  nature: {
    name: "nature",
    background: gradients.aurora,
    cardBg: hexToRgba("#ffffff", 0.04),
    cardBorder: hexToRgba("#4ade80", 0.15),
    textPrimary: "#e2f5e9",
    textSecondary: "#86d99b",
    accent: "#4ade80",
    accentAlt: "#22d3ee",
    fontFamily: "'Pretendard', 'Noto Sans KR', system-ui, sans-serif",
    borderRadius: 16,
    overlayGrid: false,
    orbEffect: true,
  },
};

export function getTheme(name?: string): Theme {
  if (!name || !(name in themes)) return themes.default;
  return themes[name as ThemeName];
}
