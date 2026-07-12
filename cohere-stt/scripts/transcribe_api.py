#!/usr/bin/env python3
"""
Cohere Transcribe API Server
Provides HTTP endpoint compatible with OpenAI Whisper API format.
For soma integration - drop-in replacement for OpenAI transcription.

Usage: python transcribe_api.py [--port 8787] [--device auto]
"""

import argparse
import json
import os
import sys
import tempfile
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import cgi

# Global model reference
_model = None
_processor = None
_device = None


def get_model():
    global _model, _processor, _device
    if _model is None:
        from inference import load_model
        _model, _processor, _device = load_model(device="auto", compile=False)
    return _model, _processor, _device


class TranscribeHandler(BaseHTTPRequestHandler):
    """HTTP handler compatible with OpenAI audio transcription API."""

    def do_POST(self):
        if self.path == "/v1/audio/transcriptions":
            self._handle_transcription()
        elif self.path == "/health":
            self._respond_json(200, {"status": "ok"})
        else:
            self._respond_json(404, {"error": "Not found"})

    def do_GET(self):
        if self.path == "/health":
            self._respond_json(200, {"status": "ok", "model": "cohere-transcribe-03-2026"})
        else:
            self._respond_json(404, {"error": "Not found"})

    def _handle_transcription(self):
        try:
            content_type = self.headers.get("Content-Type", "")
            if "multipart/form-data" not in content_type:
                self._respond_json(400, {"error": "Expected multipart/form-data"})
                return

            # Parse multipart form data
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    "REQUEST_METHOD": "POST",
                    "CONTENT_TYPE": content_type,
                },
            )

            # Get language (default: ko)
            language = "ko"
            if "language" in form:
                language = form["language"].value

            # Get audio file
            if "file" not in form:
                self._respond_json(400, {"error": "Missing 'file' field"})
                return

            file_item = form["file"]
            audio_data = file_item.file.read()

            # Save to temp file
            suffix = ".ogg"
            if file_item.filename:
                _, ext = os.path.splitext(file_item.filename)
                if ext:
                    suffix = ext

            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name

            try:
                model, processor, device = get_model()

                t0 = time.time()
                from inference import transcribe_single
                text = transcribe_single(
                    model, processor, tmp_path,
                    language=language,
                )
                elapsed = time.time() - t0

                # OpenAI-compatible response format
                response = {
                    "text": text,
                    "task": "transcribe",
                    "language": language,
                    "duration": elapsed,
                }
                self._respond_json(200, response)

            finally:
                os.unlink(tmp_path)

        except Exception as e:
            print(f"[ERROR] Transcription failed: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            self._respond_json(500, {"error": str(e)})

    def _respond_json(self, status: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        """Custom log format."""
        sys.stderr.write(
            f"[cohere-stt-api] {self.client_address[0]} - {format % args}\n"
        )


def main():
    parser = argparse.ArgumentParser(description="Cohere Transcribe API Server")
    parser.add_argument("--port", "-p", type=int, default=8787)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--device", "-d", default="auto")
    parser.add_argument(
        "--preload", action="store_true",
        help="Preload model at startup (otherwise lazy-loaded on first request)"
    )
    args = parser.parse_args()

    if args.preload:
        print("[cohere-stt-api] Preloading model...", file=sys.stderr)
        get_model()
        print("[cohere-stt-api] Model ready", file=sys.stderr)

    server = HTTPServer((args.host, args.port), TranscribeHandler)
    print(
        f"[cohere-stt-api] Listening on http://{args.host}:{args.port}",
        file=sys.stderr,
    )
    print(
        f"[cohere-stt-api] POST /v1/audio/transcriptions (OpenAI-compatible)",
        file=sys.stderr,
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[cohere-stt-api] Shutting down...", file=sys.stderr)
        server.server_close()


if __name__ == "__main__":
    main()
