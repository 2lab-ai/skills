import { interpolate, spring, useCurrentFrame, useVideoConfig, Easing } from "remotion";

// ============================================================
// BASIC ANIMATIONS
// ============================================================

export function useFadeIn(delay = 0, duration = 15) {
  const frame = useCurrentFrame();
  return interpolate(frame - delay, [0, duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
}

export function useFadeOut(startFrame: number, duration = 15) {
  const frame = useCurrentFrame();
  return interpolate(frame - startFrame, [0, duration], [1, 0], {
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

export function useSlideDown(delay = 0, distance = 40) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = spring({ frame: frame - delay, fps, config: { damping: 20, stiffness: 100 } });
  return interpolate(progress, [0, 1], [-distance, 0]);
}

export function useSlideLeft(delay = 0, distance = 60) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = spring({ frame: frame - delay, fps, config: { damping: 20, stiffness: 100 } });
  return interpolate(progress, [0, 1], [distance, 0]);
}

export function useSlideRight(delay = 0, distance = 60) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = spring({ frame: frame - delay, fps, config: { damping: 20, stiffness: 100 } });
  return interpolate(progress, [0, 1], [-distance, 0]);
}

export function useSpring(delay = 0) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - delay, fps, config: { damping: 20, stiffness: 100 } });
}

// ============================================================
// ATTENTION / EMPHASIS
// ============================================================

export function useBounceIn(delay = 0) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 8, stiffness: 200, mass: 0.5 } });
  return {
    opacity: interpolate(s, [0, 0.3], [0, 1], { extrapolateRight: "clamp" }),
    transform: `scale(${interpolate(s, [0, 1], [0.3, 1])})`,
  };
}

export function useElasticScale(delay = 0) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 6, stiffness: 150, mass: 0.8 } });
  return interpolate(s, [0, 1], [0, 1]);
}

export function usePulse(speed = 60) {
  const frame = useCurrentFrame();
  return 1 + Math.sin(frame / speed * Math.PI * 2) * 0.05;
}

export function useShake(delay = 0, intensity = 4, speed = 3) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const entered = spring({ frame: frame - delay, fps, config: { damping: 20, stiffness: 100 } });
  const shakeX = Math.sin(frame * speed) * intensity * (1 - entered);
  return shakeX;
}

export function useGlow(speed = 90) {
  const frame = useCurrentFrame();
  return 0.5 + Math.sin(frame / speed * Math.PI * 2) * 0.5;
}

export function useFloat(speed = 80, distance = 8) {
  const frame = useCurrentFrame();
  return Math.sin(frame / speed * Math.PI * 2) * distance;
}

export function useRotateIn(delay = 0, degrees = 10) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 15, stiffness: 80 } });
  return interpolate(s, [0, 1], [-degrees, 0]);
}

// ============================================================
// STAGGERED / COMPOUND
// ============================================================

export function useStaggered(index: number, staggerFrames = 8) {
  const delay = index * staggerFrames;
  const opacity = useFadeIn(delay);
  const translateY = useSlideUp(delay);
  return { opacity, transform: `translateY(${translateY}px)` };
}

export function useStaggeredScale(index: number, staggerFrames = 8) {
  const delay = index * staggerFrames;
  const opacity = useFadeIn(delay);
  const scale = useElasticScale(delay);
  return { opacity, transform: `scale(${scale})` };
}

export function useStaggeredSlideLeft(index: number, staggerFrames = 8) {
  const delay = index * staggerFrames;
  const opacity = useFadeIn(delay);
  const translateX = useSlideLeft(delay);
  return { opacity, transform: `translateX(${translateX}px)` };
}

export function useStaggeredSlideRight(index: number, staggerFrames = 8) {
  const delay = index * staggerFrames;
  const opacity = useFadeIn(delay);
  const translateX = useSlideRight(delay);
  return { opacity, transform: `translateX(${translateX}px)` };
}

// ============================================================
// TEXT ANIMATIONS
// ============================================================

