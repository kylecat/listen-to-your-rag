# listen-to-your-rag

**Structure-aware PDF extraction for a domain literature RAG — methods, evaluation and results**
**為領域文獻 RAG 設計的版面感知 PDF 擷取：方法、評測與結果紀錄**

This repository documents the **method and results** of rebuilding the text layer of a literature retrieval-augmented generation (RAG) system for **controlled environment agriculture (CEA)** research — roughly 460 papers on plant factories, vapor pressure deficit, lighting, hydroponics and AI agents.
It is a **lab notebook in public**: the code is not published here; the methods, design decisions, evaluation protocol and results are.

本 repo 公開記錄我們重建 CEA（受控環境農業）研究文獻 RAG「文字層」的**方法與結果**（約 460 篇論文）。這裡**不放程式碼**，只公開方法、設計決策、評測流程與結果，並持續更新。

## Why / 為什麼

Our first RAG index (v1) extracted PDFs page by page and split text every 500 words. An audit showed:

- **62%** of chunks had no section label (abstract, methods, results…);
- two-column papers had **left and right columns interleaved** in the same line;
- page headers, footers, journal metadata and table fragments were mixed into the text;
- **78** indexed papers pointed to PDF paths that no longer existed after file renaming.

The rebuilt pipeline (v2) uses one shared extraction module for **both** the RAG index and a text-to-speech read-aloud tool, so what a human hears is exactly what the retriever indexes — turning listening practice into a **quality audit of the RAG corpus**.

## Contents / 內容

| Document | Description |
|---|---|
| [docs/related-work.md](docs/related-work.md) | Related research and tools, verified with sources（學術研究與工具查證） |

More documents (method details, evaluation protocol, results, figure/table handling) will be added as the work progresses.

## Status / 進度

| Date | Update |
|---|---|
| 2026-10-21 | Repository created; related work published. v2 index built (not yet in production); evaluation (known-item queries + pooled topic queries with blind relevance judgments) planned. |

## Scope and limitations / 範圍與限制

- This is a **rule-based** layout approach. Published comparisons show rule-based parsers struggle on scientific papers relative to learning-based tools (e.g. Nougat, Docling, GROBID); we plan to include such a baseline in the evaluation.
- Copyrighted papers, extracted text and model outputs derived from them are **not** distributed.
- Results are from one domain corpus and may not generalise.

## License / 授權

License to be decided (copyleft documentation licence under consideration). Until then, all rights reserved.
授權確認中（考慮採用 copyleft 文件授權）；確定前保留所有權利。
