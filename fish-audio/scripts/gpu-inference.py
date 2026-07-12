#!/usr/bin/env python3
"""
Fish Speech S2 Pro — GPU-optimized inference wrapper.
Patches max_seq_len to fit in 16GB VRAM (RTX 4090 Laptop).
"""

import sys
import os

# Ensure fish-speech is in path
FISH_DIR = os.path.expanduser("~/fish-speech")
sys.path.insert(0, FISH_DIR)
os.chdir(FISH_DIR)

# Monkey-patch max_seq_len AFTER model loading, BEFORE setup_caches
import fish_speech.models.text2semantic.inference as infer_module

MAX_SEQ_LEN = 4096

_orig_init_model = infer_module.init_model

def _patched_init_model(*args, **kwargs):
    model, decode_one_token = _orig_init_model(*args, **kwargs)
    old_seq_len = model.config.max_seq_len
    model.config.max_seq_len = MAX_SEQ_LEN
    print(f"[gpu-inference] Patched max_seq_len: {old_seq_len} -> {model.config.max_seq_len}")
    return model, decode_one_token

infer_module.init_model = _patched_init_model

# Now run the normal inference main
from fish_speech.models.text2semantic.inference import main

if __name__ == "__main__":
    main()
