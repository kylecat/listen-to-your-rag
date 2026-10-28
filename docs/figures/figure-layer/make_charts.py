"""Pipeline flowcharts for the figure-layer pilot (HTML → PNG via headless Chromium)."""
import subprocess
from pathlib import Path
from PIL import Image, ImageChops

OUT = Path(__file__).resolve().parent
CSS = """body{font-family:"Noto Sans","DejaVu Sans",sans-serif;background:#fff;margin:22px;color:#1f2933;width:860px}
h1{font-size:24px;margin:0 0 4px}h2{font-size:20px;margin:22px 0 8px}.sub{color:#52606d;margin-bottom:16px;font-size:14px}
.step{background:#fff;border-radius:10px;padding:9px 14px;border:1.5px solid #cbd2d9;font-size:15px;line-height:1.45}
.step b{font-size:16px}.tag b{font-size:inherit}.tag{font-size:13px;color:#616e7c}.bad{color:#b42318}
.arrow{text-align:center;font-size:21px;color:#7b8794;line-height:24px}
.same{background:#f5f7fa;border:1.5px dashed #9aa5b1}.new{background:#eef6ff;border-color:#8fb8ea}
.gpu{background:#f3eefe;border-color:#b69ce8}.ai{background:#fff8e1;border-color:#f0c36d}
.out{background:#e8f5ec;border-color:#7cc08f}.side{background:#fdf2f2;border-color:#e3a6a6}
.split{display:flex;gap:12px;align-items:flex-start}.split>div{flex:1}
.legend{margin-top:14px;font-size:13px;color:#52606d}.legend span{display:inline-block;padding:2px 8px;border-radius:6px;margin-right:6px;border:1px solid #cbd2d9}
.note{margin-top:12px;font-size:13.5px;line-height:1.5;background:#fafafa;border-left:4px solid #9aa5b1;padding:8px 12px}"""
A = '<div class="arrow">↓</div>'


def s(t, d="", c=""):
    return f'<div class="step {c}"><b>{t}</b>' + (f"<br><span class='tag'>{d}</span>" if d else "") + "</div>"


def split(*cols):
    return '<div class="split">' + "".join("<div>" + A.join(c) + "</div>" for c in cols) + "</div>"


def page(title, sub, body, note):
    legend = ('<div class="legend">Legend: <span class="same">same as v2</span><span class="new">rule-based step</span>'
              '<span class="gpu">learned model (Docling)</span><span class="ai">LLM (Claude)</span>'
              '<span class="side">not in the vector index</span><span class="out">index produced</span></div>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><h1>{title}</h1>'
            f"<div class='sub'>{sub}</div>{body}{legend}<div class='note'>{note}</div></body></html>")


