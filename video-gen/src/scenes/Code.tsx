import React from "react";
import { useCurrentFrame, interpolate } from "remotion";
import { Background } from "../components/Background";
import { useFadeIn } from "../utils/animations";
import type { CodeData } from "../types";
import { palette, hexToRgba } from "../utils/colors";

interface CodeProps {
  data: CodeData;
  accentColor?: string;
}

// Simple syntax-like coloring by token type
function tokenize(line: string): Array<{ text: string; color: string }> {
  const tokens: Array<{ text: string; color: string }> = [];
  const keywords = /\b(const|let|var|function|return|if|else|for|while|import|export|from|class|interface|type|async|await|new|this|true|false|null|undefined|def|print|self)\b/g;
  const strings = /(["'`])(?:(?=(\\?))\2.)*?\1/g;
  const comments = /(\/\/.*$|#.*$)/gm;
  const numbers = /\b(\d+\.?\d*)\b/g;

  let remaining = line;
  if (!remaining.trim()) {
    return [{ text: remaining || " ", color: palette.gray500 }];
  }

  // Simple approach: color the whole line with basic heuristics
  const trimmed = remaining.trim();
  if (trimmed.startsWith("//") || trimmed.startsWith("#")) {
    return [{ text: remaining, color: "#6a9955" }];
  }

  // Split by tokens and colorize
  const parts = remaining.split(/(\s+|[{}()[\];,.:=<>+\-*/&|!?])/);
  const keywordSet = new Set([
    "const", "let", "var", "function", "return", "if", "else", "for", "while",
    "import", "export", "from", "class", "interface", "type", "async", "await",
    "new", "this", "def", "print", "self", "true", "false", "null", "undefined",
  ]);

  for (const part of parts) {
    if (!part) continue;
    if (keywordSet.has(part)) {
      tokens.push({ text: part, color: "#c586c0" });
    } else if (/^["'`]/.test(part)) {
      tokens.push({ text: part, color: "#ce9178" });
    } else if (/^\d/.test(part)) {
      tokens.push({ text: part, color: "#b5cea8" });
    } else if (/^[{}()[\];,.:=<>+\-*/&|!?]$/.test(part)) {
      tokens.push({ text: part, color: palette.gray300 });
    } else {
      tokens.push({ text: part, color: "#9cdcfe" });
    }
  }

  return tokens.length ? tokens : [{ text: remaining, color: palette.white }];
}

export const Code: React.FC<CodeProps> = ({ data, accentColor }) => {
  const frame = useCurrentFrame();
  const accent = accentColor || palette.accent;
  const titleOpacity = useFadeIn(0, 12);
  const lines = data.code.split("\n");
  const highlights = new Set(data.highlights || []);

  // Typewriter effect: reveal lines progressively
  const visibleLines = Math.min(
    lines.length,
    Math.floor(interpolate(frame, [10, 10 + lines.length * 4], [0, lines.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }))
  );

  return (
    <Background>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          padding: "80px 120px",
          height: "100%",
        }}
      >
        {data.title && (
          <h2
            style={{
              color: palette.white,
              fontSize: 44,
              fontWeight: 700,
              marginBottom: 36,
              opacity: titleOpacity,
              letterSpacing: "-0.02em",
            }}
          >
            {data.title}
          </h2>
        )}

        {/* Code editor frame */}
        <div
          style={{
            background: "#1e1e2e",
            borderRadius: 16,
            border: `1px solid ${hexToRgba(palette.white, 0.1)}`,
            overflow: "hidden",
            flex: 1,
          }}
        >
          {/* Title bar */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "14px 20px",
              borderBottom: `1px solid ${hexToRgba(palette.white, 0.06)}`,
            }}
          >
            <div style={{ width: 12, height: 12, borderRadius: 6, background: "#ff5f57" }} />
            <div style={{ width: 12, height: 12, borderRadius: 6, background: "#febc2e" }} />
            <div style={{ width: 12, height: 12, borderRadius: 6, background: "#28c840" }} />
            <span
              style={{
                color: palette.gray500,
                fontSize: 14,
                marginLeft: 12,
                fontFamily: "monospace",
              }}
            >
              {data.language}
            </span>
          </div>

          {/* Code lines */}
          <div style={{ padding: "24px 0", overflowY: "hidden" }}>
            {lines.slice(0, visibleLines).map((line, i) => {
              const isHighlight = highlights.has(i + 1);
              return (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    padding: "3px 24px",
                    background: isHighlight
                      ? hexToRgba(accent, 0.1)
                      : "transparent",
                    borderLeft: isHighlight
                      ? `3px solid ${accent}`
                      : "3px solid transparent",
                  }}
                >
                  <span
                    style={{
                      color: palette.gray500,
                      fontSize: 18,
                      fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                      width: 48,
                      textAlign: "right",
                      marginRight: 24,
                      userSelect: "none",
                    }}
                  >
                    {i + 1}
                  </span>
                  <span
                    style={{
                      fontSize: 20,
                      fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                      whiteSpace: "pre",
                    }}
                  >
                    {tokenize(line).map((token, j) => (
                      <span key={j} style={{ color: token.color }}>
                        {token.text}
                      </span>
                    ))}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </Background>
  );
};
