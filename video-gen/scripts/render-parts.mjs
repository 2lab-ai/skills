import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import path from "node:path";
import { fileURLToPath } from "node:url";
import v8 from "node:v8";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, "..");
const entryPoint = path.join(projectRoot, "src", "Root.tsx");

const partNum = parseInt(process.argv[2] || "1");
const totalParts = parseInt(process.argv[3] || "4");

// Log memory stats
const heapLimit = Math.round(v8.getHeapStatistics().heap_size_limit / 1024 / 1024);
console.log(`[memory] v8 heap limit: ${heapLimit}MB`);

const chromiumOptions = {
  args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--single-process", "--no-zygote"],
};

const browserExecutable = "/usr/bin/chromium-browser";
const ffmpegPath = path.join(process.env.HOME || "", ".local", "bin", "ffmpeg");

async function main() {
  console.log("[render-part " + partNum + "/" + totalParts + "] Bundling...");
  const bundled = await bundle({ entryPoint });
  console.log("[render-part " + partNum + "/" + totalParts + "] Bundle done");

  const composition = await selectComposition({
    serveUrl: bundled,
    id: "VideoComposition",
    chromiumOptions,
    browserExecutable,
  });

  const totalFrames = composition.durationInFrames;
  const framesPerPart = Math.ceil(totalFrames / totalParts);
  const startFrame = (partNum - 1) * framesPerPart;
  const endFrame = Math.min(partNum * framesPerPart - 1, totalFrames - 1);

  console.log("[render-part " + partNum + "/" + totalParts + "] Total: " + totalFrames + ", rendering frames " + startFrame + "-" + endFrame + " (" + (endFrame - startFrame + 1) + " frames)");

  const outputPath = path.join(projectRoot, "out", "part-" + partNum + ".mp4");

  await renderMedia({
    composition,
    serveUrl: bundled,
    codec: "h264",
    outputLocation: outputPath,
    imageFormat: "jpeg",
    chromiumOptions,
    browserExecutable,
    concurrency: 1,
    frameRange: [startFrame, endFrame],
    onProgress: ({ progress }) => {
      const pct = Math.round(progress * 100);
      if (pct % 10 === 0) {
        const mem = process.memoryUsage();
        const heapUsed = Math.round(mem.heapUsed / 1024 / 1024);
        const rss = Math.round(mem.rss / 1024 / 1024);
        console.log("  Part " + partNum + " rendering " + pct + "% (heap: " + heapUsed + "MB, rss: " + rss + "MB)");
      }
    },
    ffmpegExecutable: ffmpegPath,
  });

  console.log("[render-part " + partNum + "/" + totalParts + "] Done\! Output: " + outputPath);
}

main().catch((err) => {
  console.error("[render-part " + partNum + "] FATAL:", err.message);
  process.exit(1);
});
