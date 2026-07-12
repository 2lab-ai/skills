import type { EntranceType, ExitType } from "./utils/animations";
import type { ThemeName } from "./utils/colors";

export type SubtitleVariant = "box" | "stroke" | "minimal";

export type SceneType =
  | "hero" | "list" | "grid" | "code" | "flow" | "chat" | "stat"
  | "quote" | "timeline" | "comparison" | "emoji" | "image" | "bigtext"
  | "terminal" | "tokenPredict" | "matrixRain" | "progressBar"
  | "radar" | "countdown" | "map" | "callout" | "splitScreen"
  | "typewriter" | "pyramid" | "reveal" | "infographic"
  | "trainingData" | "systemPrompt" | "conversation" | "flowchart";

export interface SubtitleCue {
  text: string;
  startMs: number;
  endMs: number;
}

export interface SceneConfig {
  id: string;
  type: SceneType;
  narration: string;
  durationInSeconds?: number;
  data: Record<string, unknown>;
  style?: {
    background?: string;
    accentColor?: string;
    textColor?: string;
  };
  entrance?: EntranceType;       // scene entrance animation
  exit?: ExitType;               // scene exit animation
  theme?: ThemeName;             // per-scene theme override
}

export interface VideoConfig {
  title: string;
  fps: number;
  width: number;
  height: number;
  theme?: ThemeName;               // global theme
  subtitleVariant?: SubtitleVariant; // global subtitle style
  defaultStyle: {
    background: string;
    accentColor: string;
    textColor: string;
    fontFamily: string;
  };
  scenes: SceneConfig[];
}

// ============================================================
// SCENE DATA TYPES
// ============================================================

export interface HeroData {
  title: string;
  subtitle?: string;
  badge?: string;
  emoji?: string;       // big emoji above title
  gifUrl?: string;      // animated GIF behind or beside title
  layout?: "center" | "left" | "split";  // different hero layouts
}

export interface ListData {
  title: string;
  items: string[];
  ordered?: boolean;
  icon?: string;        // custom emoji icon for bullets
  variant?: "default" | "cards" | "timeline" | "checklist";
}

export interface GridData {
  title: string;
  cards: Array<{
    icon?: string;
    title: string;
    description: string;
    gifUrl?: string;    // animated GIF in card
  }>;
  variant?: "default" | "bento" | "masonry";
}

export interface CodeData {
  title?: string;
  language: string;
  code: string;
  highlights?: number[];
  variant?: "default" | "terminal" | "notebook";
}

export interface FlowData {
  title: string;
  steps: Array<{
    label: string;
    description?: string;
    emoji?: string;
  }>;
  direction?: "horizontal" | "vertical";
  variant?: "default" | "zigzag" | "circular";
}

export interface ChatData {
  title?: string;
  messages: Array<{
    role: "user" | "assistant" | "system";
    content: string;
    name?: string;
  }>;
}

export interface StatData {
  title: string;
  stats: Array<{
    label: string;
    value: string | number;
    unit?: string;
    change?: string;
    emoji?: string;
  }>;
  variant?: "default" | "donut" | "bar";
}

// NEW SCENE TYPES

export interface QuoteData {
  quote: string;
  author: string;
  source?: string;
  emoji?: string;
  variant?: "default" | "large" | "typewriter" | "highlight";
}

export interface TimelineData {
  title: string;
  events: Array<{
    date: string;
    title: string;
    description?: string;
    emoji?: string;
  }>;
  variant?: "default" | "horizontal" | "alternating";
}

export interface ComparisonData {
  title: string;
  left: {
    title: string;
    items: string[];
    emoji?: string;
    color?: string;
  };
  right: {
    title: string;
    items: string[];
    emoji?: string;
    color?: string;
  };
  variant?: "default" | "versus" | "before-after";
}

export interface EmojiData {
  emoji: string;
  title?: string;
  subtitle?: string;
  size?: number;       // emoji size in px (default 200)
  animate?: "bounce" | "spin" | "pulse" | "float" | "none";
}

export interface ImageData {
  src: string;          // local path in public/ or URL
  gifUrl?: string;      // animated GIF URL
  title?: string;
  caption?: string;
  layout?: "fullscreen" | "centered" | "split-left" | "split-right";
}

export interface BigTextData {
  text: string;
  subtitle?: string;
  emoji?: string;
  variant?: "impact" | "gradient" | "outline" | "glitch";
}

// CUSTOM SCENE TYPES

export interface TerminalData {
  lines: Array<{
    prompt?: string;
    text: string;
    color?: string;
    delay?: number;
  }>;
  cursor?: "block" | "underline" | "bar";
  speed?: number;
}

