import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
} from "remotion";
import type {
  FlowchartData,
  FlowchartBox,
  FlowchartDiamond,
  FlowchartEdge,
  FlowchartPathStep,
} from "../types";

const DARK = "#2B2B2B";
const ORANGE = "#F0511E";
const WHITE = "#FFFFFF";
const FONT = "Helvetica, Arial, 'Liberation Sans', sans-serif";

interface FlowchartTraceProps {
  data: FlowchartData;
  accentColor?: string;
  themeName?: string;
}

function clamp01(v: number) {
  return Math.max(0, Math.min(1, v));
}

// Polyline total length for stroke-dash draw-in
function edgeLength(points: Array<[number, number]>): number {
  let len = 0;
  for (let i = 1; i < points.length; i++) {
    const dx = points[i][0] - points[i - 1][0];
    const dy = points[i][1] - points[i - 1][1];
    len += Math.sqrt(dx * dx + dy * dy);
  }
  return len || 1;
}

export const FlowchartTrace: React.FC<FlowchartTraceProps> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width: vw, height: vh } = useVideoConfig();

  const CW = data.width ?? 860;
  const CH = data.height ?? 1220;
  const showRules = data.rules ?? true;

  const boxes: FlowchartBox[] = data.boxes ?? [];
  const diamonds: FlowchartDiamond[] = data.diamonds ?? [];
  const edges: FlowchartEdge[] = data.edges ?? [];
  const path: FlowchartPathStep[] = data.path ?? [];

  // ── Phase timing ──────────────────────────────────────────
  // Phase A (draw-in): first 35% of the scene.
  // Phase B (trace): remaining 65%.
  const total = durationInFrames;
  const phaseAEnd = Math.floor(total * 0.35);
  const phaseBStart = phaseAEnd;
  const phaseBLen = Math.max(1, total - phaseBStart);

  // ── Phase A: per-element reveal schedule ──────────────────
  const titleFade = interpolate(frame, [0, 14], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const rulesWipe = interpolate(frame, [0, 18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // Edges draw in over the middle of phase A
  const edgeDrawStart = 10;
  const edgeDrawSpan = Math.max(8, phaseAEnd - edgeDrawStart - 6);
  // Boxes pop in sequentially during phase A
  const boxStart = 14;
  const boxStagger = boxes.length > 0 ? (phaseAEnd - boxStart - 8) / boxes.length : 6;

  // ── Phase B: which step is active ─────────────────────────
  const stepCount = Math.max(1, path.length);
  const stepLen = phaseBLen / stepCount;
  const bFrame = frame - phaseBStart;
  const activeStepIdx = bFrame < 0 ? -1 : Math.min(stepCount - 1, Math.floor(bFrame / stepLen));

  // Build cumulative highlight sets: every diamond/edge belonging to a step
  // index <= activeStepIdx is "lit". Determine highlight ids per step.
  const litDiamonds = new Set<string>();
  const litEdges = new Set<string>();
  const activeBoxIds = new Set<string>();
  const resultBoxIds = new Set<string>();

  for (let i = 0; i <= activeStepIdx && i < path.length; i++) {
    const step = path[i];
    if (step.box) activeBoxIds.add(step.box);
    if (step.result) resultBoxIds.add(step.result);
    (step.diamonds ?? []).forEach((d) => litDiamonds.add(d));
    (step.edges ?? []).forEach((e) => litEdges.add(String(e)));
  }

  // Current active box (just this step) for pulse
  const currentStep = activeStepIdx >= 0 && activeStepIdx < path.length ? path[activeStepIdx] : undefined;
  const currentActiveBox = currentStep?.box;
  const currentResultBox = currentStep?.result;
  // progress within current step (0..1) for pulse phase
  const stepLocal = activeStepIdx >= 0 ? clamp01((bFrame - activeStepIdx * stepLen) / stepLen) : 0;

  // ── Renderers ─────────────────────────────────────────────
  const renderEdge = (e: FlowchartEdge, idx: number) => {
    const key = e.id ?? String(idx);
    const pts = e.points.map((p) => `${p[0]},${p[1]}`).join(" ");
    const len = edgeLength(e.points);

    // Phase A draw-in
    const t = clamp01((frame - edgeDrawStart) / edgeDrawSpan);
    const eased = Easing.out(Easing.cubic)(t);
    const dashOffset = len * (1 - eased);

    const litBySpec = litEdges.has(String(e.id)) || litEdges.has(String(idx));
    const isLit = litBySpec;
    const color = isLit ? ORANGE : e.color === "orange" ? ORANGE : DARK;
    // CRITICAL: only show the arrowhead once the line has finished drawing,
    // otherwise the triangle floats at the destination while the line is still
    // mid-draw (the "broken" look). Gate marker on draw completion.
    const drawComplete = t >= 0.98;
    const marker =
      e.arrow === false || !drawComplete
        ? undefined
        : `url(#arrow-${isLit || e.color === "orange" ? "o" : "d"})`;

    const sw = isLit ? 4 : 2;

    return (
      <polyline
        key={`edge-${key}`}
        points={pts}
        fill="none"
        stroke={color}
        strokeWidth={sw}
        strokeLinejoin="miter"
        strokeDasharray={len}
        strokeDashoffset={dashOffset}
        markerEnd={marker}
        style={{ transition: "none" }}
      />
    );
  };

  const renderBox = (b: FlowchartBox, idx: number) => {
    const style = b.style ?? "question";
    const baseStroke = style === "action" ? ORANGE : DARK;
    const baseText = style === "action" ? ORANGE : DARK;
    const fs = b.font_size ?? 22;

    // Phase A pop-in
    const delay = boxStart + idx * boxStagger;
    const s = spring({
      frame: frame - delay,
      fps,
      config: { damping: 16, stiffness: 110 },
    });
    const popScale = interpolate(s, [0, 1], [0.8, 1]);
    const popOpacity = interpolate(s, [0, 1], [0, 1]);

    const isActive = currentActiveBox === b.id;
    const isResult = currentResultBox === b.id;
    const inPath = activeBoxIds.has(b.id) || resultBoxIds.has(b.id);

    // Pulse on active / result box
    let pulse = 1;
    let glow = 0;
    if (isActive || isResult) {
      const freq = isResult ? 6 : 4;
      pulse = 1 + 0.05 * Math.sin(stepLocal * Math.PI * freq) * (1 - stepLocal * 0.3);
      glow = (isResult ? 0.9 : 0.6) * (0.5 + 0.5 * Math.sin(stepLocal * Math.PI * freq));
    }

    const stroke = inPath ? ORANGE : baseStroke;
    const textColor = inPath ? ORANGE : baseText;
    const sw = inPath ? 3 : 2;

    const cx = b.x + b.w / 2;
    const cy = b.y + b.h / 2;

    return (
      <g
        key={`box-${b.id}`}
        style={{
          opacity: popOpacity,
          transform: `translate(${cx}px, ${cy}px) scale(${popScale * pulse}) translate(${-cx}px, ${-cy}px)`,
          transformBox: "view-box",
        }}
      >
        <rect
          x={b.x}
          y={b.y}
          width={b.w}
          height={b.h}
          rx={2}
          ry={2}
          fill={WHITE}
          stroke={stroke}
          strokeWidth={sw}
          style={glow > 0 ? { filter: `drop-shadow(0 0 ${10 * glow}px ${ORANGE})` } : undefined}
        />
        <text
          x={cx}
          y={cy}
          fill={textColor}
          fontFamily={FONT}
          fontSize={fs}
          textAnchor="middle"
          dominantBaseline="central"
        >
          {b.text}
        </text>
      </g>
    );
  };

  const renderDiamond = (d: FlowchartDiamond, idx: number) => {
    const r = d.r ?? 16;
    const cx = d.x;
    const cy = d.y;
    const label = (d.label ?? "Y").toUpperCase();

    // appear with boxes during phase A (slightly after)
    const delay = boxStart + boxes.length * boxStagger * 0.5 + idx * 1.5;
    const op = interpolate(frame - delay, [0, 10], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

    const isLit = d.id ? litDiamonds.has(d.id) : false;
    // base fill: Y=orange, N=dark. When lit (chosen) → orange + glow regardless.
    let fill = label === "Y" ? ORANGE : DARK;
    let glow = 0;
    let scale = 1;
    if (isLit) {
      fill = ORANGE;
      // find if this diamond belongs to currentStep for pulse
      const inCurrent = currentStep?.diamonds?.includes(d.id ?? "") ?? false;
      if (inCurrent) {
        glow = 0.8 * (0.5 + 0.5 * Math.sin(stepLocal * Math.PI * 4));
        scale = 1 + 0.15 * Math.sin(stepLocal * Math.PI * 4);
      } else {
        glow = 0.3;
      }
    }

    const pts = `${cx},${cy - r} ${cx + r},${cy} ${cx},${cy + r} ${cx - r},${cy}`;

    return (
      <g key={`dia-${d.id ?? idx}`} style={{ opacity: op }}>
        <polygon
          points={pts}
          fill={fill}
          style={{
            transformBox: "view-box",
            transformOrigin: `${cx}px ${cy}px`,
            transform: `scale(${scale})`,
            filter: glow > 0 ? `drop-shadow(0 0 ${8 * glow}px ${ORANGE})` : undefined,
          }}
        />
        <text
          x={cx}
          y={cy}
          fill={WHITE}
          fontFamily={FONT}
          fontSize={14}
          fontWeight="bold"
          textAnchor="middle"
          dominantBaseline="central"
          style={{
            transformBox: "view-box",
            transformOrigin: `${cx}px ${cy}px`,
            transform: `scale(${scale})`,
          }}
        >
          {label}
        </text>
      </g>
    );
  };

  // Fit 860x1220 into the vertical canvas, centered
  const margin = 40;
  const availW = vw - margin * 2;
  const availH = vh - margin * 2;
  const scale = Math.min(availW / CW, availH / CH);
  const renderW = CW * scale;
  const renderH = CH * scale;

  return (
    <AbsoluteFill
      style={{
        background: WHITE,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <svg
        width={renderW}
        height={renderH}
        viewBox={`0 0 ${CW} ${CH}`}
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <marker
            id="arrow-d"
            viewBox="0 0 10 10"
            refX="8"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto-start-reverse"
          >
            <path d="M0,0 L10,5 L0,10 z" fill={DARK} />
          </marker>
          <marker
            id="arrow-o"
            viewBox="0 0 10 10"
            refX="8"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto-start-reverse"
          >
            <path d="M0,0 L10,5 L0,10 z" fill={ORANGE} />
          </marker>
        </defs>

        <rect width={CW} height={CH} fill={WHITE} />

        {/* Top / bottom orange rules — wipe in from left */}
        {showRules && (
          <>
            <rect x={40} y={34} width={(CW - 80) * rulesWipe} height={5} fill={ORANGE} />
            <rect x={40} y={CH - 44} width={(CW - 80) * rulesWipe} height={5} fill={ORANGE} />
          </>
        )}

        {/* Title */}
        {data.title && (
          <text
            x={CW / 2}
            y={72}
            fill={DARK}
            fontFamily={FONT}
            fontSize={30}
            textAnchor="middle"
            style={{ opacity: titleFade }}
          >
            {data.title}
          </text>
        )}

        {/* Edges first (behind boxes) */}
        {edges.map(renderEdge)}
        {/* Boxes */}
        {boxes.map(renderBox)}
        {/* Diamonds on top */}
        {diamonds.map(renderDiamond)}
      </svg>
    </AbsoluteFill>
  );
};
