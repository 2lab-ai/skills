import React from "react";
import { Background } from "../components/Background";
import { useStaggered, useFadeIn } from "../utils/animations";
import type { ListData } from "../types";
import { palette, hexToRgba, getTheme, type Theme } from "../utils/colors";

interface ListProps {
  data: ListData;
  accentColor?: string;
  themeName?: string;
}

const ListItem: React.FC<{ text: string; index: number; accent: string; ordered: boolean; theme: Theme }> = ({
  text,
  index,
  accent,
  ordered,
  theme,
}) => {
  const anim = useStaggered(index, 10);

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 24,
        padding: "16px 0",
        borderBottom: `1px solid ${hexToRgba(palette.white, 0.06)}`,
        ...anim,
      }}
    >
      <div
        style={{
          width: 38,
          height: 38,
          borderRadius: ordered ? 12 : 22,
          background: hexToRgba(accent, 0.15),
          border: `1px solid ${hexToRgba(accent, 0.3)}`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
        }}
      >
        <span style={{ color: accent, fontSize: 20, fontWeight: 700 }}>
          {ordered ? index + 1 : "→"}
        </span>
      </div>
      <span
        style={{
          color: theme.textPrimary,
          fontSize: 26,
          fontFamily: theme.fontFamily,
          fontWeight: 500,
          lineHeight: 1.5,
        }}
      >
        {text}
      </span>
    </div>
  );
};

export const List: React.FC<ListProps> = ({ data, accentColor, themeName }) => {
  const theme = getTheme(themeName);
  const accent = accentColor || theme.accent;
  const titleOpacity = useFadeIn(0, 12);

  return (
    <Background>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          padding: "80px 160px",
          height: "100%",
        }}
      >
        <h2
          style={{
            color: theme.textPrimary,
            fontSize: 44,
            fontFamily: theme.headingFont,
            fontWeight: 700,
            marginBottom: 48,
            opacity: titleOpacity,
            letterSpacing: "-0.02em",
          }}
        >
          {data.title}
        </h2>

        <div style={{ display: "flex", flexDirection: "column" }}>
          {data.items.map((item, i) => (
            <ListItem
              key={i}
              text={item}
              index={i}
              accent={accent}
              ordered={data.ordered ?? false}
              theme={theme}
            />
          ))}
        </div>
      </div>
    </Background>
  );
};
