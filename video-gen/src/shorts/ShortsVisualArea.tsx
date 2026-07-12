import React from "react";
import { interpolate, spring, OffthreadVideo, staticFile } from "remotion";
import { SHORTS_FONTS, ShortsBeat, ShortsThemeColors, SHORTS_THEMES } from "./ShortsConfig";

interface ShortsVisualAreaProps {
  beat: ShortsBeat;
  frame: number;
  fps: number;
  scale: number;
  theme?: ShortsThemeColors;
}

const getColor = (theme: ShortsThemeColors, c?: string) => {
  const map: Record<string, string> = {
    primary: theme.primary,
    secondary: theme.secondary,
    accent: theme.accent,
    success: theme.success,
    warning: theme.warning,
  };
  return map[c || "primary"] || theme.primary;
};

const getFont = (fontKey?: string) => {
  const map: Record<string, string> = SHORTS_FONTS;
  return map[fontKey || "heading"] || SHORTS_FONTS.heading;
};

export const ShortsVisualArea: React.FC<ShortsVisualAreaProps> = ({
  beat,
  frame,
  fps,
  scale,
  theme: themeProp,
}) => {
  const theme = themeProp || SHORTS_THEMES.midnight;
  const { visual } = beat;
  const color = getColor(theme, visual.color);
  const fontFamily = getFont(visual.font);

  // Entry animation
  const entryProgress = spring({ fps, frame, config: { damping: 14, stiffness: 100 } });
  const entryScale = interpolate(entryProgress, [0, 1], [0.88, 1]);
  const entryOpacity = interpolate(entryProgress, [0, 1], [0, 1]);

  const containerStyle: React.CSSProperties = {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    width: "100%",
    height: "100%",
    transform: `scale(${entryScale})`,
    opacity: entryOpacity,
    padding: `${80 * scale}px ${50 * scale}px`,
  };

  const props = { color, frame, fps, scale, theme, fontFamily };

  switch (visual.type) {
    case "big_number":
      return (
        <div style={containerStyle}>
          <BigNumberVisual
            number={visual.primary_text}
            label={visual.secondary_text}
            {...props}
          />
        </div>
      );

    case "comparison":
      return (
        <div style={containerStyle}>
          <ComparisonVisual
            left={visual.primary_text}
            right={visual.secondary_text || ""}
            label={visual.tertiary_text}
            {...props}
          />
        </div>
      );

    case "text_highlight":
      return (
        <div style={containerStyle}>
          <TextHighlightVisual
            text={visual.primary_text}
            subtext={visual.secondary_text}
            emphasis={visual.emphasis}
            {...props}
          />
        </div>
      );

    case "simple_flow":
      return (
        <div style={containerStyle}>
          <SimpleFlowVisual
            steps={visual.primary_text.split("→").map((s) => s.trim())}
            {...props}
          />
        </div>
      );

    case "icon_stat":
      return (
        <div style={containerStyle}>
          <IconStatVisual
            icon={visual.icon || "🔥"}
            stat={visual.primary_text}
            label={visual.secondary_text}
            {...props}
          />
        </div>
      );

    case "key_point":
      return (
        <div style={containerStyle}>
          <KeyPointVisual
            point={visual.primary_text}
            subpoint={visual.secondary_text}
            {...props}
          />
        </div>
      );

    case "question":
      return (
        <div style={containerStyle}>
          <QuestionVisual question={visual.primary_text} {...props} />
        </div>
      );

    case "stat_row":
      return (
        <div style={containerStyle}>
          <StatRowVisual
            items={visual.primary_text.split("|").map((s) => {
              const [label, value] = s.trim().split(":");
              return { label: label?.trim() || "", value: value?.trim() || "" };
            })}
            {...props}
          />
        </div>
      );

    case "list":
      return (
        <div style={containerStyle}>
          <ListVisual
            title={visual.primary_text}
            items={visual.secondary_text ? visual.secondary_text.split("\n").filter(Boolean) : []}
            {...props}
          />
        </div>
      );

    case "countdown":
      return (
        <div style={containerStyle}>
          <CountdownVisual
            number={visual.primary_text}
            label={visual.secondary_text}
            {...props}
          />
        </div>
      );

    case "quote":
      return (
        <div style={containerStyle}>
          <QuoteVisual
            quote={visual.primary_text}
            author={visual.secondary_text}
            {...props}
          />
        </div>
      );

    case "morphing_text":
      return (
        <div style={containerStyle}>
          <MorphingTextVisual
            textA={visual.primary_text}
            textB={visual.secondary_text || ""}
            label={visual.tertiary_text}
            {...props}
          />
        </div>
      );

    case "equation":
      return (
        <div style={containerStyle}>
          <EquationVisual
            equation={visual.primary_text}
            label={visual.secondary_text}
            {...props}
          />
        </div>
      );

    case "gradient_text":
      return (
        <div style={containerStyle}>
          <GradientTextVisual
            text={visual.primary_text}
            subtext={visual.secondary_text}
            {...props}
          />
        </div>
      );

    case "video_clip":
      return (
        <VideoClipVisual
          beat={beat}
          frame={frame}
          fps={fps}
          scale={scale}
          theme={theme}
          entryScale={entryScale}
          entryOpacity={entryOpacity}
        />
      );

    default:
      return (
        <div style={containerStyle}>
          <TextHighlightVisual
            text={visual.primary_text}
            subtext={visual.secondary_text}
            emphasis={visual.emphasis}
            {...props}
          />
        </div>
      );
  }
};

