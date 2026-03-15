import { readFileSync } from "node:fs";
import { VideoConfigSchema } from "../src/schema";

const configPath = process.argv[2] || "video-config.json";

try {
  const raw = JSON.parse(readFileSync(configPath, "utf8"));
  const result = VideoConfigSchema.safeParse(raw);

  if (result.success) {
    console.log(`✅ Valid config: ${result.data.scenes.length} scenes`);
    for (const scene of result.data.scenes) {
      console.log(`   [${scene.type}] ${scene.id}: ${scene.narration.slice(0, 60)}...`);
    }
  } else {
    console.error("❌ Validation errors:");
    for (const issue of result.error.issues) {
      console.error(`   ${issue.path.join(".")}: ${issue.message}`);
    }
    process.exit(1);
  }
} catch (err) {
  console.error(`❌ Failed to read/parse ${configPath}:`, err);
  process.exit(1);
}
