export type SceneType = "hero" | "list" | "grid" | "code" | "flow" | "chat" | "stat";

export interface SubtitleCue {
  text: string;
  startMs: number;
  endMs: number;
}

export interface SceneConfig {
  id: string;
  type: SceneType;
  narration: string;
  durationInSeconds?: number; // auto-calculated from TTS if omitted
  data: Record<string, unknown>;
  style?: {
    background?: string;
    accentColor?: string;
    textColor?: string;
  };
}

export interface VideoConfig {
  title: string;
  fps: number;
  width: number;
  height: number;
  defaultStyle: {
    background: string;
    accentColor: string;
    textColor: string;
    fontFamily: string;
  };
  scenes: SceneConfig[];
}

// Scene-specific data types
export interface HeroData {
  title: string;
  subtitle?: string;
  badge?: string;
}

export interface ListData {
  title: string;
  items: string[];
  ordered?: boolean;
}

export interface GridData {
  title: string;
  cards: Array<{
    icon?: string;
    title: string;
    description: string;
  }>;
}

export interface CodeData {
  title?: string;
  language: string;
  code: string;
  highlights?: number[]; // line numbers to highlight
}

export interface FlowData {
  title: string;
  steps: Array<{
    label: string;
    description?: string;
  }>;
  direction?: "horizontal" | "vertical";
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
    change?: string; // e.g. "+12%"
  }>;
}

// TTS output metadata
export interface TTSMetadata {
  sceneId: string;
  audioFile: string;
  durationMs: number;
  subtitles: SubtitleCue[];
}

// Full render context (after TTS generation)
export interface RenderContext {
  config: VideoConfig;
  ttsData: TTSMetadata[];
  totalDurationInFrames: number;
}
