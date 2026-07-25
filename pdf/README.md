# pdf/ — finished documents

The polished, printable version of the manual, **generated from the markdown** in
`docs/` (markdown stays the single source of truth). One PDF per language.

- **English:** [`warehouse-apartment.en.pdf`](warehouse-apartment.en.pdf)
- **Hebrew:** planned (`warehouse-apartment.he.pdf`)

## Rebuild

```bash
pdf/build.sh          # English (default)
pdf/build.sh en
pdf/build.sh he       # once docs-he/ exists
```

Requires **pandoc ≥ 3** and **typst**. The build concatenates the docs (with page
breaks), adds a title page and table of contents, and typesets via the Typst engine.

## Images

Put redacted images (JPEG) in [`../docs/figures/`](../docs/figures/) and reference them
from the markdown as `figures/NAME.jpg`. That path renders on GitHub (doc-relative)
*and* in the PDF: a repo-root symlink `figures → docs/figures` (created by `build.sh`)
lets Typst resolve it. Use JPEG, not WebP — Typst embeds JPEG directly but re-encodes
WebP as a huge bitmap. Rebuild to pick up new images.

## Notes / limitations

- Cross-document links (`[Euroboxes](euroboxes.md)`) render as plain text in the PDF —
  they're for the web version.
- Layout/fonts are set in `metadata.<lang>.yml`.
- **ASCII diagrams need `_header.typ`.** The SOP chapters draw their diagrams as fenced
  code blocks (portable: they render on GitHub, on Pages, and in the PDF, unlike
  Mermaid, which none of the three would render here). Typst breaks a raw block across
  a page boundary by default, which cut the first diagram in half; the
  `--include-in-header=pdf/_header.typ` preamble sets `breakable: false` on block raw
  so a diagram moves whole to the next page. Box-drawing glyphs come from the
  `monofont` — DejaVu Sans Mono has them; not every mono font does.
- **`--file-scope` is load-bearing.** Every doc opens with a Jekyll front-matter block
  (`---` / `layout: default` / `---`). Pandoc concatenates inputs before parsing unless
  told otherwise, so only the *first* file's block was consumed as metadata and the
  other thirteen were parsed as setext headings — "layout: default" appeared as a
  chapter title in the TOC before each one. `--file-scope` (plus
  `+yaml_metadata_block` on the reader) parses each file separately and strips them
  all. Remove either flag and the front matter comes back.
