# 02 · Chunking and index builder / 切塊與索引建置

> Consumes the extraction module ([01](01-extraction.md)); writes a new index next to the old one.

## 1. Chunk schema (identical in v1 and v2) / 段落欄位

| Field | Type | Notes |
|---|---|---|
| `chunk_id` | str | `<source_id>__chunkNNNN`; translations `<source_id>__en00` |
| `source_id` | str | stable paper id (kept from v1) |
| `pdf_path` | str | current file path (after recovery) |
| `title`, `year` | str, int | kept from v1 metadata (curated titles) |
| `section_type` | str | abstract · introduction · methods · results · discussion · conclusion · other (= body) · translation_en |
| `chunk_index` | int | order within the paper; translation chunk uses 9000 |
| `chunk_text` | str | |
| `word_count` | int | Latin words + CJK chars / 2 |
| `topic_tags` | [str] | kept from v1 |
| `vector` | float[768] | same embedding model as v1 |

Keeping the schema identical lets search services switch versions by table name only.

## 2. Chunking rules / 切塊規則

1. For each section in `reading_sections()`, join its paragraphs (newline; no separator between CJK sentences).
2. Split into sentences at `. ! ?` followed by whitespace and an upper-case letter/bracket, and after `。 ． ！ ？`.
3. Accumulate sentences until the chunk reaches **500 words**; start the next chunk with trailing sentences totalling **≥ 80 words** (overlap).
4. The last remainder becomes its own chunk only if it has > 100 words (overlap + 20) or it is the only chunk.
5. Drop chunks with ≤ 20 words.
6. If the whole document has **< 300 words**, treat extraction as failed (scan, empty text layer) → **fallback**: copy the paper's v1 chunks unchanged and record `reason=extract_too_short`.

## 3. Embedding / 向量化

- Same model and dimension as v1 (`nomic-embed-text`, 768-d).
- Send at most 8,000 characters; on a server error retry with 6,000 → 4,000 → 2,500 characters, then fail the batch.

## 4. Batch rebuild / 分批重建

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

- **State file** keeps per-paper results → reruns are resumable and a crash loses at most one batch (rows are written only at the end of a batch).
- Run batches in a background service, ~50 papers per batch (≈2–5 min each on our host).
- Changing the extractor mid-run produces mixed versions → finish with a **single-version full rebuild** before reporting numbers.

## 5. Path recovery by content matching / 以內容比對找回檔案

When stored paths are stale (files renamed or moved):
1. For each paper with a missing file, build signatures from its **v1 chunk text**: lower-case, strip punctuation, take up to 12 six-word shingles from the first chunks (every 60 words, starting at word 40).
2. Extract the first 4 pages of **every PDF on the machine** once (cache the normalised text).
3. Score = fraction of shingles found in a candidate's text; accept if score ≥ 0.4, or ≥ 0.17 with title-word overlap ≥ 0.5; otherwise mark for manual review.
4. If the matched file is already the path of another paper → **duplicate**, add to the skip list.
5. Files found outside the library are **copied** in (never moved); prefer an existing library copy when both exist.
6. Store the mapping `source_id → new path` in a fixes file; never rewrite v1.

Result on our corpus: 76 of 78 missing papers recovered (2 were not papers).

## 6. De-duplication and exclusions / 去重與排除

- Byte-identical files (same MD5) indexed under several ids: keep one id, add the others to the skip list with `dup_of`.
- Non-papers (journal author index, flyers): skip list with `reason=not_a_paper`.
- Duplicate **files** in the library are moved to a `_duplicates/` folder, not deleted.

## 7. Non-English papers / 非英文論文

- Extraction keeps CJK text (see [01](01-extraction.md)); the English embedding model retrieves it poorly from English queries.
- For each Japanese paper add **one English summary chunk** written from the original by an LLM, beginning with a visible label such as `[English summary translated from the Japanese original by <model>; not the authors' text]`, `section_type=translation_en`.
- Revisit multilingual embeddings when non-English papers become a meaningful share.

## 8. Switching and rollback / 切換與回退

1. Evaluate ([04](04-evaluation.md)).
2. Point search services to the new table; restart them.
3. Rollback = point back to the old table. Keep the old table until the new one has been in use for a while.
4. Move new-paper ingestion to the v2 pipeline at the same time.
