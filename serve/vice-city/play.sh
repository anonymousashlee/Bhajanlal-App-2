#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
PORT="${1:-8931}"
echo "VICE NEON serving on http://127.0.0.1:${PORT}/index.html"
python3 -m http.server "$PORT" --bind 127.0.0.1
