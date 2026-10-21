# 02 · 切塊與索引建置（Chunking and index builder）

[English](02-chunking-and-index.md) | **繁體中文**

> 讀取擷取模組（[01](01-extraction.zh-TW.md)）的輸出；在舊索引旁寫入一個新索引。

## 1. 段落（切塊）欄位結構（v1 與 v2 相同）（Chunk schema）

| 欄位 | 型別 | 備註 |
|---|---|---|
| `chunk_id` | str | `<source_id>__chunkNNNN`；翻譯為 `<source_id>__en00` |
| `source_id` | str | 穩定的論文 id（沿用 v1） |
| `pdf_path` | str | 目前的檔案路徑（修復後） |
| `title`, `year` | str, int | 沿用 v1 的 metadata（人工整理過的標題） |
| `section_type` | str | abstract · introduction · methods · results · discussion · conclusion · other (= body) · translation_en |
| `chunk_index` | int | 在論文內的順序；翻譯段落使用 9000 |
| `chunk_text` | str | |
| `word_count` | int | 拉丁字詞數 + CJK 字元數 / 2 |
| `topic_tags` | [str] | 沿用 v1 |
| `vector` | float[768] | 與 v1 相同的向量模型 |

欄位結構保持一致，搜尋服務只需改資料表名稱即可切換版本。

## 2. 切塊規則（Chunking rules）

1. 對 `reading_sections()` 中的每個章節，把其段落接起來（以換行接合；CJK 句子之間不加分隔）。
2. 在 `. ! ?` 後接空白與大寫字母／括號之處，以及 `。 ． ！ ？` 之後切分句子。
3. 逐句累積，直到段落達到 **500 字**；下一個段落以合計 **≥ 80 字**的尾端句子開頭（重疊）。
4. 最後的剩餘部分只有在超過 100 字（重疊 + 20）或它是唯一的段落時，才自成一個段落。
5. 捨棄 ≤ 20 字的段落。
6. 若整份文件 **< 300 字**，視為擷取失敗（掃描檔、文字層為空）→ **退回**：原封不動複製該論文的 v1 段落，並記錄 `reason=extract_too_short`。

## 3. 向量化（Embedding）

- 與 v1 相同的模型與維度（`nomic-embed-text`，768 維）。
- 最多送出 8,000 個字元；遇到伺服器錯誤時依序以 6,000 → 4,000 → 2,500 個字元重試，仍失敗則該批次失敗。

## 4. 分批重建（Batch rebuild）

```text
rebuild --batch N
  todo = papers (sorted by source_id) not yet in state.done, first N
  for each paper:
     if in skip list            -> record mode=skipped (duplicate / not_a_paper); write nothing
     path = path_fixes[source_id] or v1 path
     if file missing            -> fallback to v1 chunks (reason=missing_pdf)
     else extract + chunk       -> v2 chunks, or fallback (reason=extract_too_short / error)
     if translation exists      -> add one translation_en chunk
     record per-paper stats (old/new chunk counts, share of 'other', abstract found, sections)
  delete existing v2 rows for these papers, insert the new rows   # idempotent per batch
  append batch summary; save state
```

- **狀態檔**保存每篇論文的結果 → 重跑可續跑，當機時最多只損失一個批次（資料列只在批次結束時才寫入）。
- 在背景服務中執行批次，每批約 50 篇論文（在我們的主機上每批約 2–5 分鐘）。
- 執行途中更換擷取器會產生混合版本 → 回報數字前，請以**單一版本完整重建**收尾。

## 5. 以內容比對找回檔案（Path recovery by content matching）

當儲存的路徑過時（檔案被改名或搬移）時：
1. 對每篇檔案遺失的論文，從其 **v1 段落文字**建立特徵：轉小寫、去除標點，從前幾個段落取最多 12 個六字詞組片段（shingle）（從第 40 個字開始，每 60 個字取一個）。
2. 對**機器上的每個 PDF** 擷取前 4 頁一次（快取正規化後的文字）。
3. 分數 = 在候選檔文字中找到的詞組片段比例；分數 ≥ 0.4，或分數 ≥ 0.17 且標題字詞重疊率 ≥ 0.5 時接受；否則標記為待人工檢查。
4. 若比對到的檔案已經是另一篇論文的路徑 → **重複**，加入略過清單。
5. 在文獻庫之外找到的檔案一律**複製**進來（絕不搬移）；兩者都存在時，優先採用文獻庫中既有的副本。
6. 把 `source_id → new path` 對應存入修正檔；絕不改寫 v1。

在我們語料上的結果：78 篇遺失的論文找回 76 篇（另 2 篇並非論文）。

## 6. 去重與排除（De-duplication and exclusions）

- 以多個 id 建立索引、但位元組完全相同（MD5 相同）的檔案：保留一個 id，其餘以 `dup_of` 加入略過清單。
- 非論文（期刊作者索引、傳單）：以 `reason=not_a_paper` 加入略過清單。
- 文獻庫中的重複**檔案**移到 `_duplicates/` 資料夾，不刪除。

## 7. 非英文論文（Non-English papers）

- 擷取會保留 CJK 文字（見 [01](01-extraction.zh-TW.md)）；英文向量模型以英文查詢檢索這些文字的效果很差。
- 對每篇日文論文加入**一個英文摘要段落**，由 LLM 根據原文撰寫，開頭帶有可見的標示，例如 `[English summary translated from the Japanese original by <model>; not the authors' text]`，`section_type=translation_en`。
- 當非英文論文的占比變得可觀時，再重新評估多語向量模型。

## 8. 切換與回退（Switching and rollback）

1. 評估（[04](04-evaluation.zh-TW.md)）。
2. 把搜尋服務指向新資料表；重新啟動服務。
3. 回退 = 指回舊資料表。保留舊資料表，直到新資料表已使用一段時間。
4. 同時把新論文的匯入改用 v2 管線。
