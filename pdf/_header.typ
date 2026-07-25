// Typst preamble injected into the PDF build (pandoc --include-in-header).
//
// Keep block code fences whole. The SOP chapters use fenced ASCII diagrams, and
// Typst's default is to break a raw block across pages — which cuts a diagram in
// half. All the diagrams here are well under a page, so refusing the break just
// pushes the whole figure to the next page.
#show raw.where(block: true): it => block(breakable: false, it)
