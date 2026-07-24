# photos/

Photos of the system (before/after the move, boxes, dollies, pallets, the storage
wall). **Coming** — the source shots contain inventory QR codes that resolve to a
private host and must be redacted first.

## Workflow

1. Put originals in `photos/raw/` (git-ignored — never commit unredacted photos).
2. Run the redactor:
   ```bash
   python tools/redact_qr.py photos/raw photos/redacted
   ```
3. **Manually check** `photos/redacted/` — confirm every QR code is covered (the tool
   warns on images where it found none).
4. Commit only from `photos/redacted/`.

The redactor also strips EXIF (including GPS) on re-encode. See [`../tools/`](../tools/).
