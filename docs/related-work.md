# Related work / 學術研究與工具查證

> Last verified: 2026-10-21. Each entry was checked against its primary source (arXiv, ACL Anthology, CVF Open Access) unless noted.
> 查證日期：2026-10-21。每一條都對照過原始出處（arXiv、ACL Anthology、CVF Open Access），另有註明者除外。

## Summary / 結論

- **The approach is not new.** Layout-aware extraction of scientific PDFs and structure-aware chunking for RAG are established practice with clear prior work.
  **這套做法不是新發現**：學術 PDF 的版面感知擷取、依文件結構切塊，都有明確的前人研究與成熟工具。
- **Rule-based parsers are known to be weak on scientific papers.** Our pipeline is rule-based, so learning-based baselines (GROBID, Docling, Nougat) should be part of any comparison.
  **規則式解析在科學論文上普遍吃虧**；我們的流程是規則式的，評測時應納入學習式工具當比較組。
- **We found no formal study using text-to-speech read-aloud as a quality audit of a RAG corpus.** Only PDF reader guidance (listening helps catch missing or repeated words and column-order errors) and TTS for mathematical documents. To claim this as a contribution, flagged issues and before/after retrieval effects need to be logged systematically.
  **查不到「用朗讀稽核 RAG 語料」的正式研究**，只有 PDF 朗讀軟體的校對建議與數學文件 TTS。要主張這是貢獻，需要系統化記錄回報的問題類型與修正前後的檢索差異。
- **Figures and tables are the main remaining gap.** Our current pipeline drops captions and table remnants, yet key quantitative results often sit in tables.
  **圖表是目前最大的缺口**：現行流程濾掉了圖表說明與表格，但論文的關鍵數據常在表格裡。

## 1. Layout-aware extraction / 版面感知擷取與閱讀順序

