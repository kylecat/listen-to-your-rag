# Figure-layer pilot: making figure content retrievable (10 papers, 2026-10-28)

**English** | [繁體中文](#繁體中文)

> Issues: [#6](https://github.com/kylecat/listen-to-your-rag/issues/6) (captions), [#7](https://github.com/kylecat/listen-to-your-rag/issues/7) (tables), [#8](https://github.com/kylecat/listen-to-your-rag/issues/8) (figure descriptions). Methods: [design/06-figure-layer.md](../design/06-figure-layer.md). Status: **pilot, preliminary numbers**.

## Questions
1. If figures are turned into text, can information that appears only in figures be retrieved?
2. How do four pipelines compare: v2, v3 (Docling), v3-full (Docling with figure models) and v2 + LLM figure descriptions?
3. Do figure passages cause misretrieval?
4. How accurate are values read back from plots?

## Sample
Ten experimental papers on vapor pressure deficit (VPD), transpiration and stomatal conductance: 43 figures (38 data figures; 9 vector, 34 raster) and 31 tables.
Zhang et al. 2021 [1]; Ding et al. 2022 [2]; Amitrano et al. 2021 [3]; Inoue et al. 2021 [4]; Broughton & Conaty 2022 [5]; Devi & Reddy 2018 [6]; Medina et al. 2019 [7]; Li et al. 2018 [8]; Barron-Gafford et al. 2007 [9]; Eze et al. 2024 [10].

## Arms
| Arm | Text layer | Figure layer |
|---|---|---|
| v2 | rule-based extraction (production) | none; captions and tables are dropped |
| v3 | Docling, figure models off | none |
| v3-full | Docling, OCR + table structure + picture classification + SmolVLM-256M | caption + SmolVLM text + OCR text per picture; Markdown per table |
| v2 + LLM descriptions | v2 | one academic description per figure (Claude Opus 5.5), author-reported numbers only |
| Combined | v2 | LLM descriptions + Docling captions, OCR text and tables (SmolVLM text removed) |

All arms use the same embedding model (nomic-embed-text, 768-d, cosine). Flowcharts: [figures/figure-layer/](../figures/figure-layer/).

## Results

**Table 1.** General figure questions (38 questions, one gold paper each, full corpus).

| Metric | v2 | v2 + LLM descriptions |
|---|---|---|
| Hit@5 | 1.000 | 1.000 |
| MRR@10 | 0.844 | 0.869 (p = 0.28) |
| Topic F1@5 (10 queries) | 0.716 | 0.716 |

Trend questions are usually answerable from the Results text, so v2 is already at ceiling.

**Table 2.** Figure-only questions (33 questions whose answer appears only in a figure; full-text search confirmed the body text does not state it). AnsHit@10 = a chunk from the gold paper that contains all answer keywords is in the top 10.

| Arm | All (33) | Exact (17) | Approximate (16) |
|---|---|---|---|
| v2 | 0.091 | 0.000 | 0.188 |
| v3 | 0.091 | 0.000 | 0.188 |
| v3-full | 0.455 | 0.471 | 0.438 |
| v2 + LLM descriptions | 0.455 | 0.529 | 0.375 |
| **Combined** | **0.667** | **0.765** | **0.562** |

Combined vs v3-full and vs v2 + LLM descriptions: +0.212 each (95% CI +0.09 to +0.36; Wilcoxon p = 0.008).

*Exact* answers can be read directly from the figure without estimating positions: numbers printed on the figure (P values, fitted equations, R², inset tables), significance letters, or categorical conclusions (which group is highest, direction of a trend). *Approximate* answers require reading a number from plot geometry (bar height, point position, peak time) and carry reading error.

**Table 3.** Misretrieval checks.

| Check | v2 + LLM descriptions | Combined |
|---|---|---|
| Known-item questions on other papers (98) that got worse | 0 | 0 |
| Figure/table chunk ranked first but from the wrong paper | 0 / 38 | 0 / 169 |
| Numbers in descriptions found in the PDF text or printed on the figure | 536 / 558 in text; remaining 22 printed on raster figures (spot-checked) | — |

**Table 4.** Accuracy of values read from plots (blind reading: the reader saw only the image and the task list).

| Comparison | n | Error |
|---|---|---|
| vs author-reported values | 55 | median relative error 0.45%; 50 within 5% |
| vs vector-derived values (one figure) | 24 | mean 0.25% of axis range (unmagnified first pass: 0.83%) |

The largest errors were small slopes among overlapping lines (47%, 29%).

## Findings
1. **v2 and v3 share a blind spot**: both drop captions and tables, so figure-only answers are almost never retrieved.
2. **Docling's picture description model (SmolVLM-256M) contributed little**: 14 of 95 detected pictures received any text, mostly inaccurate. v3-full gains came from captions, OCR text and tables.
3. **LLM descriptions and OCR are complementary**: descriptions capture trends and group conclusions; OCR captures verbatim statistics. Combining them gave the best result.
4. **No misretrieval** was observed after adding figure passages.
5. **Values read from plots are accurate enough for trend comparison**; author-reported values should be preferred for slopes.

## Problems found and fixed during the pilot
- Docling occasionally attached a caption to the wrong picture.
- "Partial success" conversions were initially counted as successes.
- GPU memory allocation errors on the 8 GB device required retries and page-range conversion.
- The first numeric-accuracy round was contaminated (readers had seen author-reported values); it was discarded and repeated blind.

## Limitations
- 10 papers, one topic; questions were written by an LLM without human review.
- Answer-level scoring uses exact keyword matching, which underestimates all arms; approximate questions may be overestimated when OCR captures axis tick numbers.
- Numeric comparisons concentrate on a few papers and on easier-to-read points.
- Answer quality of downstream agents was not evaluated (next stage).

## AI use
Figure descriptions, question sets and blind readings were produced by Claude Opus 5.5 sub-agents under the rules above; all numbers in descriptions are author-reported and labelled. Generated descriptions, extracted values and figure images are not published.

## References
[1] Zhang, J. et al. (2021). *Scientia Horticulturae* 283, 110089. doi:10.1016/j.scienta.2021.110089
[2] Ding, J. et al. (2022). *Scientia Horticulturae* 293, 110736. doi:10.1016/j.scienta.2021.110736
[3] Amitrano, C. et al. (2021). *Agronomy* 11, 1396. doi:10.3390/agronomy11071396
[4] Inoue, T. et al. (2021). *Frontiers in Plant Science* 12, 646144. doi:10.3389/fpls.2021.646144
[5] Broughton, K.J. & Conaty, W.C. (2022). *Frontiers in Plant Science* 13, 893994. doi:10.3389/fpls.2022.893994
[6] Devi, M.J. & Reddy, V.R. (2018). *Frontiers in Plant Science* 9, 1572. doi:10.3389/fpls.2018.01572
[7] Medina, S. et al. (2019). *Frontiers in Plant Science* 9, 1994. doi:10.3389/fpls.2018.01994
[8] Li, Y. et al. (2018). *Sustainability* 10, 4063. doi:10.3390/su10114063
[9] Barron-Gafford, G.A. et al. (2007). *New Phytologist* 174, 614–625. doi:10.1111/j.1469-8137.2007.02035.x
[10] Eze, C. et al. (2024). *Photosynthetica* 62, 318–325. doi:10.32615/ps.2024.034

---

## 繁體中文

> 對應 Issue：[#6](https://github.com/kylecat/listen-to-your-rag/issues/6)（圖說）、[#7](https://github.com/kylecat/listen-to-your-rag/issues/7)（表格）、[#8](https://github.com/kylecat/listen-to-your-rag/issues/8)（圖片描述）。方法：[design/06-figure-layer.zh-TW.md](../design/06-figure-layer.zh-TW.md)。狀態：**試驗，數字為暫定**。

### 研究問題
1. 把圖轉成文字後，只出現在圖上的資訊能不能被檢索到？
2. 四種流程的效果差多少：v2、v3（Docling）、v3-full（Docling 開啟圖表模型）、v2＋LLM 圖表描述？
3. 加入圖表段落會不會造成誤判？
4. 從圖上讀回的數值準不準？

### 樣本
10 篇關於飽差（VPD）、蒸散與氣孔導度的實驗論文：43 張圖（數據圖 38 張；向量圖 9、點陣圖 34）、31 個表。文獻見英文版參考文獻 [1]–[10]。

### 組別
| 組別 | 正文 | 圖表層 |
|---|---|---|
| v2 | 規則式擷取（線上版） | 無；圖說和表格被丟棄 |
| v3 | Docling，圖表模型關閉 | 無 |
| v3-full | Docling，開啟 OCR、表格結構、圖片分類、SmolVLM-256M | 每張圖：圖說＋SmolVLM 描述＋圖上 OCR 文字；每個表：Markdown |
| v2＋LLM 描述 | v2 | 每張圖一段學術描述（Claude Opus 5.5），只含作者報告的數值 |
| 合併組 | v2 | LLM 描述＋Docling 的圖說、OCR 文字、表格（去掉 SmolVLM 描述） |

所有組別使用相同的向量模型（nomic-embed-text，768 維，cosine）。流程圖見 [figures/figure-layer/](../figures/figure-layer/)。

### 結果
**表 1.** 一般圖表題（38 題）：v2 與 v2＋LLM 描述的 Hit@5 都是 1.000；MRR@10 0.844 → 0.869（p = 0.28）；主題查詢 F1@5 都是 0.716。趨勢類問題靠 Results 的文字就找得到，有天花板效應。

**表 2.** 答案只在圖上的題目（33 題，以全文搜尋確認正文沒有寫）。AnsHit@10＝前 10 段中，有來自正確論文、且包含全部答案關鍵詞的段落。

| 組別 | 全部（33） | 精確值（17） | 約略值（16） |
|---|---|---|---|
| v2 | 0.091 | 0.000 | 0.188 |
| v3 | 0.091 | 0.000 | 0.188 |
| v3-full | 0.455 | 0.471 | 0.438 |
| v2＋LLM 描述 | 0.455 | 0.529 | 0.375 |
| **合併組** | **0.667** | **0.765** | **0.562** |

合併組相對於 v3-full、相對於 v2＋LLM 描述：皆為 +0.212（95% CI +0.09～+0.36；Wilcoxon p = 0.008）。

**精確值**：答案可以直接從圖上判讀，不需要估計座標位置。包括作者印在圖上的數字（P 值、迴歸方程式、R²、圖內小表格）、顯著性字母，或「哪一組最高」「趨勢方向」這類結論。**約略值**：答案必須從圖形位置讀出數字（長條高度、資料點位置、峰值時間），本身帶有讀數誤差。

**表 3.** 誤判檢查：評測 1 中其他論文的 98 題，0 題變差；圖表段落排第 1 名卻屬於別篇論文，0 次（v2＋LLM 描述 0／38、合併組 0／169）；描述中的數字，558 個中有 536 個可在 PDF 文字找到，其餘 22 個印在點陣圖上（抽查正確）。

**表 4.** 圖上讀數的準確度（盲測：讀數者只能看到圖和任務清單）：對照作者報告值，55 點的相對誤差中位數為 0.45%，其中 50 點在 5% 以內；對照向量圖反推值（1 張圖、24 點），平均誤差為座標軸範圍的 0.25%（未放大的第一輪目測為 0.83%）。誤差最大的是多條線重疊時的小斜率（47%、29%）。

### 主要發現
1. **v2 與 v3 有共同的盲點**：兩者都丟掉圖說和表格，幾乎取不到只在圖上的答案。
2. **Docling 的圖片描述模型（SmolVLM-256M）幾乎沒有幫助**：偵測到的 95 張圖中，只有 14 張產生文字，而且多數不正確。v3-full 的進步來自圖說、OCR 文字和表格。
3. **LLM 描述與 OCR 互補**：描述擅長趨勢和分組結論，OCR 擅長逐字的統計值；兩者合併效果最好。
4. 加入圖表段落後**沒有觀察到誤判**。
5. **圖上讀數足以用來比較趨勢**；斜率應優先引用作者報告值。

### 試驗中發現並修正的問題
- Docling 偶爾會把圖說配到錯的圖。
- 「部分成功」的轉換一開始被當成成功。
- 在 8 GB 的裝置上會發生 GPU 記憶體配置錯誤，需要重試或分頁轉換。
- 第一輪數值準確度測試被污染（讀數者事先看過作者報告值），已作廢並重新盲測。

### 限制
- 只有 10 篇、單一主題；題目由 LLM 撰寫，沒有人工檢核。
- 答案層級採關鍵詞完全比對，會低估所有組別；約略值題可能因 OCR 讀到座標軸刻度而高估。
- 數值比對集中在少數幾篇，而且多半是比較容易讀的點。
- 尚未評估下游 agent 的回答品質（屬於下一階段）。

### AI 使用
圖表描述、題目與盲測讀數由 Claude Opus 5.5 子 agent 依上述規則產生；描述中的數字皆為作者報告值並附出處。AI 產生的描述、讀出的數值與論文圖片都不公開。
