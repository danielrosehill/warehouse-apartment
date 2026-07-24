#!/usr/bin/env python3
"""
redact_qr.py — batch-redact QR / barcodes from photos.

Finds codes in every image in an input folder and covers each one, so photos of
the storage system can be shared without leaking the inventory QR codes (which
resolve to a private host). Also auto-orients (EXIF) and strips metadata (incl. GPS).

Detection takes the UNION of up to three detectors (each misses different codes):
  * pyzbar (zbar)          — robust on angled / cluttered codes
  * OpenCV QRCodeDetector  — a second classical pass
  * WeChat QRCode (CNN+SR) — best on SMALL / blurry codes; needs opencv-contrib +
                             model files in tools/models/wechat/ (see download_models.sh)

Redaction modes:
  * fill  (default) — solid opaque box. Safest: QR error-correction (~30%) means
                      partial codes still decode, and blur can sometimes be reversed.
  * blur            — hard pixelation + heavy Gaussian with FEATHERED edges, so it's a
                      soft smudge rather than an ugly box. Strong enough to destroy the
                      code, but slightly less bulletproof than fill.

Usage:
    python redact_qr.py INPUT_DIR OUTPUT_DIR [options]

Options:
    --mode fill|blur   Redaction style (default: fill)
    --to same|webp     Output format (default: webp)
    --quality N        WebP quality 1-100 (default: 82)
    --pad N            Min padding px around each code (default: 10; also 15% of code size)
    --color R,G,B      Fill colour for --mode fill (default: 0,0,0)
    --recursive        Recurse into subfolders (structure preserved)
    --detect-only      Report detections, write nothing
    --exts .jpg,...    Extensions to process (default: common raster formats)

Requires: pyzbar, opencv-contrib-python, Pillow, numpy  (pip install -r requirements.txt)
System lib: libzbar0  (Debian/Ubuntu: sudo apt install libzbar0)

⚠️  Detection is good, not perfect. The tool prints a WARNING for any image where it
    found nothing — eyeball those before publishing, or run a cloud detector (see README).
"""
import argparse
import sys
from pathlib import Path

import numpy as np

try:
    import cv2
except ImportError:
    sys.exit("OpenCV not installed. Run: pip install -r requirements.txt")
try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow not installed. Run: pip install -r requirements.txt")

try:
    from pyzbar import pyzbar
    HAVE_ZBAR = True
except Exception:
    HAVE_ZBAR = False

DEFAULT_EXTS = ".jpg,.jpeg,.png,.webp,.bmp,.tif,.tiff"
MODELS = Path(__file__).parent / "models" / "wechat"


def load_qreader(model_size="l"):
    """YOLOv8 QR *region* detector — finds the QR surface even when it can't be decoded.
    This is the high-recall detector for redaction. Returns a detector or None."""
    try:
        from qreader import QReader
    except Exception:
        return None
    for ms in (model_size, "s", "n"):
        try:
            return QReader(model_size=ms, min_confidence=0.3)
        except Exception:
            continue
    return None


def load_wechat():
    """Optional CNN+super-resolution detector. Returns a detector or None."""
    files = [MODELS / f for f in
             ("detect.prototxt", "detect.caffemodel", "sr.prototxt", "sr.caffemodel")]
    if not all(f.exists() for f in files) or not hasattr(cv2, "wechat_qrcode_WeChatQRCode"):
        return None
    try:
        return cv2.wechat_qrcode_WeChatQRCode(*[str(f) for f in files])
    except Exception:
        return None


def load_oriented_rgb(path: Path):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)  # honour phone rotation
    img = img.convert("RGB")
    return img, np.asarray(img)


