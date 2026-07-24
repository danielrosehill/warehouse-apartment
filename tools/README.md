# tools/

## `redact_qr.py` — batch QR-code redaction

Detects QR codes in photos and paints a **solid opaque box** over each one, so photos
of the storage system can be shared without leaking the inventory QR codes (which
resolve to a private host). Re-encoding also **strips EXIF** (including GPS).

### Why solid fill, not blur
QR codes use Reed–Solomon error correction — up to ~30% of a code can be missing and
still decode at the highest level. Small, blurry, or partly-hidden codes can still be
read, and light blur can sometimes be reversed. **Cover the whole code with opaque
fill.**

### Setup

```bash
# from the repo root (uv recommended)
uv venv .venv && source .venv/bin/activate
uv pip install -r tools/requirements.txt
```

### Usage

```bash
# redact every image in ./photos/raw into ./photos/redacted
python tools/redact_qr.py photos/raw photos/redacted

# just report what it finds, write nothing
python tools/redact_qr.py photos/raw photos/redacted --detect-only

# bigger safety margin around each code, recurse into subfolders
python tools/redact_qr.py photos/raw photos/redacted --pad 24 --recursive
```

Options: `--pad N`, `--color R,G,B`, `--recursive`, `--detect-only`, `--exts .jpg,.png,...`

### ⚠️ Always do a manual pass
Automatic detection is good but not perfect — very small, low-contrast, steeply
angled, or motion-blurred codes can be missed. The tool prints a **warning for any
image where it found nothing**. Eyeball the output folder before publishing and
hand-redact anything it missed.
