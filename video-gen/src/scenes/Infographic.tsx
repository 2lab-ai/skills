import React from "react";
import { useCurrentFrame, spring, useVideoConfig } from "remotion";
import { Background } from "../components/Background";
import type { InfographicData, InfographicElement } from "../types";
import { getTheme } from "../utils/colors";

// ── Canvas constants ──
const VW = 1920;
const VH = 1080;
const X = (p: number) => (p / 100) * VW;
const Y = (p: number) => (p / 100) * VH;
const STROKE = "#2d2d2d";
const SW = 2.5;
const FONT = "'Inter','Pretendard','Noto Sans KR',sans-serif";

interface Props {
  data: InfographicData;
  accentColor?: string;
  themeName?: string;
}

// ── Animation helper (translate-only, avoids SVG scale-origin issues) ──
function anim(frame: number, fps: number, delay = 0, type = "fadeIn") {
  const f = Math.max(0, frame - delay);
  const s = spring({ frame: f, fps, config: { damping: 16, stiffness: 80 } });
  let o = s, tx = 0, ty = 0;
  switch (type) {
    case "slideUp":    ty = (1 - s) * 40; break;
    case "slideDown":  ty = -(1 - s) * 40; break;
    case "slideLeft":  tx = (1 - s) * 60; break;
    case "slideRight": tx = -(1 - s) * 60; break;
    case "scaleIn":    ty = (1 - s) * 25; break;
    case "pop": {
      const p = spring({ frame: f, fps, config: { damping: 8, stiffness: 200 } });
      o = p; ty = (1 - p) * 15; break;
    }
  }
  return { o, t: `translate(${tx},${ty})` };
}

// ── Rect ──
function ERect(el: any, frame: number, fps: number) {
  const a = anim(frame, fps, el.delay, el.animation);
  const x = X(el.x), y = Y(el.y), w = X(el.width), h = Y(el.height);
  return (
    <g key={el.id} opacity={a.o} transform={a.t}>
      <rect x={x} y={y} width={w} height={h} rx={el.radius ?? 8}
        fill={el.fill} stroke={el.stroke ?? STROKE} strokeWidth={el.strokeWidth ?? SW} />
      {el.label && (
        <text x={x + w / 2} y={y + h / 2} textAnchor="middle" dominantBaseline="central"
          fill={el.labelColor ?? STROKE} fontSize={el.labelSize ?? 22} fontWeight={600} fontFamily={FONT}>
          {el.label}
        </text>
      )}
    </g>
  );
}

// ── Face (circle character with expression) ──
function EFace(el: any, frame: number, fps: number) {
  const a = anim(frame, fps, el.delay, el.animation);
  const cx = X(el.x), cy = Y(el.y), r = X(el.size) / 2;
  const eR = r * 0.09, eY = cy - r * 0.18, eG = r * 0.32;
  const mY = cy + r * 0.28, mw = r * 0.3;
  const mouths: Record<string, string> = {
    happy:   `M${cx - mw},${mY} Q${cx},${mY + r * 0.35} ${cx + mw},${mY}`,
    sad:     `M${cx - mw},${mY + r * 0.12} Q${cx},${mY - r * 0.2} ${cx + mw},${mY + r * 0.12}`,
    neutral: `M${cx - mw},${mY} L${cx + mw},${mY}`,
    worried: `M${cx - mw},${mY} Q${cx - mw * 0.3},${mY - r * 0.1} ${cx},${mY + r * 0.05} Q${cx + mw * 0.3},${mY + r * 0.15} ${cx + mw},${mY}`,
    angry:   `M${cx - mw},${mY + r * 0.08} Q${cx},${mY - r * 0.15} ${cx + mw},${mY + r * 0.08}`,
  };
  return (
    <g key={el.id} opacity={a.o} transform={a.t}>
      <circle cx={cx} cy={cy} r={r} fill={el.color} stroke={STROKE} strokeWidth={SW} />
      <circle cx={cx - eG} cy={eY} r={eR} fill={STROKE} />
      <circle cx={cx + eG} cy={eY} r={eR} fill={STROKE} />
      {el.expression === "surprised"
        ? <ellipse cx={cx} cy={mY} rx={r * 0.12} ry={r * 0.18} fill={STROKE} />
        : <path d={mouths[el.expression] ?? mouths.neutral} fill="none" stroke={STROKE} strokeWidth={SW} strokeLinecap="round" />}
    </g>
  );
}

