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

## Composites

`composite-*.jpg` are **generated, not hand-made** — multi-photo strips and grids used
as the hero and section images on the README. Don't edit them; edit the source list in
[`../../tools/make_composites.sh`](../../tools/make_composites.sh) and re-run it:

```bash
tools/make_composites.sh
```

Tiles are centre-cropped to a common aspect, so **pick sources of matching
orientation** for a given composite — most of the library is portrait, and cropping a
tall crate column into a 4:3 tile throws the subject away. Two other things learned
the hard way: avoid sources whose redaction block dominates the frame (it becomes the
tile at thumbnail size), and keep the gutter a dark neutral — a white gutter looks
broken against GitHub's dark theme.

## Not everything here is a photo of our system

Most figures are display copies of our own redacted photos. A few are not, and they
are captioned as such in the docs:

| Figure | What it is |
|--------|-----------|
| `acl-nested-and-closed.jpg` | Catalogue-style product shot of attached-lid containers, nested and closed — used because the nesting behaviour is the whole point and our own ACL has never been photographed that way |
| `alc-6441-model.jpg` | Render of our own GLB from [Modular-Storage-3D-Models](https://github.com/danielrosehill/Modular-Storage-3D-Models) |
| `composite-*.jpg` | Generated — see above |

Anything sourced from outside needs its redistribution rights checked before it lands
here; the docs and photos in this repo are published CC BY 4.0.

**Only commit redacted images** — originals with inventory QR codes must be run
through [`../../tools/redact_qr.py`](../../tools/redact_qr.py) first (the codes resolve
to a private host). See [`../../photos/`](../../photos/) for the workflow.
