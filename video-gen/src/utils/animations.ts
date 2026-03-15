import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export function useFadeIn(delay = 0, duration = 15) {
  const frame = useCurrentFrame();
  return interpolate(frame - delay, [0, duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
}

export function useSlideUp(delay = 0, distance = 40) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = spring({ frame: frame - delay, fps, config: { damping: 20, stiffness: 100 } });
  return interpolate(progress, [0, 1], [distance, 0]);
}

export function useSpring(delay = 0) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - delay, fps, config: { damping: 20, stiffness: 100 } });
}

export function useStaggered(index: number, staggerFrames = 8) {
  const delay = index * staggerFrames;
  const opacity = useFadeIn(delay);
  const translateY = useSlideUp(delay);
  return { opacity, transform: `translateY(${translateY}px)` };
}

export function useTypewriter(text: string, charsPerFrame = 0.8) {
  const frame = useCurrentFrame();
  const chars = Math.floor(frame * charsPerFrame);
  return text.slice(0, chars);
}

export function useProgressBar(totalFrames: number) {
  const frame = useCurrentFrame();
  return Math.min(frame / totalFrames, 1);
}
