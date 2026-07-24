#!/usr/bin/env bash
#
# Build the finished PDF(s) from the markdown docs, via pandoc + the Typst engine.
# Markdown stays the single source of truth; this just typesets it (with images).
#
# Usage:
#   pdf/build.sh          # build English (default)
#   pdf/build.sh en
#   pdf/build.sh he       # Hebrew (once docs-he/ exists)
#
# Requires: pandoc >= 3.x, typst.  Images live in docs/figures/ (JPEG) and are
# referenced from the markdown as figures/NAME.jpg — which renders on GitHub
# (doc-relative) and in the PDF: a repo-root symlink `figures -> docs/figures` lets
# Typst (project root = repo root) resolve the same path. Recreated below if missing.
set -euo pipefail
cd "$(dirname "$0")/.."   # repo root

LANG_CODE="${1:-en}"
OUT="pdf/warehouse-apartment.${LANG_CODE}.pdf"
BUILD_DATE="$(date +%Y-%m-%d)"
PB="pdf/_pagebreak.md"

for bin in pandoc typst; do
  command -v "$bin" >/dev/null || { echo "error: '$bin' not found on PATH" >&2; exit 1; }
done

# Ensure the figures symlink Typst needs to resolve figures/NAME.jpg from the repo root.
[ -e figures ] || ln -s docs/figures figures

case "$LANG_CODE" in
  en)
    META="pdf/metadata.en.yml"
    DOCS=(
      docs/the-why.md
      docs/euroboxes.md
      docs/cost-of-ownership.md
      docs/picking-and-sorting-bins.md
      docs/moving-equipment.md
      docs/pallets-elevators-biomechanics.md
      docs/gastronorm.md
      docs/consumables-and-inserts.md
      docs/sourcing.md
      docs/interoperability.md
      docs/shipping-container-thesis.md
      docs/wheres-my-box.md
    )
    ;;
  he)
    META="pdf/metadata.he.yml"
    shopt -s nullglob
    DOCS=( docs-he/*.md )
    shopt -u nullglob
    [ "${#DOCS[@]}" -gt 0 ] || { echo "error: no docs-he/*.md yet — Hebrew edition not written" >&2; exit 1; }
    ;;
  *)
    echo "error: unknown language '$LANG_CODE' (use en|he)" >&2; exit 1;;
esac

# Interleave a page break between documents.
INPUTS=()
for i in "${!DOCS[@]}"; do
  (( i > 0 )) && INPUTS+=("$PB")
  INPUTS+=("${DOCS[$i]}")
done

pandoc \
  --metadata-file="$META" \
  -M date="$BUILD_DATE" \
  --from=gfm+raw_attribute \
  --pdf-engine=typst \
  --resource-path=.:docs \
  --toc --toc-depth=2 \
  "${INPUTS[@]}" \
  -o "$OUT"

echo "Wrote $OUT ($(du -h "$OUT" | cut -f1))"
