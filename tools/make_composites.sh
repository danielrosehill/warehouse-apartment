#!/usr/bin/env bash
#
# Build the composite (multi-photo) figures used in README.md and the docs.
#
#   tools/make_composites.sh
#
# Sources are the redacted WebP originals in photos/; outputs are JPEGs in
# docs/figures/composite-*.jpg — JPEG because the PDF build embeds JPEG directly
# but re-encodes WebP as a huge bitmap (see docs/figures/README.md).
#
# Every tile is centre-cropped to a common aspect ratio so portrait and landscape
# phone shots tile without letterboxing. The gutter colour is a dark neutral that
# reads acceptably against both GitHub light and dark themes.
#
# Requires: ImageMagick 7 (`magick`).
set -euo pipefail
cd "$(dirname "$0")/.."   # repo root

command -v magick >/dev/null || { echo "error: ImageMagick 7 ('magick') not found" >&2; exit 1; }

GUTTER='#15181c'
PAD=6
OUT_DIR=docs/figures
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# composite <out-name> <cols> <tile-w> <tile-h> <src...>
composite() {
  local name=$1 cols=$2 tw=$3 th=$4; shift 4
  local tiles=() i=0 src
  for src in "$@"; do
    [ -f "$src" ] || { echo "error: missing source '$src'" >&2; exit 1; }
    local tile="$TMP/$(printf '%02d' "$i").jpg"
    # -resize ^ then -gravity center -extent = fill-and-centre-crop.
    magick "$src" -auto-orient -resize "${tw}x${th}^" \
      -gravity center -extent "${tw}x${th}" -strip -quality 86 "$tile"
    tiles+=("$tile"); i=$((i+1))
  done
  montage "${tiles[@]}" -tile "${cols}x" -geometry "${tw}x${th}+${PAD}+${PAD}" \
    -background "$GUTTER" -strip -quality 86 "$OUT_DIR/${name}.jpg"
  echo "  $OUT_DIR/${name}.jpg  ($(identify -format '%wx%h' "$OUT_DIR/${name}.jpg"), $(du -h "$OUT_DIR/${name}.jpg" | cut -f1))"
}

echo "Building composites…"

# Most of the library is portrait (phone shots of tall crate columns), so strips
# built from those use 3:4 tiles; grids built from the landscape shots use 4:3.

# Hero banner — the whole arc in one strip: source → shelve → pick → carry → drive.
composite composite-hero 5 345 460 \
  photos/sourcing/supplier-yard-crate-stacks-02.webp \
  photos/storage-system/euro-crate-stack-hallway.webp \
  photos/picking-bins/picking-bins-shelf-column.webp \
  photos/moving-day/strapped-crate-dolly-garage.webp \
  photos/moving-day/car-trunk-four-bins.webp

# The storage system as it lives in the flat.
composite composite-storage-system 3 520 390 \
  photos/storage-system/euro-crate-stack-window.webp \
  photos/storage-system/euro-crate-s623-handheld.webp \
  photos/storage-system/euro-crate-stack-labeled.webp \
  photos/storage-system/storage-wall-white-tubs.webp \
  photos/storage-system/consumables-paper-rolls-01.webp \
  photos/storage-system/bin-contents-cables.webp

# Industrial shelving: supplier stock → flat-pack → assembly → loaded.
composite composite-shelving 4 375 500 \
  photos/sourcing/shelving-supplier-racking.webp \
  photos/sourcing/shelving-components-pallets.webp \
  photos/storage-system/shelving-boltless-assembly.webp \
  photos/storage-system/shelving-crate-on-beam.webp

# Moving day.
composite composite-moving-day 4 375 500 \
  photos/moving-day/crate-stack-hand-truck-indoor.webp \
  photos/moving-day/strapped-crate-dolly-garage.webp \
  photos/moving-day/elevator-crate-column.webp \
  photos/moving-day/car-trunk-strapped-stack-garage.webp

# Picking and sorting bins.
composite composite-picking-bins 3 520 390 \
  photos/picking-bins/picking-bin-s625-handheld.webp \
  photos/picking-bins/wall-tilt-bins-screws.webp \
  photos/picking-bins/wall-tilt-bins-over-bookshelf.webp

# Sourcing: the supplier yard and what arrives at the kerb.
composite composite-sourcing 3 520 390 \
  photos/sourcing/supplier-yard-crate-stacks-01.webp \
  photos/sourcing/supplier-yard-crate-stacks-03.webp \
  photos/sourcing/supplier-yard-selfie-02.webp

echo "Done."