// ── Battery ──
function EBattery(el: any, frame: number, fps: number) {
  const a = anim(frame, fps, el.delay, el.animation);
  const x = X(el.x), y = Y(el.y), w = X(el.width), h = Y(el.height);
  const capW = w * 0.08, bodyW = w - capW;
  const pad = h * 0.12, cells = 4, gap = 4;
  const cW = (bodyW - pad * 2 - (cells - 1) * gap) / cells;
  const filled = Math.round(el.level * cells);
  return (
    <g key={el.id} opacity={a.o} transform={a.t}>
      <rect x={x} y={y} width={bodyW} height={h} rx={6} fill="#f5f0e0" stroke={STROKE} strokeWidth={SW} />
      <rect x={x + bodyW} y={y + h * 0.28} width={capW} height={h * 0.44} rx={2} fill={STROKE} />
      {Array.from({ length: cells }).map((_, i) => {
        const cs = spring({ frame: Math.max(0, frame - (el.delay ?? 0) - i * 3), fps, config: { damping: 14, stiffness: 100 } });
        return (
          <rect key={i} x={x + pad + i * (cW + gap)} y={y + pad} width={cW} height={h - pad * 2} rx={3}
            fill={i < filled ? el.color : "rgba(0,0,0,0.06)"} opacity={i < filled ? cs : 0.3} />
        );
      })}
    </g>
  );
}

// ── Bar Stack ──
function EBarStack(el: any, frame: number, fps: number) {
  const a = anim(frame, fps, el.delay, el.animation);
  const ax = X(el.x), ay = Y(el.y), mW = X(el.maxWidth);
  const bH = Y(el.barHeight), gap = Y(el.gap);
  const bAlign = el.barAlign ?? "center";
  return (
    <g key={el.id} opacity={a.o} transform={a.t}>
      {(el.bars as any[]).map((bar, i) => {
        const bs = spring({ frame: Math.max(0, frame - (el.delay ?? 0) - i * 5), fps, config: { damping: 14, stiffness: 80 } });
        const bw = (bar.width / 100) * mW;
        const bx = bAlign === "center" ? ax - bw / 2 : bAlign === "right" ? ax + mW / 2 - bw : ax - mW / 2;
        const by = el.align === "top" ? ay + i * (bH + gap) : ay - (i + 1) * (bH + gap);
        return (
          <g key={i} opacity={bs}>
            <rect x={bx} y={by} width={bw * bs} height={bH} rx={4} fill={bar.color} stroke={STROKE} strokeWidth={SW} />
          </g>
        );
      })}
    </g>
  );
}

// ── Arrow ──
function EArrow(el: any, frame: number, fps: number) {
  const a = anim(frame, fps, el.delay, el.animation);
  const x1 = X(el.x), y1 = Y(el.y), x2 = X(el.toX), y2 = Y(el.toY);
  const col = el.color ?? STROKE, hl = 14;
  const ang = Math.atan2(y2 - y1, x2 - x1);
  return (
    <g key={el.id} opacity={a.o} transform={a.t}>
      <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={col} strokeWidth={el.strokeWidth ?? SW}
        strokeDasharray={el.dashed ? "8,6" : undefined} />
      <polygon fill={col} points={
        `${x2},${y2} ${x2 - hl * Math.cos(ang - Math.PI / 6)},${y2 - hl * Math.sin(ang - Math.PI / 6)} ${x2 - hl * Math.cos(ang + Math.PI / 6)},${y2 - hl * Math.sin(ang + Math.PI / 6)}`
      } />
    </g>
  );
}

// ── Bubble (speech bubble) ──
function EBubble(el: any, frame: number, fps: number) {
  const a = anim(frame, fps, el.delay, el.animation);
  const x = X(el.x), y = Y(el.y), w = X(el.width), h = Y(el.height);
  const fill = el.fill ?? "#f5f0e0", stroke = el.stroke ?? STROKE;
  const dir = el.pointerDirection ?? "down", ps = 14;
  const cx = x + w / 2, btm = y + h, top = y;

  let pp = "";
  switch (dir) {
    case "down":  pp = `${cx - ps},${btm} ${cx},${btm + ps * 1.5} ${cx + ps},${btm}`; break;
    case "up":    pp = `${cx - ps},${top} ${cx},${top - ps * 1.5} ${cx + ps},${top}`; break;
    case "left":  pp = `${x},${y + h / 2 - ps} ${x - ps * 1.5},${y + h / 2} ${x},${y + h / 2 + ps}`; break;
    case "right": pp = `${x + w},${y + h / 2 - ps} ${x + w + ps * 1.5},${y + h / 2} ${x + w},${y + h / 2 + ps}`; break;
  }

  const lines = el.text.split("\n");
  const fs = el.fontSize ?? 22, lh = fs * 1.4;
  const tY = y + h / 2 - ((lines.length - 1) * lh) / 2;

  return (
    <g key={el.id} opacity={a.o} transform={a.t}>
      <rect x={x} y={y} width={w} height={h} rx={8} fill={fill} stroke={stroke} strokeWidth={SW} />
      <polygon points={pp} fill={fill} stroke={stroke} strokeWidth={SW} />
      {/* Cover border where pointer meets rect */}
      {dir === "down" && <line x1={cx - ps + 1} y1={btm} x2={cx + ps - 1} y2={btm} stroke={fill} strokeWidth={4} />}
      {dir === "up" && <line x1={cx - ps + 1} y1={top} x2={cx + ps - 1} y2={top} stroke={fill} strokeWidth={4} />}
      {dir === "left" && <line x1={x} y1={y + h / 2 - ps + 1} x2={x} y2={y + h / 2 + ps - 1} stroke={fill} strokeWidth={4} />}
      {dir === "right" && <line x1={x + w} y1={y + h / 2 - ps + 1} x2={x + w} y2={y + h / 2 + ps - 1} stroke={fill} strokeWidth={4} />}
      {lines.map((line: string, i: number) => (
        <text key={i} x={cx} y={tY + i * lh} textAnchor="middle" dominantBaseline="central"
          fill={el.textColor ?? STROKE} fontSize={fs} fontWeight={600} fontFamily={FONT}>
          {line}
        </text>
      ))}
    </g>
  );
}

