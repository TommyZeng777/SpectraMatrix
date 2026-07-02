#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-build}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE_DIR="$ROOT_DIR/launcher/SpectralMatrixLauncher"
BUILD_DIR="$ROOT_DIR/.build/spectral-matrix-launcher"
DIST_DIR="$ROOT_DIR/dist"
APP_EXECUTABLE="SpectralMatrixLauncher"
APP_DISPLAY_NAME="光谱训练矩阵启动台"
BUNDLE_ID="cn.local.spectral-matrix.launcher"
MIN_SYSTEM_VERSION="13.0"
APP_BUNDLE="$DIST_DIR/$APP_DISPLAY_NAME.app"
INSTALL_DIR="${SPECTRAL_LAUNCHER_INSTALL_DIR:-/Applications}"
INSTALLED_APP="$INSTALL_DIR/$APP_DISPLAY_NAME.app"
APP_CONTENTS="$APP_BUNDLE/Contents"
APP_MACOS="$APP_CONTENTS/MacOS"
APP_RESOURCES="$APP_CONTENTS/Resources"
INFO_PLIST="$APP_CONTENTS/Info.plist"
ICON_FILE="$ROOT_DIR/launcher/assets/AppIcon.icns"
LOGO_FILE="$ROOT_DIR/launcher/assets/AppIcon-80.png"

export CLANG_MODULE_CACHE_PATH="$ROOT_DIR/.build/module-cache"

mkdir -p "$DIST_DIR" "$BUILD_DIR" "$CLANG_MODULE_CACHE_PATH"

swift build --package-path "$PACKAGE_DIR" --scratch-path "$BUILD_DIR" -c release
BUILD_BIN_DIR="$(swift build --package-path "$PACKAGE_DIR" --scratch-path "$BUILD_DIR" -c release --show-bin-path)"
BUILD_BINARY="$BUILD_BIN_DIR/$APP_EXECUTABLE"

rm -rf "$APP_BUNDLE"
mkdir -p "$APP_MACOS" "$APP_RESOURCES"
cp "$BUILD_BINARY" "$APP_MACOS/$APP_EXECUTABLE"
chmod +x "$APP_MACOS/$APP_EXECUTABLE"
printf '%s\n' "$ROOT_DIR" > "$APP_RESOURCES/project-root.txt"
if [[ -f "$ICON_FILE" ]]; then
  cp "$ICON_FILE" "$APP_RESOURCES/AppIcon.icns"
fi
if [[ -f "$LOGO_FILE" ]]; then
  cp "$LOGO_FILE" "$APP_RESOURCES/AppIcon-80.png"
fi

cat > "$INFO_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>$APP_EXECUTABLE</string>
  <key>CFBundleIdentifier</key>
  <string>$BUNDLE_ID</string>
  <key>CFBundleName</key>
  <string>$APP_DISPLAY_NAME</string>
  <key>CFBundleDisplayName</key>
  <string>$APP_DISPLAY_NAME</string>
  <key>CFBundleIconFile</key>
  <string>AppIcon</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>0.1.0</string>
  <key>CFBundleVersion</key>
  <string>1</string>
  <key>LSMinimumSystemVersion</key>
  <string>$MIN_SYSTEM_VERSION</string>
  <key>NSPrincipalClass</key>
  <string>NSApplication</string>
</dict>
</plist>
PLIST

case "$MODE" in
  build)
    echo "$APP_BUNDLE"
    ;;
  run|--run)
    /usr/bin/open -n "$APP_BUNDLE"
    ;;
  verify|--verify)
    /usr/bin/open -n "$APP_BUNDLE"
    for _ in {1..20}; do
      if pgrep -x "$APP_EXECUTABLE" >/dev/null && curl -fsS "http://127.0.0.1:8765/health" >/dev/null; then
        echo "$APP_BUNDLE"
        echo "health: ok"
        exit 0
      fi
      sleep 0.5
    done
    echo "launcher did not reach http://127.0.0.1:8765/health" >&2
    echo "check log: $ROOT_DIR/logs/launcher_backend.log" >&2
    exit 1
    ;;
  install|--install)
    mkdir -p "$INSTALL_DIR"
    /usr/bin/ditto "$APP_BUNDLE" "$INSTALLED_APP"
    echo "$INSTALLED_APP"
    ;;
  *)
    echo "usage: $0 [build|run|verify|install]" >&2
    exit 2
    ;;
esac
