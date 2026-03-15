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
  gray300: "#d1d5db",
  gray500: "#6b7280",
  gray700: "#374151",
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
};
