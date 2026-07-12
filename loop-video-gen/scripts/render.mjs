/**
 * Programmatic Remotion render for the LoopScroll composition.
 * Reads public/loop-props.json (written by make-loop.sh) for dimensions.
 */
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, "..");
const entryPoint = path.join(projectRoot, "src", "Root.tsx");
const outputPath = process.argv[2] || path.join(projectRoot, "out", "loop.mp4");

const chromiumOptions = {
  args: [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--single-process",
    "--no-zygote",
  ],
};

const browserExecutable = "/usr/bin/chromium-browser";
const ffmpegPath = path.join(process.env.HOME || "", ".local", "bin", "ffmpeg");

async function main() {
  const props = JSON.parse(
    fs.readFileSync(path.join(projectRoot, "public", "loop-props.json"), "utf8"),
  );

  console.log("[render] Bundling...");
  const bundled = await bundle({ entryPoint });
  console.log("[render] Bundle done");

  console.log("[render] Getting composition...");
  const composition = await selectComposition({
    serveUrl: bundled,
    id: "LoopScroll",
    chromiumOptions,
    browserExecutable,
  });

  console.log(
    `[render] ${composition.width}x${composition.height}, ${composition.durationInFrames} frames @ ${composition.fps}fps (${(composition.durationInFrames / composition.fps).toFixed(2)}s)`,
  );
  console.log(
    `[render] direction=${props.direction} tileWidth=${props.tileWidth} pxPerSec=${props.pxPerSec} tiles=${props.images.length}`,
  );

  let lastProgress = 0;
  await renderMedia({
    composition,
    serveUrl: bundled,
    codec: "h264",
    outputLocation: outputPath,
    imageFormat: "jpeg",
    chromiumOptions,
    browserExecutable,
    concurrency: 1,
    ffmpegExecutable: ffmpegPath,
    onProgress: ({ progress }) => {
      const pct = Math.round(progress * 100);
      if (pct >= lastProgress + 10) {
        console.log(`  Rendering ${pct}%`);
        lastProgress = pct;
      }
    },
  });

  console.log(`[render] Done! Output: ${outputPath}`);
}

main().catch((err) => {
  console.error("[render] FATAL:", err.message);
  console.error(err.stack);
  process.exit(1);
});
