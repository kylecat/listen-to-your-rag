# listen-to-your-rag

**English** | [繁體中文](README.zh-TW.md)

**Structure-aware PDF extraction for a domain literature RAG — methods, evaluation and results**

This repository documents the **method and results** of rebuilding the text layer of a literature retrieval-augmented generation (RAG) system for **controlled environment agriculture (CEA)** research — roughly 460 papers on plant factories, vapor pressure deficit, lighting, hydroponics and AI agents.
It is a **lab notebook in public**: the code is not published here; the methods, design specifications, evaluation protocol and results are — detailed enough to rebuild the system with a coding agent (see [harness](harness/README.md)).

## Why

Our first RAG index (v1) extracted PDFs page by page and split text every 500 words. An audit showed:

- **62%** of chunks had no section label (abstract, methods, results…);
- two-column papers had **left and right columns interleaved** in the same line;
- page headers, footers, journal metadata and table fragments were mixed into the text;
- **78** indexed papers pointed to PDF paths that no longer existed after file renaming.

The rebuilt pipeline (v2) uses one shared extraction module for **both** the RAG index and a text-to-speech read-aloud tool, so what a human hears is exactly what the retriever indexes — turning listening practice into a **quality audit of the RAG corpus**.

## Contents

| Document | Description |
|---|---|
| [docs/method-v1-v2.md](docs/method-v1-v2.md) | v1 vs v2 text pipeline, flowchart and first-pass results |
| [docs/results/eval1-known-item-2026-10-21.md](docs/results/eval1-known-item-2026-10-21.md) | Evaluation 1 results (known-item queries) |
| [docs/related-work.md](docs/related-work.md) | Related research and tools, verified with sources |
| [docs/design/](docs/design/00-overview.md) | **Design specifications** (overview, extraction, chunking & index, read-aloud, evaluation, acceptance tests) — enough to rebuild the system without our code |
| [harness/](harness/README.md) | **Harness** for rebuilding with a coding agent: standing instructions (`AGENTS.md`), phased build plan with gates, prompts |

More documents (method details, evaluation protocol, results, figure/table handling) will be added as the work progresses.

## Status

| Date | Update |
|---|---|
| 2026-10-21 | Evaluation 1 (known-item, 100 questions): v2 ≥ v1 on all metrics but no significant difference; ceiling effect (#3). |
| 2026-10-21 | Design specifications and agent harness published, so the system can be rebuilt from documents. |
| 2026-10-21 | Method write-up and flowchart published (#1). |
| 2026-10-21 | Repository created; related work published. v2 index built (not yet in production); evaluation (known-item queries + pooled topic queries with blind relevance judgments) planned. |

## Scope and limitations

- This is a **rule-based** layout approach. Published comparisons show rule-based parsers struggle on scientific papers relative to learning-based tools (e.g. Nougat, Docling, GROBID); we plan to include such a baseline in the evaluation.
- Copyrighted papers, extracted text and model outputs derived from them are **not** distributed.
- Results are from one domain corpus and may not generalise.

## Publication principles

- **Verified citations** — every reference is checked against its primary source; secondary or unverified sources are marked.
- **Versioned, honest numbers** — results state their date, pipeline version and whether they are preliminary; differences are not reported as improvements until evaluated.
- **Stated limitations** — scope, failure cases and the fact that the approach builds on established methods are stated explicitly.
- **AI disclosure** — the AI model, its version and its role are disclosed and kept up to date; AI-generated translations, descriptions and judgments are labelled as such.
- **No private or copyrighted material** — no infrastructure details, credentials or copyrighted paper text are published.

## Authors and AI disclosure

- **Research direction, decisions and review**: [@kylecat](https://github.com/kylecat)
- **AI assistant**: **Iris**, an operations and research assistant built on **Claude Opus 5.5** (`claude-opus-5-5`, Anthropic), running through Claude Code on the lab's Jetson host.

What the AI did:
- designed and implemented the extraction and chunking pipeline, ran the index rebuilds and comparisons;
- searched for and verified the related literature;
- drafted the documents and figures in this repository;
- wrote English summaries of Japanese-language papers (marked as translations in the index);
- will act as the LLM relevance judge in the evaluation, checked against a human-judged subset (Cohen's κ reported).

All decisions on scope, data handling, publication and licensing were made by the human author.

Other models used:
| Purpose | Model |
|---|---|
| Text embedding | `nomic-embed-text` (768-d, via Ollama) |
| Text-to-speech | Kokoro-82M (ONNX), voice `af_bella` |

## License

Documentation in this repository is licensed under **[Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/)** — see [LICENSE](LICENSE). You may share and adapt it with attribution; derivative works must use the same licence.

Linked papers and tools remain under their own licences.