export interface TokenPredictData {
  sentence: string;
  predictions: Array<{
    token: string;
    probability: number;
  }>;
  highlightIndex?: number;
  animate?: "highlight-walk" | "reveal" | "none";
}

export interface MatrixRainData {
  color?: string;
  columns?: number;
  speed?: number;
  charset?: string;
  density?: number;
  overlayText?: string;
}

export interface ProgressBarData {
  title: string;
  percent: number;
  bigText?: string;
  label?: string;
  animate?: boolean;
}

// ============================================================
// NEW SCENE DATA TYPES (Wave 2)
// ============================================================

export interface RadarData {
  title: string;
  axes: Array<{ label: string; value: number }>; // value 0-100
  label?: string;                      // legend label for main data
  compareAxes?: Array<{ label: string; value: number }>; // optional second dataset
  compareLabel?: string;               // legend label for compare data
  rings?: number;                      // grid ring count (default 5)
}

export interface CountdownData {
  from?: number;                       // start number (default 5)
  to?: number;                         // end number (default 0)
  speed?: number;                      // seconds per count (default 1)
  title?: string;                      // top label
  subtitle?: string;                   // bottom text
  revealText?: string;                 // text shown at end instead of final number
  revealSubtitle?: string;             // subtitle shown at end
}

export interface MapData {
  title: string;
  points: Array<{
    lat: number;
    lon: number;
    label?: string;
    color?: string;
    size?: number;                     // multiplier (default 1)
  }>;
  connections?: Array<[number, number]>; // index pairs to connect with arcs
  legend?: Array<{ label: string; color?: string }>;
}

export interface CalloutData {
  variant?: "info" | "tip" | "warning" | "danger" | "success" | "quote";
  title?: string;
  content: string;
  emoji?: string;
  label?: string;                      // type badge text override
  color?: string;                      // accent color override
  footer?: string;                     // small italic footer note
}

export interface SplitScreenData {
  title?: string;
  direction?: "horizontal" | "vertical"; // default horizontal
  panels: Array<{
    title: string;
    emoji?: string;
    items?: string[];
    description?: string;
    background?: string;
    accentColor?: string;
  }>;
}

export interface TypewriterData {
  text: string;
  speed?: number;                      // chars per frame (default 2)
  fontSize?: number;                   // default 48
  variant?: "default" | "mono" | "handwriting" | "bold";
  align?: "left" | "center" | "right"; // default center
  label?: string;                      // small label above text
  attribution?: string;                // shown after typing completes
}

export interface PyramidData {
  title: string;
  levels: Array<{
    label: string;
    description?: string;
    emoji?: string;
    color?: string;
  }>;                                  // index 0 = top, last = bottom
  variant?: "default" | "inverted";
}

export interface RevealData {
  value: string;                       // the big reveal value
  preLabel?: string;                   // suspense label (e.g. "The answer is...")
  subtitle?: string;                   // shown after reveal
  emoji?: string;
  unit?: string;                       // unit after value
  delay?: number;                      // seconds before reveal (default 2)
  valueFontSize?: number;              // override font size (default 120)
}

// ============================================================
// INFOGRAPHIC BUILDING BLOCKS
// ============================================================

interface InfographicBase {
  id: string;
  x: number;    // 0–100 % of canvas width
  y: number;    // 0–100 % of canvas height
  delay?: number;
  animation?: "fadeIn" | "slideUp" | "slideDown" | "slideLeft" | "slideRight" | "scaleIn" | "pop";
}

export interface InfographicRect extends InfographicBase { type: "rect"; width: number; height: number; fill: string; stroke?: string; strokeWidth?: number; radius?: number; label?: string; labelColor?: string; labelSize?: number; }
export interface InfographicFace extends InfographicBase { type: "face"; size: number; expression: "happy" | "sad" | "neutral" | "worried" | "angry" | "surprised"; color: string; }
export interface InfographicBattery extends InfographicBase { type: "battery"; width: number; height: number; level: number; color: string; }
export interface InfographicBarStack extends InfographicBase { type: "barStack"; bars: Array<{ width: number; color: string; label?: string }>; maxWidth: number; barHeight: number; gap: number; align?: "bottom" | "top"; barAlign?: "left" | "center" | "right"; }
export interface InfographicArrow extends InfographicBase { type: "arrow"; toX: number; toY: number; color?: string; strokeWidth?: number; dashed?: boolean; }
export interface InfographicBubble extends InfographicBase { type: "bubble"; width: number; height: number; text: string; textColor?: string; fill?: string; stroke?: string; pointerDirection?: "down" | "up" | "left" | "right"; fontSize?: number; }
export interface InfographicText extends InfographicBase { type: "text"; text: string; fontSize?: number; fontWeight?: number; color?: string; align?: "left" | "center" | "right"; }
export interface InfographicLine extends InfographicBase { type: "line"; toX: number; toY: number; color?: string; strokeWidth?: number; dashed?: boolean; }
export interface InfographicConnector extends InfographicBase { type: "connector"; toX: number; toY: number; color?: string; strokeWidth?: number; bendDirection?: "horizontal-first" | "vertical-first"; dot?: boolean; }