def detect_polys(rgb: np.ndarray, wechat=None, qreader=None):
    """Return a list of (N,2) float polygons for every code found (union of detectors)."""
    polys = []
    # QReader (YOLO): detects QR *regions* even when undecodable — highest recall.
    if qreader is not None:
        try:
            for det in qreader.detect(image=rgb):
                quad = det.get("quad_xy")
                if quad is not None and len(quad):
                    polys.append(np.asarray(quad, dtype=float).reshape(-1, 2))
                elif det.get("bbox_xyxy") is not None:
                    x1, y1, x2, y2 = (float(v) for v in det["bbox_xyxy"])
                    polys.append(np.array([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], dtype=float))
        except Exception:
            pass
    if HAVE_ZBAR:
        try:
            for sym in pyzbar.decode(rgb):
                if sym.polygon:
                    polys.append(np.array([(p.x, p.y) for p in sym.polygon], dtype=float))
                else:
                    r = sym.rect
                    polys.append(np.array(
                        [(r.left, r.top), (r.left + r.width, r.top),
                         (r.left + r.width, r.top + r.height), (r.left, r.top + r.height)],
                        dtype=float))
        except Exception:
            pass
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    det = cv2.QRCodeDetector()
    for fn in ("multi", "single"):
        try:
            if fn == "multi":
                ok, _s, pts, _ = det.detectAndDecodeMulti(bgr)
            else:
                ok, pts = det.detect(bgr)
            if ok and pts is not None:
                for quad in pts:
                    polys.append(np.asarray(quad).reshape(-1, 2).astype(float))
        except cv2.error:
            pass
    if wechat is not None:
        try:
            _res, points = wechat.detectAndDecode(bgr)
            for quad in (points or []):
                polys.append(np.asarray(quad).reshape(-1, 2).astype(float))
        except Exception:
            pass
    return polys


def detect_polys_tiled(rgb, wechat, qreader, tiles, overlap=0.25):
    """Detect on the full image AND on an NxN grid of overlapping tiles, so that
    tiny codes (small % of the frame) become large enough per-tile to be found."""
    polys = detect_polys(rgb, wechat, qreader)  # full-frame pass
    if tiles <= 1:
        return polys
    h, w = rgb.shape[:2]
    step_y, step_x = h / tiles, w / tiles
    ov_y, ov_x = int(step_y * overlap), int(step_x * overlap)
    for i in range(tiles):
        for j in range(tiles):
            y0 = max(0, int(i * step_y) - ov_y); y1 = min(h, int((i + 1) * step_y) + ov_y)
            x0 = max(0, int(j * step_x) - ov_x); x1 = min(w, int((j + 1) * step_x) + ov_x)
            tile = rgb[y0:y1, x0:x1]
            if tile.size == 0:
                continue
            for p in detect_polys(tile, wechat, qreader):
                polys.append(p + np.array([x0, y0], dtype=float))
    return polys


def padded_bbox(poly, pad_px, h, w):
    xs, ys = poly[:, 0], poly[:, 1]
    size = max(xs.max() - xs.min(), ys.max() - ys.min())
    pad = max(pad_px, 0.35 * size)  # generous halo so the redaction isn't tightly bounded
    x0 = max(0, int(xs.min() - pad)); y0 = max(0, int(ys.min() - pad))
    x1 = min(w, int(xs.max() + pad)); y1 = min(h, int(ys.max() + pad))
    return x0, y0, x1, y1


def _odd(n):
    n = int(n)
    return n + 1 if n % 2 == 0 else n


