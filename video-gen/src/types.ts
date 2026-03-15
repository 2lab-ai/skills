import type { EntranceType, ExitType } from "./utils/animations";
import type { ThemeName } from "./utils/colors";

export type SubtitleVariant = "box" | "stroke" | "minimal";

export type SceneType =
  | "hero" | "list" | "grid" | "code" | "flow" | "chat" | "stat"
  | "quote" | "timeline" | "comparison" | "emoji" | "image" | "bigtext";

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
