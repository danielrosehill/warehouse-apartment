#!/usr/bin/env python3
"""
redact_qr.py — batch-redact QR codes from photos.

Detects QR codes in every image in an input folder and paints a SOLID opaque box
over each one (not a blur — blur can be reversed, and QR error correction recovers
partly-obscured codes). Re-encodes output, which also strips EXIF metadata (e.g. GPS).

Why solid fill: QR codes use Reed-Solomon error correction (up to ~30% recoverable
at the highest level), so small/blurry/partly-hidden codes can still decode. Cover
the whole code.

Usage:
    python redact_qr.py INPUT_DIR OUTPUT_DIR [options]

Options:
    --pad N         Extra pixels around each detected code (default: 12)
    --color R,G,B   Fill colour (default: 0,0,0 = black)
    --recursive     Recurse into subfolders
    --detect-only   Report detections without writing files
    --exts .jpg,... Comma-separated extensions to process
                    (default: .jpg,.jpeg,.png,.webp,.bmp,.tif,.tiff)

Requires: opencv-python, numpy  (pip install -r requirements.txt)

LIMITATIONS — read this:
  Automatic detection is good but not perfect. Very small, low-contrast, heavily
  angled, or motion-blurred codes can be missed. This tool prints a WARNING for any
  image where it found nothing. ALWAYS eyeball the output folder before publishing,
  and redact any missed codes by hand.
"""
import argparse
import sys
from pathlib import Path

import numpy as np

try:
    import cv2
except ImportError:
    sys.exit("OpenCV not installed. Run: pip install -r requirements.txt")

DEFAULT_EXTS = ".jpg,.jpeg,.png,.webp,.bmp,.tif,.tiff"


def imread_unicode(path: Path):
    """cv2.imread that tolerates non-ASCII paths."""
    data = np.fromfile(str(path), dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def imwrite_unicode(path: Path, img) -> bool:
    ok, buf = cv2.imencode(path.suffix, img)
    if not ok:
        return False
    buf.tofile(str(path))
    return True


def detect_qr_polygons(img):
    """Return a list of (4,2) int polygons for every QR code found."""
    detector = cv2.QRCodeDetector()
    polygons = []
    # detectAndDecodeMulti finds multiple codes in one pass.
    try:
        ok, _decoded, points, _straight = detector.detectAndDecodeMulti(img)
        if ok and points is not None:
            for quad in points:
                polygons.append(np.asarray(quad).reshape(-1, 2))
    except cv2.error:
        pass
    # Fall back to single-code detect for anything the multi pass missed.
    if not polygons:
        try:
            ok, points = detector.detect(img)
            if ok and points is not None:
                for quad in points:
                    polygons.append(np.asarray(quad).reshape(-1, 2))
        except cv2.error:
            pass
    return polygons


def redact(img, polygons, pad, color):
    """Paint a solid, padded, axis-aligned box over each polygon."""
    h, w = img.shape[:2]
    for poly in polygons:
        xs, ys = poly[:, 0], poly[:, 1]
        x0 = max(0, int(xs.min()) - pad)
        y0 = max(0, int(ys.min()) - pad)
        x1 = min(w, int(xs.max()) + pad)
        y1 = min(h, int(ys.max()) + pad)
        cv2.rectangle(img, (x0, y0), (x1, y1), color, thickness=cv2.FILLED)
    return img


def iter_images(root: Path, exts, recursive: bool):
    globber = root.rglob("*") if recursive else root.glob("*")
    for p in sorted(globber):
        if p.is_file() and p.suffix.lower() in exts:
            yield p


def parse_color(s: str):
    try:
        r, g, b = (int(v) for v in s.split(","))
        return (b, g, r)  # OpenCV is BGR
    except Exception:
        raise argparse.ArgumentTypeError("--color must be R,G,B e.g. 0,0,0")


def main():
    ap = argparse.ArgumentParser(description="Batch-redact QR codes from photos.")
    ap.add_argument("input_dir", type=Path)
    ap.add_argument("output_dir", type=Path)
    ap.add_argument("--pad", type=int, default=12)
    ap.add_argument("--color", type=parse_color, default=(0, 0, 0))
    ap.add_argument("--recursive", action="store_true")
    ap.add_argument("--detect-only", action="store_true")
    ap.add_argument("--exts", default=DEFAULT_EXTS)
    args = ap.parse_args()

    if not args.input_dir.is_dir():
        sys.exit(f"Input dir not found: {args.input_dir}")
    exts = {e if e.startswith(".") else "." + e
            for e in (x.strip().lower() for x in args.exts.split(",")) if e}

    if not args.detect_only:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    total = redacted = codes = misses = 0
    for src in iter_images(args.input_dir, exts, args.recursive):
        total += 1
        img = imread_unicode(src)
        if img is None:
            print(f"  ! skip (unreadable): {src.name}")
            continue
        polys = detect_qr_polygons(img)
        if polys:
            codes += len(polys)
            print(f"  ✓ {src.name}: {len(polys)} QR code(s)")
        else:
            misses += 1
            print(f"  ! {src.name}: NO QR detected — check this one by hand")

        if args.detect_only:
            continue

        out = redact(img, polys, args.pad, args.color) if polys else img
        rel = src.relative_to(args.input_dir)
        dst = args.output_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if imwrite_unicode(dst, out):
            redacted += 1
        else:
            print(f"  ! failed to write: {dst}")

    print("\n--- summary ---")
    print(f"images scanned : {total}")
    print(f"QR codes found : {codes}")
    if not args.detect_only:
        print(f"files written  : {redacted}  (EXIF stripped on re-encode)")
    print(f"no-detection   : {misses}  <- review these manually")
    if misses:
        print("\nReminder: eyeball the output before publishing. Detection is not perfect.")


if __name__ == "__main__":
    main()
