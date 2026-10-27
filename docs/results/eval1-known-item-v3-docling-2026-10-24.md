# Evaluation 1b — rule-based (v2) vs learning-based (v3, Docling) extraction (2026-10-24)

**English** | [繁體中文](#繁體中文)

> Issue: [#5](https://github.com/kylecat/listen-to-your-rag/issues/5). Same questions and protocol as [Evaluation 1](eval1-known-item-2026-10-21.md). Metric guide: [metrics-guide.md](metrics-guide.md).

## Question

Does a learning-based PDF parser retrieve better than our rule-based extractor, when everything after extraction is held constant?

## Design

| Item | v1 (original) | v2 (rule-based, this project) | v3 (learning-based) |
|---|---|---|---|
| Text extraction | page-by-page text | column-aware layout rules (extractor 0.1.4) | Docling 2.141 [1] — layout model on GPU; OCR off; table-structure model off |
| Sectioning, chunking | fixed 500 words | v2 rules | **same as v2** |
| Embedding, search | `nomic-embed-text`, cosine | same | same |

- **Single-factor comparison.** v3 changes only the text source. Docling's Markdown is flattened to plain text and passed through v2's own section rules, chunker and embedding model.
- **Coverage.** 450 papers extracted with Docling (0 failures after one retry for 2 transient GPU errors); 3 scanned papers use the same fallback as v2.
- **Questions.** The 100 known-item questions of Evaluation 1. Two were removed because the corpus changed after they were written: one item was excluded from v2/v3 as a non-paper, and one PDF was replaced with the correct file. Keeping them would favour v1. Main analysis: **98 questions**; sensitivity analysis: **94** questions rated *ok*.
- **Statistics.** Paired differences, bootstrap 95% CI (10,000 resamples), Wilcoxon signed-rank test, exact McNemar test for hit rates.

## Results

**Table 1.** Known-item retrieval, 98 questions.

| Metric | v1 | v2 | v3 | v3 − v2 (95% CI) | p |
|---|---|---|---|---|---|
| Hit@5 | 0.949 | 0.980 | 0.980 | 0.000 (−0.031 to +0.031) | 1.00 |
| Hit@10 | 0.969 | 1.000 | 0.990 | −0.010 (−0.031 to 0.000) | 0.32 |
| MRR@10 | 0.849 | 0.893 | 0.897 | +0.003 (−0.043 to +0.048) | 0.85 |
| F1@5 | 0.316 | 0.327 | 0.327 | 0.000 (−0.010 to +0.010) | 1.00 |

v2 − v1: MRR@10 +0.044 (−0.009 to +0.101; p = 0.14). v3 − v1: MRR@10 +0.047 (−0.006 to +0.100; p = 0.11).

**Table 2.** Sensitivity analysis, 94 questions rated *ok*.

| Metric | v1 | v2 | v3 | v3 − v2 (95% CI) | p |
|---|---|---|---|---|---|
| Hit@5 | 0.957 | 0.979 | 0.989 | +0.011 (0.000 to +0.032) | 0.32 |
| Hit@10 | 0.979 | 1.000 | 1.000 | 0.000 | 1.00 |
| MRR@10 | 0.861 | 0.902 | 0.911 | +0.009 (−0.032 to +0.050) | 0.69 |

**Table 3.** Text-layer statistics (448 papers extracted by both v2 and v3).

| | v2 | v3 |
|---|---|---|
| Chunks per paper (mean) | 21.2 | 19.9 |
| Chunks without a section label | 4.7% | 4.4% |
| Papers with an abstract detected | 444 | 447 |
| Extraction time | minutes, CPU only | ≈ 0.4 s per page on GPU (≈ 9,800 pages over two nights) |

## Findings

1. **v2 and v3 tie.** All v3 − v2 differences are ≤ 0.01 and not significant.
2. **Both improve on v1 numerically, not significantly** (MRR@10 +0.04 to +0.05; all CIs include 0).
3. **Ceiling effect.** v2 and v3 place the gold paper in the top 5 for 98% of questions; this benchmark cannot separate them.
4. **For single articles, the two extractors give nearly the same text.** In a spot check of a two-column journal article, section word counts differed by 1–5%, and both versions shared the same defect (a table footnote at the start of one section).
5. **The one large difference comes from section rules, not from the parser.** In one book-length proceedings volume, v3 kept 33k of 90k words: after the first reference list, later chapters had headings that v2's section rules did not recognise in Docling's output, so their text was treated as back matter and dropped.

## Interpretation

- For this corpus, a learning-based layout model did **not** improve retrieval over rule-based layout extraction, at a much higher compute cost.
- The remaining bottleneck is **after** extraction — section rules for long documents, and tables and figures, which neither v2 nor v3 indexes yet.
- Based on this result, v2 was adopted as the production index on 2026-10-27.

## Limitations

- Known-item questions mainly test whether a paper can be found; they are insensitive to finer text-quality differences. The topic-query evaluation ([#4](https://github.com/kylecat/listen-to-your-rag/issues/4)) is pending.
- v3 used v2's section rules; Docling's own document structure was not used, so v3 is a lower bound for Docling.
- Tables were excluded in both versions.
- One corpus (≈ 450 CEA papers), one embedding model; GROBID was not tested.

## References

[1] Auer, C. et al. (2024). *Docling Technical Report.* arXiv:2408.09869.

---

## 繁體中文

> 對應 Issue：[#5](https://github.com/kylecat/listen-to-your-rag/issues/5)。題目與流程同[評測 1](eval1-known-item-2026-10-21.md)；指標說明見 [metrics-guide.md](metrics-guide.md)。

### 研究問題

擷取之後的步驟全部固定時，學習式 PDF 解析工具的檢索效果是否優於本專案的規則式擷取？

### 設計

| 項目 | v1（舊版） | v2（規則式，本專案） | v3（學習式） |
|---|---|---|---|
| 文字擷取 | 逐頁抽取 | 依欄位排版的規則（擷取模組 0.1.4） | Docling 2.141 [1]：GPU 版面模型；不做 OCR；不做表格結構辨識 |
| 章節判斷、切段 | 每 500 字 | v2 規則 | **與 v2 相同** |
| 向量模型、檢索 | `nomic-embed-text`、cosine | 同左 | 同左 |

- **單一變因**：v3 只換文字來源。Docling 輸出的 Markdown 轉成純文字後，經過 v2 同一套章節規則、切段方式與向量模型。
- **涵蓋範圍**：Docling 擷取 450 篇，全部成功（2 篇 GPU 偶發錯誤重試後成功）；3 篇掃描檔與 v2 相同，沿用舊版。
- **題目**：評測 1 的 100 題。其中 2 題在出題後語料有變動（1 篇確認為非論文而排除，1 篇換成正確的 PDF），保留會對 v1 有利，故剔除。主要分析用 **98 題**，敏感度分析用 **94 題**（品質為 ok 的題目）。
- **統計**：配對差、bootstrap 95% 信賴區間（重抽 10,000 次）、Wilcoxon 符號等級檢定；命中率另做 McNemar 精確檢定。

### 結果

**表 1.** 已知答案檢索，98 題。

| 指標 | v1 | v2 | v3 | v3 − v2（95% CI） | p |
|---|---|---|---|---|---|
| Hit@5 | 0.949 | 0.980 | 0.980 | 0.000（−0.031～+0.031） | 1.00 |
| Hit@10 | 0.969 | 1.000 | 0.990 | −0.010（−0.031～0.000） | 0.32 |
| MRR@10 | 0.849 | 0.893 | 0.897 | +0.003（−0.043～+0.048） | 0.85 |
| F1@5 | 0.316 | 0.327 | 0.327 | 0.000（−0.010～+0.010） | 1.00 |

v2 − v1：MRR@10 +0.044（−0.009～+0.101；p = 0.14）。v3 − v1：MRR@10 +0.047（−0.006～+0.100；p = 0.11）。

**表 2.** 敏感度分析，94 題。

| 指標 | v1 | v2 | v3 | v3 − v2（95% CI） | p |
|---|---|---|---|---|---|
| Hit@5 | 0.957 | 0.979 | 0.989 | +0.011（0.000～+0.032） | 0.32 |
| Hit@10 | 0.979 | 1.000 | 1.000 | 0.000 | 1.00 |
| MRR@10 | 0.861 | 0.902 | 0.911 | +0.009（−0.032～+0.050） | 0.69 |

**表 3.** 文字層統計（v2、v3 皆有擷取的 448 篇）。

| | v2 | v3 |
|---|---|---|
| 每篇段落數（平均） | 21.2 | 19.9 |
| 無章節標籤的段落 | 4.7% | 4.4% |
| 偵測到摘要的論文數 | 444 | 447 |
| 擷取時間 | 數分鐘，只用 CPU | GPU 每頁約 0.4 秒（約 9,800 頁，兩晚） |

### 主要發現

1. **v2 與 v3 打平**：v3 − v2 的差異都在 0.01 以內，皆不顯著。
2. **兩者數值上都優於 v1，但不顯著**：MRR@10 +0.04～+0.05，信賴區間皆包含 0。
3. **天花板效應**：v2、v3 都有 98% 的題目把正確論文排進前 5 名，本評測無法區分兩者。
4. **單篇論文的擷取結果幾乎相同**：抽查一篇雙欄期刊論文，各章節字數差 1–5%，兩版連同一個瑕疵都一樣（表格註腳混入某章節開頭）。
5. **唯一的大差距來自章節規則，而非解析工具**：一本論文集在 v3 只保留 9 萬字中的 3.3 萬字。原因是第一份參考文獻之後，後續章節標題在 Docling 輸出中的格式不符合 v2 的章節規則，內容被當成參考文獻區而捨棄。

### 解讀

- 在本語料上，學習式版面模型**沒有**比規則式擷取帶來更好的檢索結果，運算成本卻高出許多。
- 剩下的瓶頸在擷取**之後**：長篇文件的章節規則，以及 v2、v3 都尚未納入的表格與圖。
- 依據本結果，2026-10-27 起以 v2 作為線上索引。

### 限制

- 已知答案題主要測「找不找得到」，對細部文字品質不敏感；主題查詢評測（[#4](https://github.com/kylecat/listen-to-your-rag/issues/4)）尚未進行。
- v3 使用 v2 的章節規則，沒有使用 Docling 自己的文件結構，因此 v3 的結果是 Docling 表現的下限。
- 兩版皆未納入表格。
- 單一語料（約 450 篇 CEA 論文）、單一向量模型；未測試 GROBID。

### 參考文獻

[1] Auer, C. et al. (2024). *Docling Technical Report.* arXiv:2408.09869.
