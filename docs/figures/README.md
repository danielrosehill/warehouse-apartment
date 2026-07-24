# docs/figures/

Downscaled **JPEG** display copies of the photos embedded inline in the manual
(source WebP originals live in [`../../photos/`](../../photos/)). Reference them from
any doc as `figures/NAME.jpg`.

That reference resolves in three places:

- **On GitHub** — relative to the doc in `docs/`, so `figures/NAME.jpg` → `docs/figures/NAME.jpg`.
- **In the PDF build** — a repo-root symlink `figures → docs/figures` lets Typst
  (whose project root is the repo root) resolve the same path. See [`../../pdf/build.sh`](../../pdf/build.sh).

**Why JPEG, not WebP:** Typst re-encodes WebP as an uncompressed bitmap (a single
12 MP photo bloated the PDF to ~20 MB), but embeds JPEG directly. JPEG keeps the PDF
small. Generate a display copy with:

```bash
magick photos/<folder>/<name>.webp -resize '1400x1400>' -quality 82 -strip docs/figures/<name>.jpg
```

**Only commit redacted images** — originals with inventory QR codes must be run
through [`../../tools/redact_qr.py`](../../tools/redact_qr.py) first (the codes resolve
to a private host). See [`../../photos/`](../../photos/) for the workflow.
