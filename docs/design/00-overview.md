# 00 · System overview / 系統總覽

**English** | [繁體中文](00-overview.zh-TW.md)

> Design documents for rebuilding the system **without our code**: the specifications below are written so that a developer — or a coding agent driven by a harness (see [`../../harness/`](../../harness/)) — can re-implement each component and check it against the stated acceptance criteria.
> 這組設計文件讓讀者**不需要我們的程式碼**也能重建系統：規格寫到足以讓開發者或由 harness 驅動的程式代理（見 `harness/`）逐一實作，並用驗收條件檢查。

Status: describes pipeline version **v2 / extractor 0.1.4** (2026-10-21). Numbers quoted are first-pass unless marked final.

## Goal / 目標

Turn a folder of academic PDFs (mostly English, some Japanese/Chinese; many two-column) into:
1. a **retrieval index** of clean, sectioned, sentence-aligned chunks; and
2. a **read-aloud** stream of the same text, so a human can listen to — and audit — exactly what the index contains.

## Components / 元件

| # | Component | Input → output | Spec |
|---|---|---|---|
| 1 | **Extraction module** | PDF → structured document (sections, paragraphs) | [01-extraction.md](01-extraction.md) |
| 2 | **Chunking & index builder** | structured document → chunks + vectors in a vector store; batch rebuild, path recovery, de-duplication | [02-chunking-and-index.md](02-chunking-and-index.md) |
| 3 | **Read-aloud** | section text → speakable text → speech → voice message; listener flags | [03-read-aloud.md](03-read-aloud.md) |
| 4 | **Evaluation** | two indexes + query sets → retrieval metrics | [04-evaluation.md](04-evaluation.md) |
| 5 | **Acceptance tests** | behaviour each component must satisfy | [05-acceptance-tests.md](05-acceptance-tests.md) |

```
PDF ─► [1 Extraction] ─► structured document ─┬─► [2 Chunk + embed] ─► vector index ─► agents / search UI
                         (cached)             └─► [3 Speakable rewrite ─► TTS] ─► listener ─► flags ─► rule fixes ─┐
                                                                                                                  └─► back to [1]
```

## Design principles / 設計原則

1. **One text layer, two consumers.** The index and the read-aloud tool use the same extraction output, so listening is a faithful audit of the index.
2. **Keep the old index until the new one wins.** Build v2 into a separate table with the same schema; switching is a table-name change; rollback is the reverse.
3. **Same embedding model across versions**, so differences come from the text layer only.
4. **Resumable batches.** Long jobs run in batches with persistent per-paper state; a failed batch writes nothing.
5. **Fallback, never silent loss.** When extraction fails (scans, missing files) keep the previous version's chunks and record the reason.
6. **Everything generated is labelled** (translations, figure descriptions, LLM judgments).

## Reference environment / 參考環境

| Item | Ours | Notes |
|---|---|---|
| Host | NVIDIA Jetson Orin Nano 8 GB (shared CPU/GPU memory, ~4 GB free) | anything with 4 GB free RAM works |
| PDF tools | poppler (`pdftotext`, `pdfinfo`) | `-bbox-layout` support required |
| Vector store | LanceDB | any store with a fixed schema and per-row delete |
| Embedding | `nomic-embed-text` via Ollama (768-d) | keep identical across versions |
| TTS | Kokoro-82M (ONNX, fp32) | int8 was slower on ARM CPU |
| Agent harness used to build it | Claude Code with Claude Opus 5.5 | see `harness/` |

## Out of scope (for now) / 目前不含

Figures and tables (planned: captions → tables → figure descriptions), learning-based layout models (future comparison), multilingual embeddings.