C = {
"flow-v1": page("v1 (original index)", "Page-by-page text extraction; fixed-size chunks",
    A.join([s("1. PDF"), s("2. Page-by-page text extraction", "<span class='bad'>two-column lines interleaved</span>", "new"),
            s("3. Concatenate all text", "<span class='bad'>headers, footers, metadata, captions and table fragments kept</span>", "new"),
            s("4. Section detection (whole-line match only)", "<span class='bad'>62% of chunks unlabeled</span>", "new"),
            s("5. Fixed 500-word chunks (80 overlap)", "<span class='bad'>often split mid-sentence</span>", "new"),
            s("6. Embedding", "nomic-embed-text, 768-d"), s("v1 index", "11,258 chunks / 464 papers", "out")]),
    "Figure information is present only as fragmentary caption and table text mixed into body chunks."),
"flow-v2": page("v2 (rule-based extraction, production since 2026-10-27)", "Shared extraction module for the index and the read-aloud tool",
    A.join([s("1. PDF"), s("2. Coordinate-aware text extraction + column reordering", "", "new"),
            s("3. Noise removal", "headers, footers, page numbers, journal metadata, sidebars", "new"),
            s("4. Section detection", "abstract / introduction / methods / results / discussion / conclusion", "new"),
            s("5. Filtering", "<span class='bad'>captions (Fig./Table …) and table fragments dropped; nothing after References</span>", "new"),
            s("6. Sentence-aligned chunks", "≈500 words, 80-word overlap, section label per chunk", "new"),
            s("7. Embedding", "nomic-embed-text, 768-d, cosine"), s("v2 index", "9,601 chunks / 453 papers", "out")]),
    "Limitation: no figures, captions or tables — figure-only answers are almost never retrieved (AnsHit@10 = 0.09)."),
"flow-v3": page("v3 (Docling, figure features off)", "Comparison arm: only the text source differs from v2",
    A.join([s("1. PDF"), s("2. Docling layout analysis (GPU)", "OCR off, table structure off, picture models off; one paper per process", "gpu"),
            s("3. Markdown → plain text", "image placeholders and table rows removed", "new"),
            s("4. v2 sectioning and chunking", "<span class='bad'>captions dropped as in v2</span>", "same"),
            s("5. Embedding", "same model as v2", "same"), s("v3 index", "8,990 chunks / 453 papers", "out")]),
    "Ties with v2 on known-item retrieval (MRR@10 0.897 vs 0.893); like v2, it cannot return figure-only answers."),
"flow-v3full": page("v3-full (Docling, figure features on)", "Comparison arm, 10 pilot papers",
    A.join([s("1. PDF", "one paper per process; partial conversions treated as failures and retried"),
            s("2. Docling (GPU)", "OCR (RapidOCR) + table structure (TableFormer) + picture classification + picture description (SmolVLM-256M)", "gpu"),
            split([s("3a. Body Markdown", "", "new"), s("4a. v2 chunking", "", "same")],
                  [s("3b. One passage per picture", "caption + class + SmolVLM text + <b>OCR text inside the figure</b>", "gpu")],
                  [s("3c. One passage per table", "caption + Markdown table", "gpu")]),
            s("5. Embedding", "same model as v2", "same"), s("v3-full index (pilot)", "", "out")]),
    "AnsHit@10 = 0.455 on figure-only questions. The gain comes from captions, OCR text and tables; SmolVLM produced text for only 14 of 95 pictures, mostly inaccurate."),
"flow-v2-ai": page("v2 + LLM figure descriptions (this project)", "Pilot arm, 10 papers",
    A.join([s("1. v2 body chunks", "unchanged", "same"), s("2. Reuse Docling layout boxes", "figures are cropped; whole papers are not re-processed", "gpu"),
            s("3. Crop + vector/raster check", "", "new"), s("4. Packet per figure", "figure number, caption, sentences citing the figure, image", "new"),
            split([s("5a. Academic description (LLM)", "80–180 words: figure type, variables and units, treatments, trends; <b>only author-reported numbers, with location</b>", "ai"),
                   s("6a. figure_description chunk", "", "new"), s("7a. Embedding", "", "same"), s("v2 + descriptions index", "", "out")],
                  [s("5b. Values read from the figure", "vector figures: PDF drawing coordinates; raster figures: blind magnified reading", "ai"),
                   s("6b. Evidence table", "every value labelled: reported (with location) or estimated", "side"),
                   s("7b. Not indexed", "queried separately; author-reported values take precedence", "side")])]),
    "AnsHit@10 = 0.455 (exact-value questions 0.529); no misjudgment. <b>Combined arm</b>: add Docling captions, OCR text and tables (without SmolVLM) → AnsHit@10 = 0.667, the best of all arms."),
"flow-docling-smolvlm": page("Docling and SmolVLM: architecture and analysis flow", "Docling 2.141 standard PDF pipeline; (v3 / v3-full) shows whether each stage was on",
    A.join([s("1. PDF"), s("2. Page preprocessing", "PDF text cells with coordinates; page images rendered", "new"),
            s("3. OCR — RapidOCR (PP-OCRv6)", "text in raster regions (off / on)", "gpu"),
            s("4. Layout — Heron (RT-DETRv2, ResNet-50 backbone)", "detects 17 region classes: text, title, section header, caption, picture, table, formula, … (on / on)", "gpu"),
            s("5. Table structure — TableFormer", "rows, columns, cells (off / on)", "gpu"),
            s("6. Assembly, reading order, heading hierarchy", "captions linked to their figure or table", "new"),
            split([s("7a. Picture classification — EfficientNet", "26 classes, e.g. line chart, bar chart, scatter plot, photograph (off / on)", "gpu"),
                   s("8a. Picture description — SmolVLM-256M", "pictures ≥ 5% of page area; prompt 'Describe this image in a few sentences.'; ≤ 200 tokens (off / on)", "gpu")],
                  [s("7b. Chart extraction — Granite-Vision 4.1 (4B)", "chart → CSV; ≈8 GB memory", "side"), s("8b. Not run", "insufficient memory on the 8 GB device", "side")]),
            s("9. DoclingDocument → Markdown / JSON", "", "out")]) +
    "<h2>Inside SmolVLM-256M (Idefics3 architecture)</h2>" +
    A.join([s("Image tiling", "long edge ≤ 2,048 px, split into 512×512 tiles plus a downscaled global view", "new"),
            s("Vision encoder — SigLIP-B/16-512 (93M)", "12 layers, hidden 768; 32×32 = 1,024 patch features per tile", "gpu"),
            s("Pixel shuffle (×4) + projection", "64 visual tokens per tile", "gpu"),
            s("Language model — SmolLM2-135M", "30 layers, hidden 576; greedy decoding", "gpu"), s("Picture description text", "", "out")]),
    "Pilot (10 papers): 95 pictures detected; 43 had a description field (the rest presumably below the 5% area threshold); 29 empty, 14 with text, mostly inaccurate."),
}
for name, html in C.items():
    h = OUT / f"{name}.html"; h.write_text(html, encoding="utf-8"); png = OUT / f"{name}.png"
    subprocess.run(["chromium-browser", "--headless", "--disable-gpu", "--hide-scrollbars", f"--screenshot={png}",
                    "--window-size=910,2600", f"file://{h}"], capture_output=True, timeout=120)
    im = Image.open(png).convert("RGB"); bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    im.crop((0, 0, im.width, min(im.height, bb[3] + 24))).save(png); print(name, Image.open(png).size)
