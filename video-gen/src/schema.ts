import { z } from "zod";

const SceneTypeSchema = z.enum(["hero", "list", "grid", "code", "flow", "chat", "stat"]);

const StyleSchema = z.object({
  background: z.string().optional(),
  accentColor: z.string().optional(),
  textColor: z.string().optional(),
}).optional();

const SceneConfigSchema = z.object({
  id: z.string().min(1),
  type: SceneTypeSchema,
  narration: z.string().min(1),
  durationInSeconds: z.number().positive().optional(),
  data: z.record(z.unknown()),
  style: StyleSchema,
});

export const VideoConfigSchema = z.object({
  title: z.string().min(1),
  fps: z.number().int().positive().default(30),
  width: z.number().int().positive().default(1920),
  height: z.number().int().positive().default(1080),
  defaultStyle: z.object({
    background: z.string().default("#0f0f23"),
    accentColor: z.string().default("#00d4ff"),
    textColor: z.string().default("#ffffff"),
    fontFamily: z.string().default("'Pretendard', 'Noto Sans KR', sans-serif"),
  }),
  scenes: z.array(SceneConfigSchema).min(1),
});

export type VideoConfigInput = z.input<typeof VideoConfigSchema>;
export type VideoConfigOutput = z.output<typeof VideoConfigSchema>;