export function useTypewriter(text: string, charsPerFrame = 0.8) {
  const frame = useCurrentFrame();
  const chars = Math.floor(frame * charsPerFrame);
  return text.slice(0, chars);
}

export function useWordReveal(text: string, wordsPerSecond = 3) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const words = text.split(" ");
  const framesPerWord = fps / wordsPerSecond;
  const visibleWords = Math.min(words.length, Math.floor(frame / framesPerWord));
  return {
    words,
    visibleCount: visibleWords,
    getText: () => words.slice(0, visibleWords).join(" "),
  };
}

export function useCountUp(target: number, delay = 0, duration = 30) {
  const frame = useCurrentFrame();
  const progress = interpolate(frame - delay, [0, duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return Math.round(target * progress);
}

// ============================================================
// PROGRESS / UTILITY
// ============================================================

export function useProgressBar(totalFrames: number) {
  const frame = useCurrentFrame();
  return Math.min(frame / totalFrames, 1);
}

export function useRevealLine(delay = 0, duration = 20) {
  const frame = useCurrentFrame();
  return interpolate(frame - delay, [0, duration], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
}

export function useClipReveal(delay = 0, duration = 20, direction: "left" | "right" | "top" | "bottom" = "left") {
  const frame = useCurrentFrame();
  const progress = interpolate(frame - delay, [0, duration], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  switch (direction) {
    case "left": return `inset(0 ${100 - progress}% 0 0)`;
    case "right": return `inset(0 0 0 ${100 - progress}%)`;
    case "top": return `inset(0 0 ${100 - progress}% 0)`;
    case "bottom": return `inset(${100 - progress}% 0 0 0)`;
  }
}

// ============================================================
// SCENE TRANSITIONS
// ============================================================

export type EntranceType =
  | "fadeSlideUp" | "fadeSlideDown" | "fadeSlideLeft" | "fadeSlideRight"
  | "zoomIn" | "zoomOut" | "bounceIn" | "flipIn" | "none";

export function useSceneEntrance(type: EntranceType = "fadeSlideUp", delay = 0) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 15, stiffness: 80 } });

  switch (type) {
    case "fadeSlideUp":
      return { opacity: s, transform: `translateY(${interpolate(s, [0, 1], [40, 0])}px)` };
    case "fadeSlideDown":
      return { opacity: s, transform: `translateY(${interpolate(s, [0, 1], [-40, 0])}px)` };
    case "fadeSlideLeft":
      return { opacity: s, transform: `translateX(${interpolate(s, [0, 1], [60, 0])}px)` };
    case "fadeSlideRight":
      return { opacity: s, transform: `translateX(${interpolate(s, [0, 1], [-60, 0])}px)` };
    case "zoomIn":
      return { opacity: s, transform: `scale(${interpolate(s, [0, 1], [0.8, 1])})` };
    case "zoomOut":
      return { opacity: s, transform: `scale(${interpolate(s, [0, 1], [1.2, 1])})` };
    case "bounceIn":
      return useBounceIn(delay);
    case "flipIn":
      return { opacity: s, transform: `perspective(600px) rotateY(${interpolate(s, [0, 1], [90, 0])}deg)` };
    case "none":
      return { opacity: 1, transform: "none" };
    default:
      return { opacity: s, transform: `translateY(${interpolate(s, [0, 1], [40, 0])}px)` };
  }
}

// ============================================================
// PARTICLE / DECORATIVE
// ============================================================

export function useParticlePosition(
  index: number,
  config: { speed?: number; spread?: number; baseX?: number; baseY?: number } = {}
) {
  const frame = useCurrentFrame();
  const { speed = 0.5, spread = 200, baseX = 50, baseY = 50 } = config;
  const seed = index * 137.508;
  const x = baseX + Math.sin(frame * speed * 0.01 + seed) * spread * Math.cos(seed);
  const y = baseY + Math.cos(frame * speed * 0.01 + seed * 0.7) * spread * Math.sin(seed);
  const opacity = 0.3 + Math.sin(frame * 0.02 + seed) * 0.3;
  return { x: `${x}%`, y: `${y}%`, opacity };
}