// ── Common props type ─────────────────────────────────────
interface VisualProps {
  color: string;
  frame: number;
  fps: number;
  scale: number;
  theme: ShortsThemeColors;
  fontFamily: string;
}

// ── Visual Sub-Components ──────────────────────────────────

const BigNumberVisual: React.FC<{ number: string; label?: string } & VisualProps> = ({
  number: num,
  label,
  color,
  frame,
  fps,
  scale,
  theme,
  fontFamily,
}) => {
  const numericValue = parseFloat(num.replace(/[^0-9.]/g, ""));
  const prefix = num.match(/^[^0-9]*/)?.[0] || "";
  const suffix = num.match(/[^0-9.]*$/)?.[0] || "";
  const isNumeric = !isNaN(numericValue);

  const countProgress = interpolate(frame, [0, fps * 1.2], [0, 1], {
    extrapolateRight: "clamp",
  });
  const displayNum = isNumeric ? Math.floor(numericValue * countProgress) : num;
  const glowPulse = Math.sin((frame / fps) * 3) * 0.3 + 0.7;

  return (
    <>
      <div
        style={{
          fontFamily: SHORTS_FONTS.display,
          fontSize: 130 * scale,
          fontWeight: 900,
          color,
          textShadow: `0 0 ${40 * glowPulse}px ${color}50, 0 0 ${80 * glowPulse}px ${color}25`,
          letterSpacing: "-0.03em",
          lineHeight: 1,
        }}
      >
        {isNumeric ? `${prefix}${displayNum.toLocaleString()}${suffix}` : num}
      </div>
      {label && (
        <div
          style={{
            fontFamily: SHORTS_FONTS.primary,
            fontSize: 26 * scale,
            color: theme.textMuted,
            marginTop: 20 * scale,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
          }}
        >
          {label}
        </div>
      )}
    </>
  );
};

const ComparisonVisual: React.FC<{
  left: string;
  right: string;
  label?: string;
} & VisualProps> = ({ left, right, label, color, frame, fps, scale, theme }) => {
  const leftEntry = spring({ fps, frame, config: { damping: 14 } });
  const rightEntry = spring({ fps, frame: Math.max(0, frame - 10), config: { damping: 14 } });

  return (
    <>
      {label && (
        <div
          style={{
            fontFamily: SHORTS_FONTS.primary,
            fontSize: 22 * scale,
            color: theme.textMuted,
            marginBottom: 30 * scale,
            letterSpacing: "0.12em",
            textTransform: "uppercase",
          }}
        >
          {label}
        </div>
      )}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 24 * scale }}>
        <div
          style={{
            fontFamily: SHORTS_FONTS.heading,
            fontSize: 44 * scale,
            fontWeight: 600,
            color: theme.textMuted,
            opacity: leftEntry,
            transform: `translateX(${(1 - leftEntry) * -40}px)`,
            textDecoration: "line-through",
            textDecorationColor: `${theme.secondary}90`,
            textDecorationThickness: 3 * scale,
          }}
        >
          {left}
        </div>
        <div style={{ fontSize: 32 * scale, color: theme.textMuted, opacity: Math.min(leftEntry, rightEntry) }}>
          ↓
        </div>
        <div
          style={{
            fontFamily: SHORTS_FONTS.display,
            fontSize: 52 * scale,
            fontWeight: 800,
            color,
            opacity: rightEntry,
            transform: `translateX(${(1 - rightEntry) * 40}px) scale(${0.9 + rightEntry * 0.1})`,
            textShadow: `0 0 25px ${color}35`,
          }}
        >
          {right}
        </div>
      </div>
    </>
  );
};

