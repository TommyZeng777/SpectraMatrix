#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-run}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_EXECUTABLE="SpectralMatrixLauncher"

pkill -x "$APP_EXECUTABLE" >/dev/null 2>&1 || true
pkill -f "uvicorn spectral_core.api.app:create_app.*--port 8765" >/dev/null 2>&1 || true

case "$MODE" in
  run|--run)
    "$ROOT_DIR/script/build_macos_launcher.sh" run
    ;;
  build|--build)
    "$ROOT_DIR/script/build_macos_launcher.sh" build
    ;;
  verify|--verify)
    "$ROOT_DIR/script/build_macos_launcher.sh" verify
    ;;
  install|--install)
    "$ROOT_DIR/script/build_macos_launcher.sh" install
    ;;
  logs|--logs)
    "$ROOT_DIR/script/build_macos_launcher.sh" run
    /usr/bin/log stream --info --style compact --predicate "process == \"$APP_EXECUTABLE\""
    ;;
  *)
    echo "usage: $0 [run|build|verify|install|logs]" >&2
    exit 2
    ;;
esac
