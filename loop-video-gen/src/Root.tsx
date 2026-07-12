import React from "react";
import { Composition, registerRoot } from "remotion";
import { LoopScroll, type LoopScrollProps } from "./LoopScroll";
import propsData from "../public/loop-props.json";

interface LoopConfig extends LoopScrollProps {
  width: number;
  fps: number;
}

const config = propsData as LoopConfig;

const totalWidth = config.images.length * config.tileWidth;
// Exactly one full loop = perfectly seamless (end frame == start frame).
const durationInFrames = Math.max(
  1,
  Math.round((totalWidth / config.pxPerSec) * config.fps),
);

const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="LoopScroll"
      component={LoopScroll}
      durationInFrames={durationInFrames}
      fps={config.fps}
      width={config.width}
      height={config.height}
      defaultProps={{
        images: config.images,
        tileWidth: config.tileWidth,
        pxPerSec: config.pxPerSec,
        height: config.height,
        direction: config.direction,
        background: config.background,
      }}
    />
  );
};

registerRoot(RemotionRoot);
