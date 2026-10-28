# 06 · Figure layer: methods / 圖表層方法

**English** | [繁體中文](06-figure-layer.zh-TW.md)

> Status: pilot on 10 papers (2026-10-28). Results: [figure-layer-pilot-2026-10-28.md](../results/figure-layer-pilot-2026-10-28.md). Flowcharts: [figures/figure-layer/](../figures/figure-layer/).

## Goal
Make information that appears only in figures and tables retrievable, without letting values estimated from plots be mistaken for values reported by the authors.

## Pipelines compared

| Pipeline | Summary | Flowchart |
|---|---|---|
| v1 | page-by-page extraction, fixed 500-word chunks; captions and table fragments mixed into body text | [flow-v1](../figures/figure-layer/flow-v1.png) |
| v2 | coordinate-aware rule-based extraction ([01](01-extraction.md), [02](02-chunking-and-index.md)); **captions and tables dropped** | [flow-v2](../figures/figure-layer/flow-v2.png) |
| v3 | Docling text with v2 sectioning and chunking; figure models off | [flow-v3](../figures/figure-layer/flow-v3.png) |
| v3-full | Docling with OCR, table structure, picture classification and SmolVLM-256M; one passage per picture and per table | [flow-v3full](../figures/figure-layer/flow-v3full.png) |
| v2 + LLM descriptions | v2 body + one academic figure description per figure; plot-read values go to a separate evidence table | [flow-v2-ai](../figures/figure-layer/flow-v2-ai.png) |
| Combined | v2 + LLM descriptions + Docling captions, OCR text and tables (no SmolVLM text) | — |

All pipelines use the same embedding model and similarity metric, so differences come from the text that is indexed.

## v2 + LLM figure descriptions
1. **Locate and crop**: reuse figure bounding boxes from Docling's layout model; crop each figure from the PDF. Whole papers are not re-processed.
2. **Vector or raster**: check whether the box contains PDF drawing operations (vector) or an embedded image (raster).
3. **Packet**: figure number parsed from the caption, the caption, sentences that cite the figure, and the image.
4. **Description** (LLM): 80–180 words in the paper's terminology: figure type, variables and units, treatments and conditions, main trends. **Only numbers reported by the authors** (text, caption, table, or printed on the figure), each with its location. A header line marks the passage as AI-generated.
5. **Index**: one chunk per figure, `section_type = figure_description`.
6. **Evidence table (not indexed)**: values read from plots, stored separately.

## Rules for estimated values
| Rule | Content |
|---|---|
| Separate storage | Body text and figure descriptions are indexed; plot-read values live only in the evidence table, which agents query separately |
| Label every estimate | `57% [estimated │ authors report 58% (Results, p.6)]` or `4.54 mmol m⁻² s⁻¹ [estimated │ not reported by the authors]` |
| Agreement field | `match` (≤ 5% difference), `differs` (> 5%, needs human review), `not_reported` |
| Precedence | When the authors report a value, cite it; estimates are supplementary |
| Reading methods | vector figures: PDF drawing coordinates + axis-tick calibration; raster figures: magnified reading, blind to the paper text |

## Docling and SmolVLM architecture
Docling 2.141 standard PDF pipeline (configuration read from the installed model files; flowchart [flow-docling-smolvlm](../figures/figure-layer/flow-docling-smolvlm.png)):

| Stage | Component | v3 | v3-full |
|---|---|---|---|
| Page preprocessing | PDF text cells and page images | on | on |
| OCR | RapidOCR (PP-OCRv6 detection + recognition) | off | on |
| Layout | Heron: RT-DETRv2 detector, ResNet-50 backbone, 17 region classes | on | on |
| Table structure | TableFormer | off | on |
| Assembly | reading order, heading hierarchy, caption linking | on | on |
| Picture classification | EfficientNet, 26 classes | off | on |
| Picture description | SmolVLM-256M-Instruct | off | on |
| Chart extraction | Granite-Vision 4.1 (4B) | off | off (≈8 GB memory) |

SmolVLM-256M (Idefics3 architecture): images are tiled into 512×512 crops plus a global view; a SigLIP-B/16-512 vision encoder (93M parameters) produces 1,024 patch features per tile, compressed by pixel shuffle (×4) to 64 visual tokens; SmolLM2-135M generates the text. Docling's defaults: prompt "Describe this image in a few sentences.", up to 200 tokens, only pictures covering ≥ 5% of the page.

## Recommended design for the full library
Process figures only (no full re-run): reuse layout boxes; for each figure index the caption, the OCR text inside the figure and an LLM academic description; convert tables to Markdown; do not use SmolVLM descriptions. Before scaling up, add an automatic caption–figure pairing check and keep author-reported values separate from descriptions.

## References
Auer, C. et al. (2024). *Docling Technical Report.* arXiv:2408.09869. SmolVLM-256M-Instruct model card (Hugging Face): SmolLM2-135M-Instruct + google/siglip-base-patch16-512.
