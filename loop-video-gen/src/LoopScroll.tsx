import React from "react";
import {
  AbsoluteFill,
  Img,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export interface LoopScrollProps {
  images: string[];
  tileWidth: number;
  pxPerSec: number;
  height: number;
  direction: "ltr" | "rtl";
  background: string;
}

function resolveSrc(src: string): string {
  if (src.startsWith("http://") || src.startsWith("https://")) return src;
  return staticFile(src);
}

export const LoopScroll: React.FC<LoopScrollProps> = ({
  images,
  tileWidth,
  pxPerSec,
  height,
  direction,
  background,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const totalWidth = images.length * tileWidth;
  // modulo = wrap; one full loop = totalWidth px => seamless because
  // durationInFrames is computed as totalWidth / pxPerSec * fps.
  const traveled = ((frame / fps) * pxPerSec) % totalWidth;
  // rtl: content slides left (camera pans right->left). ltr: opposite.
  const offset = direction === "rtl" ? -traveled : traveled - totalWidth;

  const tiles = [...images, ...images];

  return (
    <AbsoluteFill style={{ background, overflow: "hidden" }}>
      <div
        style={{
          display: "flex",
          height,
          transform: `translateX(${offset}px)`,
          willChange: "transform",
        }}
      >
        {tiles.map((src, i) => (
          <Img
            key={i}
            src={resolveSrc(src)}
            style={{
              width: tileWidth,
              height,
              objectFit: "cover",
              flexShrink: 0,
              display: "block",
            }}
          />
        ))}
      </div>
    </AbsoluteFill>
  );
};
