#!/usr/bin/env python3
"""VoxCPM2 TTS generator — text-to-speech, voice design, voice cloning.

Modes (auto-selected from flags):
  - plain TTS:          gen_voice.py "text" -o out.wav
  - voice design:       gen_voice.py "text" --design "A young woman, gentle voice" -o out.wav
  - controllable clone: gen_voice.py "text" --reference-wav ref.wav [--control "faster, cheerful"] -o out.wav
  - ultimate clone:     gen_voice.py "text" --prompt-wav ref.wav --prompt-text "transcript" -o out.wav

Run with the voxcpm venv:
  ~/voxcpm-venv/bin/python ~/2lab.ai/skills/voxcpm/scripts/gen_voice.py ...
"""
import argparse
import os
import sys
import time

# triton JIT compiles GPU kernels with gcc, which needs Python.h. The system
# lacks python3.12-dev (no sudo), so we ship the headers in the skill dir and
# expose them via CPATH before torch/triton import. (resolved 2026-06-15)
_HDR_BASE = os.path.expanduser("~/2lab.ai/skills/voxcpm/py312-include")
if os.path.isdir(_HDR_BASE):
    # Python.h is in python3.12/, and its pyconfig.h stub includes
    # <x86_64-linux-gnu/python3.12/pyconfig.h> relative to the base dir.
    _paths = [os.path.join(_HDR_BASE, "python3.12"), _HDR_BASE]
    _existing = os.environ.get("CPATH", "")
    os.environ["CPATH"] = os.pathsep.join(_paths + ([_existing] if _existing else []))


def main():
    ap = argparse.ArgumentParser(description="VoxCPM2 TTS")
    ap.add_argument("text", help="text to synthesize")
    ap.add_argument("-o", "--output", default="out.wav", help="output wav path")
    ap.add_argument("--model", default="openbmb/VoxCPM2", help="model id or local dir")
    ap.add_argument("--design", help="voice-design description (no reference needed); prepended as (desc)")
    ap.add_argument("--control", help="style control for cloning (speed/emotion); prepended as (ctrl)")
    ap.add_argument("--reference-wav", help="reference audio for controllable cloning")
    ap.add_argument("--prompt-wav", help="reference audio for ultimate cloning (audio continuation)")
    ap.add_argument("--prompt-text", help="exact transcript of --prompt-wav (ultimate cloning)")
    ap.add_argument("--cfg", type=float, default=2.0, help="cfg_value (default 2.0)")
    ap.add_argument("--timesteps", type=int, default=10, help="inference_timesteps (default 10)")
    ap.add_argument("--local-dir", help="if model already snapshot-downloaded, pass its dir here")
    args = ap.parse_args()

    import soundfile as sf
    from voxcpm import VoxCPM

    text = args.text
    if args.design:
        text = f"({args.design}){text}"
    elif args.control:
        text = f"({args.control}){text}"

    model_path = args.local_dir or args.model
    t0 = time.time()
    sys.stderr.write(f"[voxcpm] loading {model_path} ...\n")
    sys.stderr.flush()
    model = VoxCPM.from_pretrained(model_path, load_denoiser=False)
    sys.stderr.write(f"[voxcpm] model loaded in {time.time()-t0:.1f}s\n")
    sys.stderr.flush()

    kwargs = dict(text=text, cfg_value=args.cfg, inference_timesteps=args.timesteps)
    if args.reference_wav:
        kwargs["reference_wav_path"] = args.reference_wav
    if args.prompt_wav:
        kwargs["prompt_wav_path"] = args.prompt_wav
    if args.prompt_text:
        kwargs["prompt_text"] = args.prompt_text

    t1 = time.time()
    wav = model.generate(**kwargs)
    gen_s = time.time() - t1
    sf.write(args.output, wav, model.tts_model.sample_rate)
    dur = len(wav) / model.tts_model.sample_rate
    sys.stderr.write(
        f"[voxcpm] generated {dur:.2f}s audio in {gen_s:.1f}s "
        f"(RTF={gen_s/dur:.2f}) @ {model.tts_model.sample_rate}Hz\n"
    )
    print(args.output)


if __name__ == "__main__":
    main()
