# photos/

Photos of the system — sourcing, the storage wall, picking bins, moving equipment,
and moving day — organized by theme. **Redacted and metadata-stripped:** inventory
QR codes (which resolve to a private host) are covered, and EXIF/GPS is removed.

| Folder | What's in it |
|--------|--------------|
| [`sourcing/`](sourcing/) | The supplier yard; pallet deliveries |
| [`storage-system/`](storage-system/) | The storage wall, labelled Euroboxes, shelving, bin contents, consumables |
| [`picking-bins/`](picking-bins/) | Open-front picking bins and wall hardware bins |
| [`moving-equipment/`](moving-equipment/) | Hand trucks, dollies, carts, labelling tools |
| [`moving-day/`](moving-day/) | Palletized/strapped loads, car loads, the lift |
| [`extras/`](extras/) | Odds and ends |

These are the full-resolution WebP set. Downscaled JPEG copies of the ones embedded
inline in the manual live in [`../docs/figures/`](../docs/figures/).

## Adding new photos

1. Put originals in `photos/raw/` (git-ignored — never commit unredacted photos).
2. Run the redactor:
   ```bash
   python tools/redact_qr.py photos/raw photos/redacted
   ```
3. **Manually check** `photos/redacted/` — confirm every QR code is covered (the tool
   warns on images where it found none).
4. Strip metadata as a backstop: `exiftool -all= -overwrite_original -r photos/redacted`.
5. File the result into the theme folder above with a descriptive name; commit only
   redacted images. The redactor also strips EXIF (incl. GPS) on re-encode. See
   [`../tools/`](../tools/).