const TextHighlightVisual: React.FC<{
  text: string;
  subtext?: string;
  emphasis?: string;
} & VisualProps> = ({ text, subtext, emphasis, color, frame, fps, scale, theme }) => {
  const glowPulse = Math.sin((frame / fps) * 2) * 0.15 + 0.85;
  const isShake = emphasis === "shake";
  const shakeX = isShake ? Math.sin(frame * 0.8) * 2 : 0;

  const highlightStyle: React.CSSProperties =
    emphasis === "underline"
      ? { borderBottom: `4px solid ${color}`, paddingBottom: 8 * scale }
      : emphasis === "highlight"
      ? { background: `${color}20`, padding: `${8 * scale}px ${20 * scale}px`, borderRadius: 8 * scale }
      : {};

  return (
    <>
      <div
        style={{
          fontFamily: SHORTS_FONTS.heading,
          fontSize: 52 * scale,
          fontWeight: 800,
          color: theme.text,
          textAlign: "center",
          lineHeight: 1.35,
          maxWidth: 900 * scale,
          textShadow: emphasis === "glow" ? `0 0 ${30 * glowPulse}px ${color}50` : `0 0 ${15 * glowPulse}px ${color}20`,
          transform: `translateX(${shakeX}px)`,
          ...highlightStyle,
        }}
      >
        {text}
      </div>
      {subtext && (
        <div
          style={{
            fontFamily: SHORTS_FONTS.primary,
            fontSize: 26 * scale,
            color: theme.textMuted,
            marginTop: 24 * scale,
            textAlign: "center",
            maxWidth: 800 * scale,
            lineHeight: 1.6,
          }}
        >
          {subtext}
        </div>
      )}
    </>
  );
};

const SimpleFlowVisual: React.FC<{ steps: string[] } & VisualProps> = ({
  steps,
  color,
  frame,
  fps,
  scale,
  theme,
}) => (
  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 18 * scale }}>
    {steps.map((step, i) => {
      const delay = i * 10;
      const progress = spring({ fps, frame: Math.max(0, frame - delay), config: { damping: 14 } });
      const isLast = i === steps.length - 1;
      return (
        <React.Fragment key={i}>
          <div
            style={{
              fontFamily: SHORTS_FONTS.primary,
              fontSize: 30 * scale,
              fontWeight: isLast ? 700 : 500,
              color: isLast ? color : theme.text,
              padding: `${14 * scale}px ${28 * scale}px`,
              background: isLast ? `${color}12` : `${theme.text}08`,
              border: `1px solid ${isLast ? `${color}40` : `${theme.text}10`}`,
              borderRadius: 10 * scale,
              opacity: progress,
              transform: `translateY(${(1 - progress) * 25}px)`,
              textShadow: isLast ? `0 0 15px ${color}30` : "none",
            }}
          >
            {step}
          </div>
          {i < steps.length - 1 && (
            <div style={{ fontSize: 20 * scale, color: theme.textMuted, opacity: progress * 0.5 }}>↓</div>
          )}
        </React.Fragment>
      );
    })}
  </div>
);