| Work | Source | Key point / 重點 |
|---|---|---|
| **S2ORC** — Lo et al., ACL 2020 | [ACL Anthology 2020.acl-main.447](https://aclanthology.org/2020.acl-main.447) | Uses GROBID to extract section-organised paragraphs and figure/table captions; structured full text for 8.1M open-access papers. 用 GROBID 抽出依章節組織的全文。 |
| **Nougat** — Blecher et al., 2023 | [arXiv:2308.13418](https://arxiv.org/abs/2308.13418) | Page image → structured Markdown including equations and tables; notes that PDFs lose most semantic structure. 頁面影像直接轉結構化 Markdown。 |
| **Docling** — IBM, 2024 | [arXiv:2408.09869](https://arxiv.org/abs/2408.09869) | Layout analysis (DocLayNet) + table structure recognition (TableFormer); JSON/Markdown output. 版面分析＋表格結構辨識。 |
| **PDF parser comparison** — Adhikari & Agarwal, 2024 | [arXiv:2410.09871](https://arxiv.org/abs/2410.09871) | 10 parsers across 6 document categories (DocLayNet); **all rule-based parsers struggled on scientific and patent documents**; learning-based tools (Nougat) did better. 規則式工具在科學論文上普遍表現不佳。 |
| **OmniDocBench** — Ouyang et al., CVPR 2025 | [CVF Open Access](https://openaccess.thecvf.com/content/CVPR2025/html/Ouyang_OmniDocBench_Benchmarking_Diverse_PDF_Document_Parsing_with_Comprehensive_Annotations_CVPR_2025_paper.html) | End-to-end parsing benchmark over 9 document sources; VLMs generalise better to unusual layouts, pipeline tools handle merged-cell tables better. 文件解析評測基準。 |

## 2. Chunking for RAG / RAG 切塊

| Work | Source | Key point / 重點 |
|---|---|---|
| **Element-based chunking** — Jimeno Yepes et al., 2024 | [arXiv:2402.05131](https://arxiv.org/abs/2402.05131) | Chunking by document elements (titles, paragraphs, tables) instead of fixed size improves RAG on financial reports. 依文件元素切塊優於固定長度。 |
| **Dense X Retrieval** — Chen et al., EMNLP 2024 | [arXiv:2312.06648](https://arxiv.org/abs/2312.06648) | Retrieval granularity (passage / sentence / proposition) significantly affects retrieval and downstream QA. 檢索單位粒度影響檢索品質。 |
| **Parsing + chunking for financial QA**, 2026 | [arXiv:2604.12047](https://arxiv.org/abs/2604.12047) | Compares parsers and chunking strategies within one framework. 解析器與切塊放在同一框架比較。 |
| **PDF-to-Markdown frameworks for RAG**, 2026 | [arXiv:2604.04948](https://arxiv.org/abs/2604.04948) | Docling, MinerU, Marker, DeepSeek OCR scored by downstream QA accuracy (Portuguese administrative documents). 以問答準確率評估轉換框架。 |

## 3. Evaluation methods / 評測方法

| Work | Source | Key point / 重點 |
|---|---|---|
| **LLM relevance labelling** — Thomas et al., SIGIR 2024 | [arXiv:2309.10621](https://arxiv.org/abs/2309.10621) | LLM relevance labels can match human labellers, but prompt wording and paraphrases change accuracy → we pair LLM judgments with a human-judged subset and report Cohen's κ. LLM 可判斷相關性，但需人工抽查。 |
| **Pooled relevance judgments** (TREC practice) | Voorhees & Harman (eds.), *TREC: Experiment and Evaluation in Information Retrieval*, MIT Press, 2005 *(not re-verified online)* | Pool the top-k results of all compared systems and judge relevance blind to the system. 合併各系統前幾名後盲評。 |

## 4. Read-aloud as a corpus audit / 朗讀稽核

| Source | Note |
|---|---|
| PDF text-to-speech reader guidance (e.g. [UPDF](https://updf.com/read-pdf/pdf-reader-with-text-to-speech/)) | Vendor guidance: listening helps notice repeated or missing words, awkward sentences and column-order errors. *Practical advice, not a validated method.* |
| **MathReader** — 2025 | [arXiv:2501.07088](https://arxiv.org/abs/2501.07088) — TTS for mathematical documents; converts LaTeX formulas to spoken English. 數學文件 TTS。 |

No peer-reviewed work was found that uses read-aloud of the indexed text as a systematic quality audit of a RAG corpus (search date 2026-10-21).

## 5. Figures and tables (next step) / 圖表（下一步）

| Work | Source | Key point / 重點 |
|---|---|---|
| **PDFFigures 2.0** — Clark & Divvala, JCDL 2016 | [AllenAI pdffigures2](https://github.com/allenai/pdffigures2) | Extracts captioned figures/tables, captions and bounding boxes from scholarly PDFs. 擷取圖表、說明與位置。 |
| **PubTables-1M / Table Transformer** — Smock et al., 2021–2022 | [arXiv:2110.00061](https://arxiv.org/abs/2110.00061) | ~1M tables from scientific articles; DETR models for table detection and structure recognition. 表格偵測與結構辨識。 |
| **ColPali** (visual late-interaction page retrieval) | [overview](https://medium.com/@intuitivedl/rag-with-colpali-everything-you-need-to-know-46b7bd50901b) *(secondary source)* | Retrieves pages from images without OCR; can find figures and charts; ~1,000 patch vectors per page. 以頁面影像檢索。 |
| **Multimodal RAG in the biomedical domain**, 2025 | [arXiv:2512.16802](https://arxiv.org/abs/2512.16802) | 120 questions from 25 papers incl. figure/table questions: multimodal 0.808, text 0.782, ColPali 0.745 (GPT-4o); differences small and model-dependent. 多模態優勢不大且依模型而定。 |

### Planned layers / 規劃
| Layer | Approach | Cost |
|---|---|---|
| L1 | Keep figure/table captions as separate chunks with page numbers. 保留圖表說明為獨立段落。 | Low |
| L2 | Convert detected tables to Markdown chunks (e.g. Docling / TableFormer). 表格轉 Markdown。 | Medium |
| L3 | Generate labelled descriptions of figure images with a vision model. 以視覺模型產生圖片描述（標示為生成內容）。 | High |

Each layer will be evaluated with the same benchmark, extended with figure/table questions.
