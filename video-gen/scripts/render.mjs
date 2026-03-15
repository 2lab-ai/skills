/**
 * Programmatic Remotion render script.
 * Bypasses CLI limitations for Chromium flags.
 */
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, "..");
const entryPoint = path.join(projectRoot, "src", "Root.tsx");
const outputPath = process.argv[2] || path.join(projectRoot, "out", "video.mp4");

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
  console.log("[render] Bundling...");
  const bundled = await bundle({
    entryPoint,
    onProgress: (progress) => {
      if (progress % 25 === 0) {
        process.stdout.write(`  Bundling ${progress}%\r`);
      }
    },
  });
  console.log("[render] Bundle done");

  console.log("[render] Getting composition...");
  const composition = await selectComposition({
    serveUrl: bundled,
    id: "VideoComposition",
    chromiumOptions,
    browserExecutable,
  });

  console.log(`[render] Composition: ${composition.width}x${composition.height}, ${composition.durationInFrames} frames @ ${composition.fps}fps`);
  console.log(`[render] Duration: ${(composition.durationInFrames / composition.fps).toFixed(1)}s`);

  console.log("[render] Rendering...");
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
    onProgress: ({ progress }) => {
      const pct = Math.round(progress * 100);
      if (pct >= lastProgress + 5) {
        console.log(`  Rendering ${pct}%`);
        lastProgress = pct;
      }
    },
    ffmpegExecutable: ffmpegPath,
  });

  console.log(`[render] Done! Output: ${outputPath}`);
}

main().catch((err) => {
  console.error("[render] FATAL:", err.message);
  console.error(err.stack);
  process.exit(1);
});