const IconStatVisual: React.FC<{ icon: string; stat: string; label?: string } & VisualProps> = ({
  icon,
  stat,
  label,
  color,
  frame,
  fps,
  scale,
  theme,
}) => {
  const bounce = spring({ fps, frame, config: { damping: 8 } });
  return (
    <>
      <div style={{ fontSize: 80 * scale, transform: `scale(${bounce})`, marginBottom: 20 * scale }}>
        {icon}
      </div>
      <div
        style={{
          fontFamily: SHORTS_FONTS.display,
          fontSize: 68 * scale,
          fontWeight: 900,
          color,
          textShadow: `0 0 30px ${color}35`,
        }}
      >
        {stat}
      </div>
      {label && (
        <div
          style={{
            fontFamily: SHORTS_FONTS.primary,
            fontSize: 24 * scale,
            color: theme.textMuted,
            marginTop: 14 * scale,
            textTransform: "uppercase",
            letterSpacing: "0.1em",
          }}
        >
          {label}
        </div>
      )}
    </>
  );
};

const KeyPointVisual: React.FC<{ point: string; subpoint?: string } & VisualProps> = ({
  point,
  subpoint,
  color,
  frame,
  fps,
  scale,
  theme,
}) => {
  const progress = spring({ fps, frame, config: { damping: 14 } });
  return (
    <div
      style={{
        background: `${theme.text}06`,
        borderLeft: `4px solid ${color}`,
        borderRadius: `0 ${14 * scale}px ${14 * scale}px 0`,
        padding: `${30 * scale}px ${36 * scale}px`,
        maxWidth: 900 * scale,
        opacity: progress,
        transform: `translateX(${(1 - progress) * -50}px)`,
      }}
    >
      <div
        style={{
          fontFamily: SHORTS_FONTS.heading,
          fontSize: 34 * scale,
          fontWeight: 700,
          color: theme.text,
          lineHeight: 1.4,
        }}
      >
        {point}
      </div>
      {subpoint && (
        <div
          style={{
            fontFamily: SHORTS_FONTS.primary,
            fontSize: 24 * scale,
            color: theme.textMuted,
            lineHeight: 1.5,
            marginTop: 12 * scale,
          }}
        >
          {subpoint}
        </div>
      )}
    </div>
  );
};

const QuestionVisual: React.FC<{ question: string } & VisualProps> = ({
  question,
  color,
  frame,
  fps,
  scale,
  theme,
}) => {
  const pulse = Math.sin((frame / fps) * 2.5) * 0.1 + 1.0;
  return (
    <>
      <div
        style={{
          fontSize: 72 * scale,
          transform: `scale(${pulse})`,
          marginBottom: 30 * scale,
          filter: `drop-shadow(0 0 20px ${color}40)`,
        }}
      >
        🤔
      </div>
      <div
        style={{
          fontFamily: SHORTS_FONTS.heading,
          fontSize: 42 * scale,
          fontWeight: 700,
          color: theme.text,
          textAlign: "center",
          maxWidth: 850 * scale,
          lineHeight: 1.45,
        }}
      >
        {question}
      </div>
    </>
  );
};

const StatRowVisual: React.FC<{
  items: Array<{ label: string; value: string }>;
} & VisualProps> = ({ items, color, frame, fps, scale, theme }) => (
  <div style={{ display: "flex", flexDirection: "column", gap: 20 * scale, width: "100%", maxWidth: 900 * scale }}>
    {items.map((item, i) => {
      const delay = i * 7;
      const progress = spring({ fps, frame: Math.max(0, frame - delay), config: { damping: 14 } });
      return (
        <div
          key={i}
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: `${14 * scale}px ${22 * scale}px`,
            background: `${theme.text}05`,
            borderRadius: 10 * scale,
            borderLeft: `3px solid ${i === 0 ? color : `${theme.text}15`}`,
            opacity: progress,
            transform: `translateX(${(1 - progress) * 35}px)`,
          }}
        >
          <span style={{ fontFamily: SHORTS_FONTS.primary, fontSize: 24 * scale, color: theme.textMuted }}>
            {item.label}
          </span>
          <span
            style={{
              fontFamily: SHORTS_FONTS.display,
              fontSize: 30 * scale,
              fontWeight: 700,
              color: i === 0 ? color : theme.text,
            }}
          >
            {item.value}
          </span>
        </div>
      );
    })}
  </div>
);

