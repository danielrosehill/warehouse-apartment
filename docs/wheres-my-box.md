# Where's My Box

The information layer over the physical system: knowing **what's in each box and
where each box is**, without opening anything.

## What it is

- A **home inventory system** — a **substantial fork of [Homebox](https://github.com/hay-kot/homebox)** — with **QR-code labels** on every box.
- Scan a box's QR → see its contents. Search an item → find its box and location.
- **Not yet publicly released.** The fork is substantial; release TBD.

## Why it's essential to the rest

Renting means you can't predict your next apartment's storage or closet layout — you
often reorganize from scratch every move. A lookup system decouples *what you own*
from *where it currently lives*, so a reshuffle is a data update, not a memory test.
It also records **where everything was**, which matters when you're reconstructing a
setup after a move.

## Current state: the manual-reset cost

This move is the system at its hardest point. Old boxes were discarded and everything
was repacked into Euroboxes, so every box has to be **manually re-checked-in**. Once
past this reset, the check-in/check-out flow (the UI is the strong part of the fork)
makes maintenance quick.

## ⚠️ QR codes and photo privacy

The QR labels resolve to a **private inventory host**. That has a direct consequence
for sharing photos of the system:

- **Assume any QR in a photo is readable.** QR codes carry Reed–Solomon error
  correction (up to ~30% recoverable at the highest level), so small, blurry, or
  partly-obscured codes can still decode. "Barely visible" is **not** safe. Even
  light blur can sometimes be reversed.
- **Redact with solid opaque fill**, not blur, over the whole code.
- A batch redaction tool for exactly this is in [`../tools/`](../tools/) — it detects
  QR codes and paints solid boxes over them (and strips EXIF, which can leak GPS
  location).

## Related

- [Euroboxes](euroboxes.md) · [`../tools/`](../tools/) · [`../photos/`](../photos/)
