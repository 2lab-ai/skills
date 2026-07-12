import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
import { Background } from "../components/Background";
import { getTheme } from "../utils/colors";
import type { ConversationData } from "../types";

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface Props {
  data: ConversationData;
  accentColor?: string;
  themeName?: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const CHAT_BG = "#0d1117";
const NARRATION_BG = "#000000";

const COLORS = {
  userLabel: "#5b8dd9",
  claudeLabel: "#e8a050",
  narrationText: "#808080",
  contextRed: "#ff4444",
  cursorBlock: "#e0e0e0",
  green: "#00ff41",
  red: "#ff4444",
  blue: "#5b8dd9",
  navy: "#0d1117",
};

const MONO_FONT = "'JetBrains Mono', 'Fira Code', monospace";

// ---------------------------------------------------------------------------
// Chat sub-component
// ---------------------------------------------------------------------------

interface ChatViewProps {
  data: ConversationData;
  frame: number;
  fps: number;
  /** Offset in frames before the chat portion begins (for mixed mode). */
  frameOffset?: number;
}

const ChatView: React.FC<ChatViewProps> = ({
  data,
  frame,
  fps,
  frameOffset = 0,
}) => {
  const showCursor = data.showCursor !== false;
  const charsPerFrame = 3;

  // Time budget per message: proportional to text length, minimum ~1.5s
  // plus a small gap between messages.
  const messageTiming = data.messages.map((msg) => {
    const textLen = msg.cutoffAt != null ? Math.min(msg.text.length, msg.cutoffAt) : msg.text.length;
    const typingFrames = Math.ceil(textLen / charsPerFrame);
    // Pause after typing before next message begins (~0.5s)
    const pauseFrames = Math.round(fps * 0.5);
    return { textLen, typingFrames, pauseFrames };
  });

  // Cumulative start frames
  let cumulative = frameOffset;
  const messageStarts = messageTiming.map((t) => {
    const start = cumulative;
    cumulative += t.typingFrames + t.pauseFrames;
    return start;
  });

  // Determine which message is currently "active" (being typed)
  let activeIdx = -1;
  for (let i = data.messages.length - 1; i >= 0; i--) {
    if (frame >= messageStarts[i]) {
      activeIdx = i;
      break;
    }
  }

  // Cursor blink: toggle every ~15 frames
  const cursorVisible = Math.floor(frame / 15) % 2 === 0;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "flex-start",
        padding: "80px 60px",
        height: "100%",
        fontFamily: MONO_FONT,
        gap: 18,
        position: "relative",
      }}
    >
      {/* Context percentage indicator */}
      {data.contextPercent != null && (
        <div
          style={{
            position: "absolute",
            top: 30,
            right: 40,
            fontFamily: MONO_FONT,
            fontSize: 22,
            color: COLORS.contextRed,
            opacity: interpolate(frame, [0, 10], [0, 1], {
              extrapolateRight: "clamp",
            }),
          }}
        >
          context: {data.contextPercent}%
        </div>
      )}

      {/* Messages */}
      {data.messages.map((msg, i) => {
        const startFrame = messageStarts[i];
        const timing = messageTiming[i];

        // Don't render if we haven't reached this message yet
        if (frame < startFrame) return null;

        const localFrame = frame - startFrame;
        const rawCharsTyped = Math.floor(localFrame * charsPerFrame);
        const maxChars = timing.textLen;
        const charsToShow = Math.min(rawCharsTyped, maxChars);
        const isTyping = charsToShow < maxChars;
        const isDone = charsToShow >= maxChars;

        // By default, typing is true for claude, false for others (instant appear)
        const shouldType = msg.typing ?? (msg.role === "claude");

        let displayText: string;
        if (shouldType) {
          displayText = msg.text.substring(0, charsToShow);
        } else {
          // Instant appear with a short fade-in
          displayText = msg.text.substring(0, maxChars);
        }

        // Fade in for instant messages
        const fadeIn = shouldType
          ? 1
          : interpolate(localFrame, [0, 6], [0, 1], {
              extrapolateRight: "clamp",
            });

        // Is this the last visible message and currently active?
        const isActiveMessage = i === activeIdx;
        const showBlockCursor =
          showCursor && isActiveMessage && shouldType && isTyping;
        const showBlinkCursor =
          showCursor && isActiveMessage && isDone && i === data.messages.length - 1;

        // Role label
        const labelColor =
          msg.role === "user"
            ? COLORS.userLabel
            : msg.role === "claude"
            ? COLORS.claudeLabel
            : COLORS.narrationText;

        const labelText =
          msg.role === "user"
            ? "USER:"
            : msg.role === "claude"
            ? "CLAUDE:"
            : "";

        // Narrator messages are rendered differently (italic, centered)
        if (msg.role === "narrator") {
          return (
            <div
              key={i}
              style={{
                color: COLORS.narrationText,
                fontSize: 26,
                fontStyle: "italic",
                textAlign: "center",
                padding: "12px 0",
                opacity: fadeIn,
                lineHeight: 1.6,
              }}
            >
              {displayText}
            </div>
          );
        }

        return (
          <div
            key={i}
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 4,
              opacity: fadeIn,
            }}
          >
            {/* Role label */}
            <span
              style={{
                color: labelColor,
                fontSize: 22,
                fontWeight: 700,
                letterSpacing: "0.04em",
              }}
            >
              {labelText}
            </span>

            {/* Message text */}
            <div
              style={{
                color: "#e0e0e0",
                fontSize: 28,
                lineHeight: 1.6,
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
                paddingLeft: 8,
              }}
            >
              {displayText}
              {/* Typing cursor (solid block while typing) */}
              {showBlockCursor && (
                <span
                  style={{
                    color: COLORS.cursorBlock,
                    opacity: 1,
                  }}
                >
                  {"\u2588"}
                </span>
              )}
              {/* Blinking cursor (after done typing, last message only) */}
              {showBlinkCursor && (
                <span
                  style={{
                    color: COLORS.cursorBlock,
                    opacity: cursorVisible ? 1 : 0,
                  }}
                >
                  {"\u2588"}
                </span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Narration sub-component
// ---------------------------------------------------------------------------

interface NarrationViewProps {
  phrases: NonNullable<ConversationData["phrases"]>;
  frame: number;
  fps: number;
  /** Offset in frames before the narration portion begins (for mixed mode). */
  frameOffset?: number;
}

const NarrationView: React.FC<NarrationViewProps> = ({
  phrases,
  frame,
  fps,
  frameOffset = 0,
}) => {
  const defaultDurationSec = 2;
  const fadeFrames = Math.round(fps * 0.3);

  // Calculate phrase timings
  let cumulative = frameOffset;
  const phraseTiming = phrases.map((phrase) => {
    const durationSec = phrase.duration ?? defaultDurationSec;
    const totalFrames = Math.round(durationSec * fps);
    const start = cumulative;
    cumulative += totalFrames;
    return { start, totalFrames, durationSec };
  });

  // Find current phrase
  let currentIdx = -1;
  for (let i = phrases.length - 1; i >= 0; i--) {
    if (frame >= phraseTiming[i].start) {
      currentIdx = i;
      break;
    }
  }

  if (currentIdx < 0) return null;

  const phrase = phrases[currentIdx];
  const timing = phraseTiming[currentIdx];
  const localFrame = frame - timing.start;
  const totalFrames = timing.totalFrames;

  // Fade in (first 0.3s)
  const fadeIn = interpolate(localFrame, [0, fadeFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Fade out (last 0.3s)
  const fadeOut = interpolate(
    localFrame,
    [totalFrames - fadeFrames, totalFrames],
    [1, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    },
  );

  const opacity = Math.min(fadeIn, fadeOut);

  // Determine color with special rules
  let color = phrase.color ?? COLORS.narrationText;
  let fontSize = phrase.fontSize ?? 48;
  let fontFamily = MONO_FONT;
  let bgOverride: string | undefined;

  const text = phrase.text;

  // Special: "READY." -> green, larger
  if (text === "READY.") {
    color = phrase.color ?? COLORS.green;
    fontSize = phrase.fontSize ?? 72;
  }
  // Special: starts with "[" -> red, monospace
  else if (text.startsWith("[")) {
    color = phrase.color ?? COLORS.red;
    fontFamily = MONO_FONT;
  }
  // Special: "Hello!" -> blue on navy bg
  else if (text === "Hello!") {
    color = phrase.color ?? COLORS.blue;
    bgOverride = COLORS.navy;
  }

  return (
    <AbsoluteFill
      style={{
        background: bgOverride || "transparent",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "100%",
          width: "100%",
          padding: "0 120px",
        }}
      >
        <span
          style={{
            fontFamily,
            fontSize,
            color,
            opacity,
            textAlign: "center",
            lineHeight: 1.4,
            fontWeight: 400,
            letterSpacing: "0.02em",
          }}
        >
          {text}
        </span>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Main Conversation component
// ---------------------------------------------------------------------------

export const Conversation: React.FC<Props> = ({
  data,
  accentColor,
  themeName,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName || "bigbrain");

  const variant = data.variant ?? "chat";
  const bg = data.background ?? (variant === "narration" ? NARRATION_BG : CHAT_BG);

  // Container fade-in
  const containerOpacity = interpolate(frame, [0, 10], [0, 1], {
    extrapolateRight: "clamp",
  });

  // ---------------------------------------------------------------------------
  // CHAT variant
  // ---------------------------------------------------------------------------

  if (variant === "chat") {
    return (
      <Background background={bg} themeName={themeName}>
        <AbsoluteFill style={{ opacity: containerOpacity }}>
          <ChatView data={data} frame={frame} fps={fps} />
        </AbsoluteFill>
      </Background>
    );
  }

  // ---------------------------------------------------------------------------
  // NARRATION variant
  // ---------------------------------------------------------------------------

  if (variant === "narration") {
    const phrases = data.phrases ?? [];
    return (
      <Background background={bg} themeName={themeName}>
        <AbsoluteFill style={{ opacity: containerOpacity }}>
          <NarrationView phrases={phrases} frame={frame} fps={fps} />
        </AbsoluteFill>
      </Background>
    );
  }

  // ---------------------------------------------------------------------------
  // MIXED variant: chat section first, then narration
  // ---------------------------------------------------------------------------

  const charsPerFrame = 3;
  const pauseFrames = Math.round(fps * 0.5);

  // Calculate total frames for chat section
  let chatTotalFrames = 0;
  for (const msg of data.messages) {
    const textLen =
      msg.cutoffAt != null
        ? Math.min(msg.text.length, msg.cutoffAt)
        : msg.text.length;
    const typingFrames = Math.ceil(textLen / charsPerFrame);
    chatTotalFrames += typingFrames + pauseFrames;
  }
  // Add a 1-second buffer after last message before narration starts
  const transitionBuffer = Math.round(fps * 1);
  const narrationStartFrame = chatTotalFrames + transitionBuffer;

  const phrases = data.phrases ?? [];
  const isInNarrationPhase = frame >= narrationStartFrame;

  // Cross-fade between chat and narration
  const chatOpacity = isInNarrationPhase
    ? interpolate(
        frame,
        [narrationStartFrame, narrationStartFrame + Math.round(fps * 0.5)],
        [1, 0],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
      )
    : 1;

  const narrationOpacity = isInNarrationPhase
    ? interpolate(
        frame,
        [narrationStartFrame, narrationStartFrame + Math.round(fps * 0.3)],
        [0, 1],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
      )
    : 0;

  // Background transitions from navy (chat) to black (narration)
  const mixedBg = isInNarrationPhase ? NARRATION_BG : CHAT_BG;

  return (
    <Background background={mixedBg} themeName={themeName}>
      <AbsoluteFill style={{ opacity: containerOpacity }}>
        {/* Chat layer */}
        {chatOpacity > 0 && (
          <AbsoluteFill style={{ opacity: chatOpacity }}>
            <ChatView data={data} frame={frame} fps={fps} />
          </AbsoluteFill>
        )}

        {/* Narration layer */}
        {narrationOpacity > 0 && phrases.length > 0 && (
          <AbsoluteFill style={{ opacity: narrationOpacity }}>
            <NarrationView
              phrases={phrases}
              frame={frame}
              fps={fps}
              frameOffset={narrationStartFrame}
            />
          </AbsoluteFill>
        )}
      </AbsoluteFill>
    </Background>
  );
};