export type InfographicElement =
  | InfographicRect | InfographicFace | InfographicBattery | InfographicBarStack
  | InfographicArrow | InfographicBubble | InfographicText | InfographicLine | InfographicConnector;

export interface InfographicData {
  title?: string;
  subtitle?: string;
  background?: string;
  elements: InfographicElement[];
}

// ============================================================
// BIGBRAIN-STYLE SCENE TYPES (@realbigbrainai inspired)
// ============================================================

/** Chaotic scrolling multi-color training data text (code, memes, equations) */
export interface TrainingDataData {
  /** Lines of "training data" text to scroll through */
  lines: Array<{
    text: string;
    color?: string;       // override per-line color
    indent?: number;      // spaces of indent (0-8)
  }>;
  /** Scroll speed multiplier (default 1) */
  speed?: number;
  /** Whether to add garble/corruption effect at end (default false) */
  garbleAtEnd?: boolean;
  /** Background color override (default #000000) */
  background?: string;
}

/** System prompt reveal with >> prefix lines (dark reddish-brown bg) */
export interface SystemPromptData {
  /** Lines of system prompt to reveal one by one */
  lines: string[];
  /** Prefix character (default ">>") */
  prefix?: string;
  /** Text color override (default warm orange) */
  textColor?: string;
  /** Background color (default dark reddish-brown #1a0c0c) */
  background?: string;
  /** Whether to flip/invert last line (default false) */
  flipLastLine?: boolean;
}

/** AI conversation scene with typing cursor, context %, multi-turn */
export interface ConversationData {
  /** Chat turns with typing animation */
  messages: Array<{
    role: "user" | "claude" | "narrator";
    text: string;
    /** Whether to show typing animation (default true for claude) */
    typing?: boolean;
    /** Truncate/cut-off the response at this char index */
    cutoffAt?: number;
  }>;
  /** Show context window percentage (e.g. "2%") in top right */
  contextPercent?: number;
  /** Background color (default dark navy #0d1117) */
  background?: string;
  /** Whether to show blinking cursor (default true) */
  showCursor?: boolean;
  /** Variant: "chat" = labeled chat, "narration" = centered phrases, "mixed" = both */
  variant?: "chat" | "narration" | "mixed";
  /** For narration variant: phrases shown one at a time, centered */
  phrases?: Array<{
    text: string;
    color?: string;
    fontSize?: number;
    /** Duration in seconds for this phrase (default 2) */
    duration?: number;
  }>;
}

// ============================================================
// FLOWCHART SCENE ("How to Adult" decision-chart walkthrough)
// ============================================================

export interface FlowchartBox {
  id: string;
  x: number; y: number; w: number; h: number;
  text: string;
  style?: "question" | "action" | "plain";
  font_size?: number;
}

export interface FlowchartDiamond {
  id?: string;
  x: number; y: number;
  label: "Y" | "N";
  r?: number;
}

export interface FlowchartEdge {
  id?: string;
  points: Array<[number, number]>;
  color?: "black" | "orange";
  arrow?: boolean;
}

/** One step of the traced decision path */
export interface FlowchartPathStep {
  /** box id to pulse/activate */
  box?: string;
  /** chosen branch at this box: "Y" or "N" */
  choice?: "Y" | "N";
  /** diamond ids to light up orange when reaching this step */
  diamonds?: string[];
  /** edge ids (or indices) to light up orange when reaching this step */
  edges?: Array<string | number>;
  /** final result box id (terminal emphasis) */
  result?: string;
}

export interface FlowchartData {
  title?: string;
  /** SVG canvas dims (default 860x1220) */
  width?: number;
  height?: number;
  rules?: boolean;
  boxes: FlowchartBox[];
  diamonds: FlowchartDiamond[];
  edges: FlowchartEdge[];
  /** ordered decision path to trace */
  path: FlowchartPathStep[];
}

// TTS output metadata
export interface TTSMetadata {
  sceneId: string;
  audioFile: string;
  durationMs: number;
  subtitles: SubtitleCue[];
}

// Full render context
export interface RenderContext {
  config: VideoConfig;
  ttsData: TTSMetadata[];
  totalDurationInFrames: number;
}
