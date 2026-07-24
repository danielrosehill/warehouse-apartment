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

Put redacted images in [`../docs/figures/`](../docs/figures/) and reference them from
the markdown as `figures/NAME.jpg`. That path renders on GitHub *and* in the PDF (the
build adds `docs/` to the resource path). Rebuild to pick up new images.

## Notes / limitations

- Cross-document links (`[Euroboxes](euroboxes.md)`) render as plain text in the PDF —
  they're for the web version.
- Layout/fonts are set in `metadata.<lang>.yml`.
