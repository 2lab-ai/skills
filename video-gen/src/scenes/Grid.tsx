import React from "react";
import { Background } from "../components/Background";
import { useStaggered, useFadeIn } from "../utils/animations";
import type { GridData } from "../types";
import { palette, hexToRgba } from "../utils/colors";

interface GridProps {
  data: GridData;
  accentColor?: string;
}

const Card: React.FC<{
  icon?: string;
  title: string;
  description: string;
  index: number;
  accent: string;
}> = ({ icon, title, description, index, accent }) => {
  const anim = useStaggered(index, 8);

  return (
    <div
      style={{
        background: hexToRgba(palette.white, 0.04),
        border: `1px solid ${hexToRgba(palette.white, 0.08)}`,
        borderRadius: 20,
        padding: "36px 32px",
        display: "flex",
        flexDirection: "column",
        gap: 16,
        ...anim,
      }}
    >
      {icon && (
        <span style={{ fontSize: 42 }}>{icon}</span>
      )}
      <h3
        style={{
          color: palette.white,
          fontSize: 28,
          fontWeight: 700,
          margin: 0,
          letterSpacing: "-0.01em",
        }}
      >
        {title}
      </h3>
      <p
        style={{
          color: palette.gray300,
          fontSize: 22,
          fontWeight: 400,
          margin: 0,
          lineHeight: 1.6,
        }}
      >
        {description}
      </p>
    </div>
  );
};

export const Grid: React.FC<GridProps> = ({ data, accentColor }) => {
  const accent = accentColor || palette.accent;
  const titleOpacity = useFadeIn(0, 12);
  const cols = data.cards.length <= 3 ? data.cards.length : data.cards.length <= 4 ? 2 : 3;

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
        <h2
          style={{
            color: palette.white,
            fontSize: 52,
            fontWeight: 700,
            marginBottom: 48,
            opacity: titleOpacity,
            letterSpacing: "-0.02em",
          }}
        >
          {data.title}
        </h2>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: `repeat(${cols}, 1fr)`,
            gap: 24,
            flex: 1,
            alignContent: "start",
          }}
        >
          {data.cards.map((card, i) => (
            <Card key={i} {...card} index={i} accent={accent} />
          ))}
        </div>
      </div>
    </Background>
  );
};