// ── Text ──
function EText(el: any, frame: number, fps: number) {
  const a = anim(frame, fps, el.delay, el.animation);
  const x = X(el.x), y = Y(el.y);
  const anchor = el.align === "left" ? "start" : el.align === "right" ? "end" : "middle";
  const lines = el.text.split("\n");
  const fs = el.fontSize ?? 32, lh = fs * 1.3;
  return (
    <g key={el.id} opacity={a.o} transform={a.t}>
      {lines.map((line: string, i: number) => (
        <text key={i} x={x} y={y + i * lh} textAnchor={anchor} dominantBaseline="central"
          fill={el.color ?? STROKE} fontSize={fs} fontWeight={el.fontWeight ?? 700} fontFamily={FONT}>
          {line}
        </text>
      ))}
    </g>
  );
}

// ── Line ──
function ELine(el: any, frame: number, fps: number) {
  const a = anim(frame, fps, el.delay, el.animation);
  const x1 = X(el.x), y1 = Y(el.y), x2 = X(el.toX), y2 = Y(el.toY);
  const ds = spring({ frame: Math.max(0, frame - (el.delay ?? 0)), fps, config: { damping: 20, stiffness: 60 } });
  return (
    <g key={el.id} opacity={a.o}>
      <line x1={x1} y1={y1} x2={x1 + (x2 - x1) * ds} y2={y1 + (y2 - y1) * ds}
        stroke={el.color ?? STROKE} strokeWidth={el.strokeWidth ?? SW}
        strokeDasharray={el.dashed ? "8,6" : undefined} />
      <circle cx={x1} cy={y1} r={4} fill={el.color ?? STROKE} />
    </g>
  );
}

// ── Connector (L-shaped line with dots) ──
function EConnector(el: any, frame: number, fps: number) {
  const a = anim(frame, fps, el.delay, el.animation);
  const x1 = X(el.x), y1 = Y(el.y), x2 = X(el.toX), y2 = Y(el.toY);
  const col = el.color ?? STROKE;
  const path = (el.bendDirection ?? "vertical-first") === "vertical-first"
    ? `M${x1},${y1} L${x1},${y2} L${x2},${y2}`
    : `M${x1},${y1} L${x2},${y1} L${x2},${y2}`;
  return (
    <g key={el.id} opacity={a.o} transform={a.t}>
      <path d={path} fill="none" stroke={col} strokeWidth={el.strokeWidth ?? SW} />
      {el.dot !== false && (
        <>
          <circle cx={x1} cy={y1} r={4.5} fill={col} />
          <circle cx={x2} cy={y2} r={4.5} fill={col} />
        </>
      )}
    </g>
  );
}

// ── Dispatcher ──
function renderEl(el: InfographicElement, frame: number, fps: number) {
  switch ((el as any).type) {
    case "rect":      return ERect(el, frame, fps);
    case "face":      return EFace(el, frame, fps);
    case "battery":   return EBattery(el, frame, fps);
    case "barStack":  return EBarStack(el, frame, fps);
    case "arrow":     return EArrow(el, frame, fps);
    case "bubble":    return EBubble(el, frame, fps);
    case "text":      return EText(el, frame, fps);
    case "line":      return ELine(el, frame, fps);
    case "connector": return EConnector(el, frame, fps);
    default:          return null;
  }
}

// ── Main Component ──
export const Infographic: React.FC<Props> = ({ data, accentColor, themeName }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName);
  const bg = data.background ?? theme.background;

  return (
    <Background background={bg} themeName={themeName}>
      <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" height="100%"
        style={{ position: "absolute", inset: 0 }}>
        {data.elements.map((el) => renderEl(el, frame, fps))}
      </svg>
    </Background>
  );
};