const ListVisual: React.FC<{ title: string; items: string[] } & VisualProps> = ({
  title,
  items,
  color,
  frame,
  fps,
  scale,
  theme,
}) => (
  <div style={{ maxWidth: 900 * scale, width: "100%" }}>
    <div
      style={{
        fontFamily: SHORTS_FONTS.heading,
        fontSize: 38 * scale,
        fontWeight: 800,
        color: theme.text,
        marginBottom: 28 * scale,
        textAlign: "center",
      }}
    >
      {title}
    </div>
    {items.map((item, i) => {
      const delay = i * 7 + 12;
      const progress = spring({ fps, frame: Math.max(0, frame - delay), config: { damping: 14 } });
      return (
        <div
          key={i}
          style={{
            display: "flex",
            alignItems: "flex-start",
            gap: 14 * scale,
            padding: `${10 * scale}px 0`,
            opacity: progress,
            transform: `translateX(${(1 - progress) * 40}px)`,
          }}
        >
          <div
            style={{
              width: 6 * scale,
              height: 6 * scale,
              borderRadius: "50%",
              background: color,
              flexShrink: 0,
              marginTop: 10 * scale,
              boxShadow: `0 0 8px ${color}50`,
            }}
          />
          <span style={{ fontFamily: SHORTS_FONTS.primary, fontSize: 26 * scale, color: theme.text, lineHeight: 1.5 }}>
            {item}
          </span>
        </div>
      );
    })}
  </div>
);

const CountdownVisual: React.FC<{ number: string; label?: string } & VisualProps> = ({
  number: num,
  label,
  color,
  frame,
  fps,
  scale,
  theme,
}) => {
  const bounce = spring({ fps, frame, config: { damping: 8, stiffness: 120 } });
  const glowPulse = Math.sin((frame / fps) * 4) * 0.35 + 0.65;
  return (
    <>
      <div
        style={{
          fontFamily: SHORTS_FONTS.display,
          fontSize: 170 * scale,
          fontWeight: 900,
          color,
          transform: `scale(${bounce})`,
          textShadow: `0 0 ${60 * glowPulse}px ${color}45, 0 0 ${120 * glowPulse}px ${color}18`,
          lineHeight: 1,
        }}
      >
        {num}
      </div>
      {label && (
        <div
          style={{
            fontFamily: SHORTS_FONTS.primary,
            fontSize: 28 * scale,
            color: theme.textMuted,
            marginTop: 24 * scale,
            textTransform: "uppercase",
            letterSpacing: "0.12em",
          }}
        >
          {label}
        </div>
      )}
    </>
  );
};

// ── NEW VISUAL TYPES ──────────────────────────────────────

const QuoteVisual: React.FC<{ quote: string; author?: string } & VisualProps> = ({
  quote,
  author,
  color,
  frame,
  fps,
  scale,
  theme,
}) => {
  const progress = spring({ fps, frame, config: { damping: 16 } });
  const quoteMarkOpacity = interpolate(frame, [0, fps * 0.5], [0, 0.15], { extrapolateRight: "clamp" });

  return (
    <div style={{ position: "relative", maxWidth: 900 * scale, padding: `${20 * scale}px` }}>
      {/* Giant quote mark background */}
      <div
        style={{
          position: "absolute",
          top: -40 * scale,
          left: -10 * scale,
          fontFamily: SHORTS_FONTS.serif,
          fontSize: 220 * scale,
          color,
          opacity: quoteMarkOpacity,
          lineHeight: 1,
          userSelect: "none",
        }}
      >
        "
      </div>
      <div
        style={{
          fontFamily: SHORTS_FONTS.serif,
          fontSize: 38 * scale,
          fontWeight: 500,
          color: theme.text,
          lineHeight: 1.6,
          textAlign: "center",
          opacity: progress,
          transform: `translateY(${(1 - progress) * 20}px)`,
          fontStyle: "italic",
        }}
      >
        "{quote}"
      </div>
      {author && (
        <div
          style={{
            fontFamily: SHORTS_FONTS.primary,
            fontSize: 22 * scale,
            color: theme.textMuted,
            marginTop: 24 * scale,
            textAlign: "center",
            opacity: interpolate(frame, [fps * 0.3, fps * 0.6], [0, 1], { extrapolateRight: "clamp" }),
            letterSpacing: "0.05em",
          }}
        >
          — {author}
        </div>
      )}
    </div>
  );
};

