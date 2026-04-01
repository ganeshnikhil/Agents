Blueprint regeneration

This folder contains the source blueprint PDF and exported diagram images.

Files

- `docs/blueprint/twin.pdf` — original blueprint PDF (source of truth)
- `docs/blueprint/images/` — exported images (one file per page)

Recommended tools (macOS):

- `pdftoppm` (from `poppler`) — reliable page-to-image exporter
- `magick` (ImageMagick) — flexible, supports density and page ranges

Install (Homebrew):

```bash
brew install poppler imagemagick
```

Basic full-export commands

Using `pdftoppm` (png pages):

```bash
mkdir -p docs/blueprint/images
pdftoppm -png docs/blueprint/twin.pdf docs/blueprint/images/page
# produces page-1.png, page-2.png, ...
```

Using ImageMagick (preserve high resolution, zero-based page index naming):

```bash
mkdir -p docs/blueprint/images
magick -density 300 docs/blueprint/twin.pdf docs/blueprint/images/page-%03d.png
# produces page-000.png, page-001.png, ...
```

Export only selected pages

To export a small set of pages (example: pages 1-5):

```bash
# pdftoppm uses 1-based page numbers
pdftoppm -f 1 -l 5 -png docs/blueprint/twin.pdf docs/blueprint/images/page

# ImageMagick (zero-based page indexes, so 0-4 is pages 1-5)
magick -density 300 docs/blueprint/twin.pdf[0-4] docs/blueprint/images/page-%03d.png
```

Which pages to keep as "essential"

From the exported images, the project references these essential diagrams (keep these for the README):

- Component diagram — `docs/blueprint/images/page-000.png`
- Flow diagram — `docs/blueprint/images/page-001.png`
- Dataflow / Memory lifecycle — `docs/blueprint/images/page-002.png`
- Deployment overview — `docs/blueprint/images/page-003.png`
- Memory schema — `docs/blueprint/images/page-004.png`

Notes

- Filenames may differ depending on the tool and options; adapt commands above to match your preferred naming scheme.
- Use `-density 300` (or 150–300) with ImageMagick for readable diagrams.
- If you need embedded images only (not page renders), `pdfimages` (poppler) can extract embedded raster images.

If you'd like, I can (1) run the commands here to regenerate images with a consistent naming scheme, or (2) prune the `README.md` image list to reference only these five essential images. Which should I do next?