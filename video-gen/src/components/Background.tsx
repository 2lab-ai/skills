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
  const showCrt = theme.crtEffect ?? false;
  const accent = theme.accent;

  // CRT flicker: subtle random-ish opacity variation
  const flickerOpacity = showCrt
    ? 0.97 + Math.sin(frame * 7.3) * 0.015 + Math.sin(frame * 13.1) * 0.01
    : 1;

  // CRT rolling scanline band (slow moving dark band)
  const scanBandY = showCrt ? ((frame * 1.8) % 1200) - 100 : -9999;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        background: bg,
        position: "relative",
        overflow: "hidden",
        fontFamily: theme.fontFamily,
        ["--heading-font" as string]: theme.headingFont,
        ["--body-font" as string]: theme.fontFamily,
        ["--mono-font" as string]: theme.monoFont,
      }}
    >
      {/* Subtle grid overlay (theme-dependent) */}
      {showGrid && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage: `
              linear-gradient(${hexToRgba(accent, 0.05)} 1px, transparent 1px),
              linear-gradient(90deg, ${hexToRgba(accent, 0.05)} 1px, transparent 1px)
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

      {/* Content with CRT flicker */}
      <div style={{
        position: "relative",
        zIndex: 1,
        width: "100%",
        height: "100%",
        opacity: flickerOpacity,
      }}>
        {children}
      </div>

      {/* ═══════════════════════════════════════════════ */}
      {/* CRT EFFECTS OVERLAY (evangelion theme)          */}
      {/* ═══════════════════════════════════════════════ */}

      {showCrt && (
        <>
          {/* 1. SCANLINES — thin horizontal lines every 3px */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              zIndex: 10,
              backgroundImage: `repeating-linear-gradient(
                0deg,
                transparent 0px,
                transparent 2px,
                rgba(0,0,0,0.15) 2px,
                rgba(0,0,0,0.15) 3px
              )`,
              backgroundSize: "100% 3px",
              pointerEvents: "none",
            }}
          />

          {/* 2. RGB SUB-PIXEL pattern — faint vertical RGB stripes */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              zIndex: 10,
              backgroundImage: `repeating-linear-gradient(
                90deg,
                rgba(255,0,0,0.03) 0px,
                rgba(0,255,0,0.03) 1px,
                rgba(0,100,255,0.03) 2px,
                transparent 3px
              )`,
              backgroundSize: "3px 100%",
              pointerEvents: "none",
            }}
          />

          {/* 3. ROLLING SCAN BAND — dark band that slowly moves down */}
          <div
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: scanBandY,
              height: 80,
              zIndex: 11,
              background: `linear-gradient(
                180deg,
                transparent 0%,
                rgba(0,0,0,0.08) 30%,
                rgba(0,0,0,0.12) 50%,
                rgba(0,0,0,0.08) 70%,
                transparent 100%
              )`,
              pointerEvents: "none",
            }}
          />

          {/* 4. VIGNETTE — dark edges */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              zIndex: 12,
              background: `radial-gradient(
                ellipse 70% 65% at 50% 50%,
                transparent 0%,
                transparent 55%,
                rgba(0,0,0,0.25) 80%,
                rgba(0,0,0,0.6) 100%
              )`,
              pointerEvents: "none",
            }}
          />

          {/* 5. EDGE GLOW — faint accent color at top/bottom edges (monitor bezel reflection) */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              zIndex: 12,
              borderTop: `1px solid ${hexToRgba(accent, 0.3)}`,
              borderBottom: `1px solid ${hexToRgba(accent, 0.2)}`,
              boxShadow: `inset 0 2px 30px ${hexToRgba(accent, 0.05)}, inset 0 -2px 30px ${hexToRgba(accent, 0.03)}`,
              pointerEvents: "none",
            }}
          />

          {/* 6. NOISE grain — SVG filter */}
          <svg style={{ position: "absolute", width: 0, height: 0 }}>
            <defs>
              <filter id="crt-noise">
                <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" seed={frame % 60} />
                <feColorMatrix type="saturate" values="0" />
              </filter>
            </defs>
          </svg>
          <div
            style={{
              position: "absolute",
              inset: 0,
              zIndex: 10,
              filter: "url(#crt-noise)",
              opacity: 0.03,
              pointerEvents: "none",
              mixBlendMode: "overlay",
            }}
          />

          {/* 7. CHROMATIC ABERRATION — slight red/blue shift at edges */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              zIndex: 9,
              boxShadow: `
                inset 2px 0 8px rgba(255,0,0,0.04),
                inset -2px 0 8px rgba(0,100,255,0.04)
              `,
              pointerEvents: "none",
            }}
          />

          {/* 8. CORNER BRACKETS — NERV style targeting brackets */}
          <svg
            viewBox="0 0 1920 1080"
            style={{ position: "absolute", inset: 0, zIndex: 13, pointerEvents: "none" }}
          >
            {/* Top-left bracket */}
            <path d="M 40,40 L 40,80 M 40,40 L 80,40" stroke={hexToRgba(accent, 0.4)} strokeWidth={1.5} fill="none" />
            {/* Top-right bracket */}
            <path d="M 1880,40 L 1880,80 M 1880,40 L 1840,40" stroke={hexToRgba(accent, 0.4)} strokeWidth={1.5} fill="none" />
            {/* Bottom-left bracket */}
            <path d="M 40,1040 L 40,1000 M 40,1040 L 80,1040" stroke={hexToRgba(accent, 0.4)} strokeWidth={1.5} fill="none" />
            {/* Bottom-right bracket */}
            <path d="M 1880,1040 L 1880,1000 M 1880,1040 L 1840,1040" stroke={hexToRgba(accent, 0.4)} strokeWidth={1.5} fill="none" />
            {/* Center crosshair */}
            <line x1={950} y1={530} x2={970} y2={530} stroke={hexToRgba(accent, 0.15)} strokeWidth={1} />
            <line x1={960} y1={520} x2={960} y2={540} stroke={hexToRgba(accent, 0.15)} strokeWidth={1} />
          </svg>
        </>
      )}
    </div>
  );
};