const MorphingTextVisual: React.FC<{
  textA: string;
  textB: string;
  label?: string;
} & VisualProps> = ({ textA, textB, label, color, frame, fps, scale, theme }) => {
  const morphTime = fps * 1.5; // morph happens at 1.5s
  const isMorphed = frame > morphTime;
  const morphProgress = interpolate(frame, [morphTime - 5, morphTime + 5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const textAOpacity = 1 - morphProgress;
  const textBOpacity = morphProgress;
  const textAScale = interpolate(morphProgress, [0, 1], [1, 0.85]);
  const textBScale = interpolate(morphProgress, [0, 1], [0.85, 1]);

  return (
    <>
      {label && (
        <div
          style={{
            fontFamily: SHORTS_FONTS.primary,
            fontSize: 22 * scale,
            color: theme.textMuted,
            marginBottom: 30 * scale,
            letterSpacing: "0.12em",
            textTransform: "uppercase",
          }}
        >
          {label}
        </div>
      )}
      <div style={{ position: "relative", height: 80 * scale }}>
        <div
          style={{
            position: "absolute",
            width: "100%",
            textAlign: "center",
            fontFamily: SHORTS_FONTS.display,
            fontSize: 50 * scale,
            fontWeight: 800,
            color: theme.textMuted,
            opacity: textAOpacity,
            transform: `scale(${textAScale})`,
            textDecoration: isMorphed ? "line-through" : "none",
            textDecorationColor: `${theme.secondary}80`,
          }}
        >
          {textA}
        </div>
        <div
          style={{
            position: "absolute",
            width: "100%",
            textAlign: "center",
            fontFamily: SHORTS_FONTS.display,
            fontSize: 56 * scale,
            fontWeight: 900,
            color,
            opacity: textBOpacity,
            transform: `scale(${textBScale})`,
            textShadow: `0 0 30px ${color}40`,
          }}
        >
          {textB}
        </div>
      </div>
    </>
  );
};

const EquationVisual: React.FC<{ equation: string; label?: string } & VisualProps> = ({
  equation,
  label,
  color,
  frame,
  fps,
  scale,
  theme,
}) => {
  const progress = spring({ fps, frame, config: { damping: 14 } });
  const glowPulse = Math.sin((frame / fps) * 2) * 0.2 + 0.8;

  return (
    <>
      <div
        style={{
          fontFamily: SHORTS_FONTS.mono,
          fontSize: 36 * scale,
          fontWeight: 700,
          color,
          textAlign: "center",
          padding: `${24 * scale}px ${32 * scale}px`,
          background: `${color}08`,
          border: `1px solid ${color}25`,
          borderRadius: 12 * scale,
          opacity: progress,
          transform: `scale(${0.9 + progress * 0.1})`,
          textShadow: `0 0 ${20 * glowPulse}px ${color}30`,
          letterSpacing: "0.02em",
          lineHeight: 1.6,
        }}
      >
        {equation}
      </div>
      {label && (
        <div
          style={{
            fontFamily: SHORTS_FONTS.primary,
            fontSize: 24 * scale,
            color: theme.textMuted,
            marginTop: 20 * scale,
            textAlign: "center",
          }}
        >
          {label}
        </div>
      )}
    </>
  );
};

const GradientTextVisual: React.FC<{ text: string; subtext?: string } & VisualProps> = ({
  text,
  subtext,
  color,
  frame,
  fps,
  scale,
  theme,
}) => {
  const gradientAngle = 90 + Math.sin((frame / fps) * 0.8) * 30;

  return (
    <>
      <div
        style={{
          fontFamily: SHORTS_FONTS.display,
          fontSize: 56 * scale,
          fontWeight: 900,
          background: `linear-gradient(${gradientAngle}deg, ${color}, ${theme.accent}, ${theme.secondary})`,
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          backgroundClip: "text",
          textAlign: "center",
          lineHeight: 1.3,
          maxWidth: 900 * scale,
          filter: `drop-shadow(0 0 20px ${color}25)`,
        }}
      >
        {text}
      </div>
      {subtext && (
        <div
          style={{
            fontFamily: SHORTS_FONTS.primary,
            fontSize: 26 * scale,
            color: theme.textMuted,
            marginTop: 24 * scale,
            textAlign: "center",
            maxWidth: 800 * scale,
            lineHeight: 1.6,
          }}
        >
          {subtext}
        </div>
      )}
    </>
  );
};

// ── Video Clip Visual ──────────────────────────────────────
// Full-screen background video with text overlay + gradient scrim
const VideoClipVisual: React.FC<{
  beat: ShortsBeat;
  frame: number;
  fps: number;
  scale: number;
  theme: ShortsThemeColors;
  entryScale: number;
  entryOpacity: number;
}> = ({ beat, frame, fps, scale, theme, entryScale, entryOpacity }) => {
  const { visual } = beat;
  const videoSrc = visual.video_src ? staticFile(visual.video_src) : null;
  const videoOpacity = visual.video_opacity ?? 0.4;
  const primaryText = visual.primary_text;
  const secondaryText = visual.secondary_text;
  const color = getColor(theme, visual.color);
  const fontFamily = getFont(visual.font);
  const glowPulse = Math.sin((frame / fps) * 2) * 0.15 + 0.85;

  const textEntry = spring({ fps, frame: Math.max(0, frame - 8), config: { damping: 14, stiffness: 100 } });

  return (
    <div style={{
      position: "absolute",
      top: 0, left: 0,
      width: 1080 * scale,
      height: 1920 * scale,
      overflow: "hidden",
    }}>
      {/* Background video */}
      {videoSrc && (
        <OffthreadVideo
          src={videoSrc}
          style={{
            position: "absolute",
            top: 0, left: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover",
            opacity: videoOpacity,
          }}
          startFrom={Math.floor((visual.video_start ?? 0) * fps)}
          muted
        />
      )}

      {/* Gradient scrim - top */}
      <div style={{
        position: "absolute",
        top: 0, left: 0, right: 0,
        height: "35%",
        background: `linear-gradient(to bottom, ${theme.background}ee, transparent)`,
      }} />

      {/* Gradient scrim - bottom */}
      <div style={{
        position: "absolute",
        bottom: 0, left: 0, right: 0,
        height: "45%",
        background: `linear-gradient(to top, ${theme.background}f0, ${theme.background}80, transparent)`,
      }} />

      {/* Vignette */}
      <div style={{
        position: "absolute",
        top: 0, left: 0, right: 0, bottom: 0,
        boxShadow: `inset 0 0 ${200 * scale}px ${80 * scale}px ${theme.background}90`,
      }} />

      {/* Text overlay - centered in bottom third */}
      <div style={{
        position: "absolute",
        bottom: "25%",
        left: 0, right: 0,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: `0 ${60 * scale}px`,
        opacity: entryOpacity * textEntry,
        transform: `scale(${entryScale}) translateY(${(1 - textEntry) * 30}px)`,
      }}>
        <div style={{
          fontFamily: fontFamily || SHORTS_FONTS.display,
          fontSize: 52 * scale,
          fontWeight: 900,
          color: theme.text,
          textAlign: "center",
          lineHeight: 1.35,
          textShadow: `0 0 ${30 * glowPulse}px ${color}60, 0 2px 20px ${theme.background}cc`,
          maxWidth: 900 * scale,
        }}>
          {primaryText}
        </div>
        {secondaryText && (
          <div style={{
            fontFamily: SHORTS_FONTS.primary,
            fontSize: 28 * scale,
            color: theme.textMuted,
            marginTop: 20 * scale,
            textAlign: "center",
            maxWidth: 800 * scale,
            lineHeight: 1.5,
            textShadow: `0 2px 15px ${theme.background}cc`,
          }}>
            {secondaryText}
          </div>
        )}
      </div>

      {/* Accent line */}
      <div style={{
        position: "absolute",
        bottom: `calc(25% - ${40 * scale}px)`,
        left: "50%",
        transform: `translateX(-50%) scaleX(${textEntry})`,
        width: 80 * scale,
        height: 3 * scale,
        background: `linear-gradient(90deg, transparent, ${color}, transparent)`,
        borderRadius: 2,
      }} />
    </div>
  );
};
