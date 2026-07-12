#!/usr/bin/env python3
"""
Fish-TTS Glitch Detector v5
Detects the specific failure fingerprint of Fish-TTS:
  - Mid-content digital silence in last 6 seconds (>=100ms)
  - Followed by 0.90~1.05s of audio at exactly ~-15.6dB peak
  - Followed by tail silence
This fingerprint is consistent across all confirmed broken outputs.

Usage: python3 detect_glitch.py <wav_file>
       python3 detect_glitch.py <directory>  # scan all *.wav
"""
import numpy as np, wave, os, sys, glob

def load_wav(path):
    with wave.open(path, 'rb') as w:
        sr = w.getframerate()
        n = w.getnframes()
        data = w.readframes(n)
        ch = w.getnchannels()
    arr = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
    if ch == 2:
        arr = arr.reshape(-1, 2).mean(axis=1)
    return arr, sr

def detect_glitch(path):
    audio, sr = load_wav(path)
    dur = len(audio) / sr
    silent = np.abs(audio) < 1e-6
    runs = []
    in_run = False; rs = 0
    for i, s in enumerate(silent):
        if s and not in_run:
            in_run = True; rs = i
        elif not s and in_run:
            in_run = False
            d = (i - rs) / sr
            if d >= 0.05:
                runs.append((rs/sr, i/sr, d))
    if in_run:
        d = (len(silent) - rs) / sr
        if d >= 0.05:
            runs.append((rs/sr, len(silent)/sr, d))
    end_zone = [r for r in runs if r[0] > dur - 6]
    tail = [r for r in end_zone if r[1] > dur - 0.05]
    mid_drops = [r for r in end_zone if r[1] <= dur - 0.05 and r[2] >= 0.1]
    if not mid_drops or not tail:
        return False, None
    last_drop = mid_drops[-1]; t = tail[0]
    gap = t[0] - last_drop[1]
    if not (0.90 <= gap <= 1.05):
        return False, None
    gap_audio = audio[int(last_drop[1]*sr):int(t[0]*sr)]
    if len(gap_audio) == 0:
        return False, None
    peak_db = 20*np.log10(np.max(np.abs(gap_audio)) + 1e-12)
    if not (-16.0 <= peak_db <= -15.0):
        return False, None
    return True, {
        'gap_s': round(gap, 3),
        'peak_db': round(peak_db, 1),
        'drop_at': round(last_drop[0], 2),
        'drop_ms': int(last_drop[2]*1000),
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    target = sys.argv[1]
    if os.path.isdir(target):
        paths = sorted(glob.glob(os.path.join(target, '*.wav')))
    else:
        paths = [target]
    n_broken = 0
    for p in paths:
        broken, info = detect_glitch(p)
        name = os.path.basename(p)
        if broken:
            n_broken += 1
            print(f"⚠️ {name}  {info}")
        else:
            print(f"✅ {name}")
    print(f"\n{n_broken}/{len(paths)} broken")
