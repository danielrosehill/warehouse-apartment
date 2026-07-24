# docs/figures/

Redacted images go here. Reference them from any doc as `figures/NAME.jpg` — that
path resolves both on GitHub (docs are in `docs/`) and in the PDF build
(`pdf/build.sh` adds `docs/` to the resource path).

**Only commit redacted images.** Originals with inventory QR codes must be run through
[`../../tools/redact_qr.py`](../../tools/redact_qr.py) first — the codes resolve to a
private host. See [`../../photos/`](../../photos/) for the workflow.
