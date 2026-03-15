import React from "react";
import {
  useCurrentFrame,
  spring,
  interpolate,
  useVideoConfig,
  Img,
  OffthreadVideo,
  staticFile,
  Easing,
} from "remotion";
import { Background } from "../components/Background";
import {
  useFadeIn,
  useSlideUp,
  useSlideLeft,
  useSlideRight,
  useClipReveal,
  usePulse,
} from "../utils/animations";
import type { ImageData } from "../types";
import { palette, hexToRgba, getTheme } from "../utils/colors";

interface ImageProps {
  data: ImageData;
  accentColor?: string;
  themeName?: string;
}

export const Image: React.FC<ImageProps> = ({ data, accentColor, themeName }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = getTheme(themeName);
  const accent = accentColor || theme.accent;

  const layout = data.layout ?? "centered";

  // Resolve the image source: URL or local static file
  const imgSrc = data.gifUrl || data.src;
  const resolvedSrc =
    imgSrc.startsWith("http://") || imgSrc.startsWith("https://")
      ? imgSrc
      : staticFile(imgSrc);

  // Determine if this is a video file (mp4/webm from GIF conversion)
  const isVideo = /\.(mp4|webm|mov)$/i.test(imgSrc);

  // Unified media renderer — video files use OffthreadVideo, images use Img
  const MediaElement: React.FC<{ style: React.CSSProperties }> = ({ style }) =>
    isVideo ? (
      <OffthreadVideo
        src={resolvedSrc}
        style={style}
        muted
      />
    ) : (
      <Img src={resolvedSrc} style={style} />
    );

  // Animations (all hooks called unconditionally at top level)
  const imageFade = useFadeIn(0, 20);
  const titleFade = useFadeIn(8, 15);
  const titleSlide = useSlideUp(8, 30);
  const captionFade = useFadeIn(18, 15);
  const captionSlide = useSlideUp(18, 25);

  // Image scale-in spring
  const imageSpring = spring({
    frame,
    fps,
    config: { damping: 18, stiffness: 80 },
  });
  const imageScale = interpolate(imageSpring, [0, 1], [1.05, 1]);

  // Image reveal clip
  const clipReveal = useClipReveal(0, 25, "left");

  // Split layout hooks (always called regardless of layout)
  const slideRight = useSlideRight(0, 50);
  const slideLeft = useSlideLeft(0, 50);

  // --- FULLSCREEN LAYOUT ---
  if (layout === "fullscreen") {
    return (
      <Background background={theme.background}>
        <div
          style={{
            width: "100%",
            height: "100%",
            position: "relative",
            overflow: "hidden",
          }}
        >
          {/* Fullscreen media (image or animated GIF/video) */}
          <MediaElement
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              opacity: imageFade,
              transform: `scale(${imageScale})`,
              clipPath: isVideo ? undefined : clipReveal,
            }}
          />

          {/* Dark gradient overlay for text legibility */}
          <div
            style={{
              position: "absolute",
              bottom: 0,
              left: 0,
              right: 0,
              height: "50%",
              background: "linear-gradient(transparent, rgba(0,0,0,0.7))",
              opacity: imageFade,
            }}
          />

          {/* Text overlay */}
          {(data.title || data.caption) && (
            <div
              style={{
                position: "absolute",
                bottom: 60,
                left: 80,
                right: 80,
                zIndex: 2,
              }}
            >
              {data.title && (
                <h2
                  style={{
                    color: "#ffffff",
                    fontFamily: theme.headingFont,
                    fontSize: 46,
                    fontWeight: 700,
                    margin: 0,
                    marginBottom: data.caption ? 12 : 0,
                    opacity: titleFade,
                    transform: `translateY(${titleSlide}px)`,
                    letterSpacing: "-0.02em",
                    textShadow: "0 2px 20px rgba(0,0,0,0.5)",
                  }}
                >
                  {data.title}
                </h2>
              )}
              {data.caption && (
                <p
                  style={{
                    color: "rgba(255,255,255,0.8)",
                    fontFamily: theme.fontFamily,
                    fontSize: 24,
                    fontWeight: 400,
                    margin: 0,
                    opacity: captionFade,
                    transform: `translateY(${captionSlide}px)`,
                    textShadow: "0 1px 10px rgba(0,0,0,0.5)",
                  }}
                >
                  {data.caption}
                </p>
              )}
            </div>
          )}
        </div>
      </Background>
    );
  }

  // --- SPLIT LAYOUTS ---
  if (layout === "split-left" || layout === "split-right") {
    const imageOnLeft = layout === "split-left";
    const imgSlide = imageOnLeft ? slideRight : slideLeft;

    const imageElement = (
      <div
        style={{
          flex: 1,
          overflow: "hidden",
          borderRadius: theme.borderRadius,
          position: "relative",
        }}
      >
        <MediaElement
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            opacity: imageFade,
            transform: `translateX(${imgSlide}px) scale(${imageScale})`,
          }}
        />

        {/* Subtle accent border glow */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            borderRadius: theme.borderRadius,
            border: `2px solid ${hexToRgba(accent, 0.15)}`,
            pointerEvents: "none",
          }}
        />
      </div>
    );

    const textElement = (
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: "0 40px",
          gap: 16,
        }}
      >
        {data.title && (
          <h2
            style={{
              color: theme.textPrimary,
              fontFamily: theme.headingFont,
              fontSize: 42,
              fontWeight: 700,
              margin: 0,
              opacity: titleFade,
              transform: `translateY(${titleSlide}px)`,
              letterSpacing: "-0.02em",
              lineHeight: 1.2,
            }}
          >
            {data.title}
          </h2>
        )}
        {data.caption && (
          <p
            style={{
              color: theme.textSecondary,
              fontFamily: theme.fontFamily,
              fontSize: 23,
              fontWeight: 400,
              margin: 0,
              opacity: captionFade,
              transform: `translateY(${captionSlide}px)`,
              lineHeight: 1.6,
            }}
          >
            {data.caption}
          </p>
        )}
      </div>
    );

    return (
      <Background background={theme.background}>
        <div
          style={{
            display: "flex",
            flexDirection: "row",
            padding: "60px 80px",
            height: "100%",
            gap: 40,
            alignItems: "stretch",
          }}
        >
          {imageOnLeft ? imageElement : textElement}
          {imageOnLeft ? textElement : imageElement}
        </div>
      </Background>
    );
  }

  // --- CENTERED LAYOUT (default) ---
  return (
    <Background background={theme.background}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          height: "100%",
          padding: "60px 100px",
          gap: 24,
        }}
      >
        {/* Title above */}
        {data.title && (
          <h2
            style={{
              color: theme.textPrimary,
              fontFamily: theme.headingFont,
              fontSize: 42,
              fontWeight: 700,
              margin: 0,
              opacity: titleFade,
              transform: `translateY(${titleSlide}px)`,
              letterSpacing: "-0.02em",
              textAlign: "center",
            }}
          >
            {data.title}
          </h2>
        )}

        {/* Image container */}
        <div
          style={{
            maxWidth: 800,
            maxHeight: 500,
            borderRadius: theme.borderRadius,
            overflow: "hidden",
            position: "relative",
            boxShadow: `0 20px 60px ${hexToRgba("#000", 0.4)}, 0 0 40px ${hexToRgba(accent, 0.1)}`,
          }}
        >
          <MediaElement
            style={{
              maxWidth: "100%",
              maxHeight: 500,
              objectFit: "contain",
              display: "block",
              opacity: imageFade,
              transform: `scale(${imageScale})`,
              clipPath: isVideo ? undefined : clipReveal,
            }}
          />

          {/* Border overlay */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              borderRadius: theme.borderRadius,
              border: `1px solid ${hexToRgba(theme.textPrimary, 0.1)}`,
              pointerEvents: "none",
            }}
          />
        </div>

        {/* Caption below */}
        {data.caption && (
          <p
            style={{
              color: theme.textSecondary,
              fontFamily: theme.fontFamily,
              fontSize: 22,
              fontWeight: 400,
              margin: 0,
              opacity: captionFade,
              transform: `translateY(${captionSlide}px)`,
              textAlign: "center",
              maxWidth: 700,
              lineHeight: 1.5,
            }}
          >
            {data.caption}
          </p>
        )}
      </div>
    </Background>
  );
};
