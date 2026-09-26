#!/usr/bin/env bash
# One-time setup per fresh machine/session: Python deps, offline voice model, fonts.
set -e
C="${RAW_AVENUE_CACHE:-$HOME/.cache/rawavenue}"
mkdir -p "$C/fonts"
pip install --break-system-packages -q kokoro-onnx soundfile pillow numpy
[ -s "$C/kokoro.onnx" ] || curl -sSL -o "$C/kokoro.onnx" https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -s "$C/voices.bin" ] || curl -sSL -o "$C/voices.bin" https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
G=https://raw.githubusercontent.com/google/fonts/main
[ -s "$C/fonts/PermanentMarker-Regular.ttf" ] || curl -sSL -o "$C/fonts/PermanentMarker-Regular.ttf" $G/apache/permanentmarker/PermanentMarker-Regular.ttf
[ -s "$C/fonts/PatrickHand-Regular.ttf" ] || curl -sSL -o "$C/fonts/PatrickHand-Regular.ttf" $G/ofl/patrickhand/PatrickHand-Regular.ttf
[ -s "$C/fonts/ArchivoBlack-Regular.ttf" ] || curl -sSL -o "$C/fonts/ArchivoBlack-Regular.ttf" $G/ofl/archivoblack/ArchivoBlack-Regular.ttf
command -v ffmpeg >/dev/null || { echo "ffmpeg missing"; exit 1; }
echo "setup ok"
