#!/usr/bin/env bash
# Download the WeChat QRCode model files (CNN detector + super-resolution) used for
# high-recall QR detection on small/blurry codes. ~1 MB total. Not committed to git.
set -euo pipefail
cd "$(dirname "$0")"
DEST="models/wechat"
mkdir -p "$DEST"
BASE="https://raw.githubusercontent.com/WeChatCV/opencv_3rdparty/wechat_qrcode"
for f in detect.prototxt detect.caffemodel sr.prototxt sr.caffemodel; do
  if [ -s "$DEST/$f" ]; then
    echo "have $f"
  else
    echo "fetching $f"
    curl -fsSL "$BASE/$f" -o "$DEST/$f"
  fi
done
echo "WeChat models ready in $DEST"