def redact(rgb: np.ndarray, polys, mode, pad_px, color):
    h, w = rgb.shape[:2]
    out = rgb.copy()
    for poly in polys:
        x0, y0, x1, y1 = padded_bbox(poly, pad_px, h, w)
        rw, rh = x1 - x0, y1 - y0
        if rw <= 1 or rh <= 1:
            continue
        if mode == "blur":
            region = out[y0:y1, x0:x1].astype(np.uint8)
            # 1) hard pixelation destroys the QR modules irreversibly
            sw, sh = max(1, rw // 12), max(1, rh // 12)
            pix = cv2.resize(cv2.resize(region, (sw, sh), interpolation=cv2.INTER_LINEAR),
                             (rw, rh), interpolation=cv2.INTER_NEAREST)
            # 2) heavy Gaussian smooths the pixels into a soft smudge
            k = _odd(max(31, max(rw, rh) // 2))
            smudge = cv2.GaussianBlur(pix, (k, k), 0)
            # 3) feathered mask -> no hard rectangle edge
            feather = _odd(max(11, max(rw, rh) // 5))
            inset = feather
            mask = np.zeros((rh, rw), np.float32)
            cv2.rectangle(mask, (inset, inset), (rw - inset, rh - inset), 1.0, -1)
            mask = cv2.GaussianBlur(mask, (feather, feather), 0)[..., None]
            out[y0:y1, x0:x1] = (smudge * mask + region * (1 - mask)).astype(np.uint8)
        else:  # fill
            out[y0:y1, x0:x1] = color
    return out


def iter_images(root: Path, exts, recursive: bool):
    globber = root.rglob("*") if recursive else root.glob("*")
    for p in sorted(globber):
        if p.is_file() and p.suffix.lower() in exts:
            yield p


def parse_color(s: str):
    try:
        r, g, b = (int(v) for v in s.split(","))
        return (r, g, b)
    except Exception:
        raise argparse.ArgumentTypeError("--color must be R,G,B e.g. 0,0,0")


def main():
    ap = argparse.ArgumentParser(description="Batch-redact QR/barcodes from photos.")
    ap.add_argument("input_dir", type=Path)
    ap.add_argument("output_dir", type=Path)
    ap.add_argument("--mode", choices=["fill", "blur"], default="fill")
    ap.add_argument("--to", choices=["same", "webp"], default="webp")
    ap.add_argument("--quality", type=int, default=82)
    ap.add_argument("--pad", type=int, default=24)
    ap.add_argument("--tiles", type=int, default=1,
                    help="NxN sliced detection for tiny codes (e.g. 4). 1 = full frame only.")
    ap.add_argument("--qr-model", default="l", choices=["n", "s", "m", "l"],
                    help="QReader YOLO model size (default l). Smaller = faster, less recall.")
    ap.add_argument("--color", type=parse_color, default=(0, 0, 0))
    ap.add_argument("--recursive", action="store_true")
    ap.add_argument("--detect-only", action="store_true")
    ap.add_argument("--exts", default=DEFAULT_EXTS)
    args = ap.parse_args()

    if not args.input_dir.is_dir():
        sys.exit(f"Input dir not found: {args.input_dir}")
    qreader = load_qreader(args.qr_model)
    wechat = load_wechat()
    detectors = ((["qreader(YOLO)"] if qreader else []) + (["zbar"] if HAVE_ZBAR else [])
                 + ["opencv"] + (["wechat"] if wechat else []))
    print(f"detectors: {' + '.join(detectors)}\n")
    exts = {e if e.startswith(".") else "." + e
            for e in (x.strip().lower() for x in args.exts.split(",")) if e}
    if not args.detect_only:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    total = written = codes = misses = 0
    for src in iter_images(args.input_dir, exts, args.recursive):
        total += 1
        try:
            _pil, rgb = load_oriented_rgb(src)
        except Exception as e:
            print(f"  ! skip (unreadable): {src.name} ({e})")
            continue
        polys = detect_polys_tiled(rgb, wechat, qreader, args.tiles)
        if polys:
            codes += len(polys)
            print(f"  ✓ {src.name}: {len(polys)} code region(s)")
        else:
            misses += 1
            print(f"  ! {src.name}: NO code detected — check by hand")

        if args.detect_only:
            continue

        out_rgb = redact(rgb, polys, args.mode, args.pad, args.color) if polys else rgb
        rel = src.relative_to(args.input_dir)
        if args.to == "webp":
            rel = rel.with_suffix(".webp")
        dst = args.output_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        out_img = Image.fromarray(out_rgb)  # no exif -> metadata stripped
        if args.to == "webp":
            out_img.save(dst, "WEBP", quality=args.quality, method=6)
        else:
            out_img.save(dst)
        written += 1

    print("\n--- summary ---")
    print(f"detectors      : {' + '.join(detectors)}")
    print(f"images scanned : {total}")
    print(f"code regions   : {codes}")
    if not args.detect_only:
        print(f"files written  : {written}  (mode={args.mode}, format={args.to}, EXIF stripped)")
    print(f"no-detection   : {misses}  <- review these by hand (or run a cloud detector)")


if __name__ == "__main__":
    main()
