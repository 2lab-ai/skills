#!/bin/bash
# Cohere Transcribe STT - Shell wrapper
# Usage: cohere-stt <audio_file> [--language ko] [--json]

VENV_PYTHON="/home/zhugehyuk/.cohere-stt-venv/bin/python"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INFERENCE_SCRIPT="${SCRIPT_DIR}/inference.py"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment not found at $VENV_PYTHON"
    echo "Run: python3 -m venv /home/zhugehyuk/.cohere-stt-venv"
    echo "Then: pip install 'transformers>=4.56,<5.3,!=5.0.*,!=5.1.*' torch huggingface_hub soundfile librosa sentencepiece protobuf"
    exit 1
fi

exec "$VENV_PYTHON" "$INFERENCE_SCRIPT" "$@"
