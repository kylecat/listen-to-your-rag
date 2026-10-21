# 00 · 系統總覽（System overview）

[English](00-overview.md) | **繁體中文**

> 這組設計文件讓讀者**不需要我們的程式碼**也能重建系統：以下規格寫到足以讓開發者，或由 harness 驅動的程式代理（見 [`../../harness/`](../../harness/)），逐一重新實作各元件，並依所列的驗收條件檢查。

狀態：描述的是管線版本 **v2 / extractor 0.1.4**（2026-10-21）。文中引用的數字除非標示為最終值，否則皆為初步結果。

## 目標（Goal）

把一個裝滿學術論文 PDF 的資料夾（多為英文，部分為日文／中文；許多為雙欄排版）轉成：
1. 一個由乾淨、分好章節、以句子為界的段落（切塊）所組成的**檢索索引**；以及
2. 同一份文字的**朗讀**串流，讓人可以實際聆聽——並稽核——索引裡到底裝了什麼。

## 元件（Components）

| # | 元件 | 輸入 → 輸出 | 規格 |
|---|---|---|---|
| 1 | **擷取模組** | PDF → 結構化文件（章節、段落） | [01-extraction.zh-TW.md](01-extraction.zh-TW.md) |
| 2 | **切塊與索引建置** | 結構化文件 → 段落 + 向量存入向量資料庫；批次重建、路徑修復、去重 | [02-chunking-and-index.zh-TW.md](02-chunking-and-index.zh-TW.md) |
| 3 | **朗讀** | 章節文字 → 可念出的文字 → 語音 → 語音訊息；聆聽回報 | [03-read-aloud.zh-TW.md](03-read-aloud.zh-TW.md) |
| 4 | **評估** | 兩個索引 + 查詢集 → 檢索指標 | [04-evaluation.zh-TW.md](04-evaluation.zh-TW.md) |
| 5 | **驗收測試** | 各元件必須滿足的行為 | [05-acceptance-tests.zh-TW.md](05-acceptance-tests.zh-TW.md) |

```
PDF ─► [1 Extraction] ─► structured document ─┬─► [2 Chunk + embed] ─► vector index ─► agents / search UI
                         (cached)             └─► [3 Speakable rewrite ─► TTS] ─► listener ─► flags ─► rule fixes ─┐
                                                                                                                  └─► back to [1]
```

## 設計原則（Design principles）

1. **一層文字，兩個使用端。** 索引與朗讀工具使用同一份擷取輸出，因此聆聽就是對索引的忠實稽核。
2. **新索引勝出前保留舊索引。** v2 建在另一個欄位結構相同的資料表；切換只是改資料表名稱，回退則反向操作。
3. **各版本使用相同的向量模型**，因此差異只來自文字層。
4. **可續跑的批次。** 長時間工作分批執行，並保存每篇論文的狀態；失敗的批次不寫入任何東西。
5. **退回舊版，絕不無聲遺失。** 擷取失敗時（掃描檔、檔案遺失），沿用前一版的段落並記錄原因。
6. **所有生成內容皆加標示**（翻譯、圖片描述、LLM 判斷）。

## 參考環境（Reference environment）

| 項目 | 我們的環境 | 備註 |
|---|---|---|
| 主機 | NVIDIA Jetson Orin Nano 8 GB（CPU/GPU 共用記憶體，約 4 GB 可用） | 任何有 4 GB 可用 RAM 的機器皆可 |
| PDF 工具 | poppler（`pdftotext`、`pdfinfo`） | 需支援 `-bbox-layout` |
| 向量資料庫 | LanceDB | 任何具固定欄位結構且可逐列刪除的資料庫 |
| 向量模型 | `nomic-embed-text`，經 Ollama（768 維） | 各版本間保持一致 |
| TTS | Kokoro-82M（ONNX，fp32） | int8 在 ARM CPU 上反而較慢 |
| 用來建置的 agent harness | Claude Code 搭配 Claude Opus 5.5 | 見 `harness/` |

## 目前不含（Out of scope, for now）

圖與表（規劃中：圖表說明 → 表格 → 圖片描述）、以學習為基礎的版面模型（未來比較方向）、多語向量模型。
