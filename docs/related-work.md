# Related work / 學術研究與工具查證

> Last verified: 2026-10-21. Each entry was checked against its primary source (arXiv, ACL Anthology, CVF Open Access) unless noted.
> Citations use numbered references [n]; full entries are listed under **References** at the end.
> 查證日期：2026-10-21。文中以編號 [n] 引用，完整書目列於文末**參考文獻**。每一條都對照過原始出處（arXiv、ACL Anthology、CVF Open Access），另有註明者除外。

## Summary / 結論

- **The approach is not new.** Layout-aware extraction of scientific PDFs and structure-aware chunking for RAG are established practice with clear prior work [1]–[3], [6], [7].
  **這套做法不是新發現**：學術 PDF 的版面感知擷取、依文件結構切塊，都有明確的前人研究與成熟工具 [1]–[3], [6], [7]。
- **Rule-based parsers are known to be weak on scientific papers.** Our pipeline is rule-based, so learning-based baselines (GROBID, Docling, Nougat) should be part of any comparison [4].
  **規則式解析在科學論文上普遍吃虧**；我們的流程是規則式的，評測時應納入學習式工具當比較組 [4]。
- **We found no formal study using text-to-speech read-aloud as a quality audit of a RAG corpus.** Only PDF reader guidance (listening helps catch missing or repeated words and awkward sentences) and TTS for mathematical documents [12], [13]. To claim this as a contribution, flagged issues and before/after retrieval effects need to be logged systematically.
  **查不到「用朗讀稽核 RAG 語料」的正式研究**，只有 PDF 朗讀軟體的校對建議與數學文件 TTS [12], [13]。要主張這是貢獻，需要系統化記錄回報的問題類型與修正前後的檢索差異。
- **Figures and tables are the main remaining gap.** Our current pipeline drops captions and table remnants, yet key quantitative results often sit in tables [14]–[17].
  **圖表是目前最大的缺口**：現行流程濾掉了圖表說明與表格，但論文的關鍵數據常在表格裡 [14]–[17]。

## 1. Layout-aware extraction / 版面感知擷取與閱讀順序

Scientific PDFs encode positioned glyphs rather than paragraphs and sections, so multi-column layouts, running headers, equations and tables corrupt text obtained by naive extraction. Prior work addresses this problem along three lines:

- **Structure recovery at corpus scale.** Lo et al. [1] used GROBID to build S2ORC, providing section-structured full text, figure/table captions and inline citation links for 8.1 million open-access papers.
- **Learning-based document conversion.** Blecher et al. [2] convert page images directly into structured markup, including equations and tables, arguing that much of a PDF's semantic structure is otherwise lost; Auer et al. [3] combine a layout-analysis model with a table-structure model (TableFormer) and export JSON or Markdown.
- **Comparative evaluation of parsers.** Adhikari and Agarwal [4] benchmarked ten parsing tools on six document categories and found that all rule-based tools struggled on scientific and patent documents, whereas the learning-based Nougat performed better; Ouyang et al. [5] reported that vision-language models generalise better to unusual layouts while pipeline tools handle merged-cell tables better.

*Implications for this work.*
- The failures observed in our v1 index (interleaved columns, missing section labels) are those predicted by [4].
- Our v2 extractor is rule-based and therefore belongs to the class that [4] found weakest on scientific documents; a learning-based baseline such as GROBID or Docling is required in our evaluation ([#5](https://github.com/kylecat/listen-to-your-rag/issues/5)).
- Because parser quality depends on document type [4], [5], conclusions must be drawn from measurements on our own corpus.

科學論文 PDF 儲存的是帶座標的字元，而非段落與章節，因此多欄排版、頁首頁尾、公式與表格會使直接擷取的文字失真。既有研究從三個方向處理此問題：

- **大規模還原文件結構。** Lo 等人 [1] 以 GROBID 建立 S2ORC，為 810 萬篇開放取用論文提供依章節組織的全文、圖表說明與內文引用連結。
- **學習式文件轉換。** Blecher 等人 [2] 將頁面影像直接轉為含公式與表格的結構化標記，並指出 PDF 原有的語意結構大多已流失；Auer 等人 [3] 結合版面分析模型與表格結構模型（TableFormer），輸出 JSON 或 Markdown。
- **解析工具的比較評估。** Adhikari 與 Agarwal [4] 以六類文件評測十種解析工具，發現所有規則式工具在科學論文與專利上表現皆不佳，而學習式的 Nougat 表現較好；Ouyang 等人 [5] 則指出視覺語言模型對罕見版型的泛化較佳，傳統管線工具處理合併儲存格表格較佳。

*對本研究的意涵：*
- v1 索引的問題（左右欄混雜、缺少章節標籤）正是 [4] 所預期的失誤類型。
- v2 擷取器屬於規則式方法，即 [4] 認為在科學論文上最弱的一類；因此評測必須納入 GROBID 或 Docling 等學習式比較組。
- 解析品質取決於文件類型 [4], [5]，結論須以本研究語料的實測為準。

| Work | Source | Key point / 重點 |
|---|---|---|
| [1] **S2ORC** — Lo et al., ACL 2020 | [ACL Anthology 2020.acl-main.447](https://aclanthology.org/2020.acl-main.447) | Uses GROBID to extract section-organised paragraphs and figure/table captions; structured full text for 8.1M open-access papers. 用 GROBID 抽出依章節組織的全文。 |
| [2] **Nougat** — Blecher et al., 2023 | [arXiv:2308.13418](https://arxiv.org/abs/2308.13418) | Page image → structured Markdown including equations and tables; notes that PDFs lose most semantic structure. 頁面影像直接轉結構化 Markdown。 |
| [3] **Docling** — Auer et al. (IBM), 2024 | [arXiv:2408.09869](https://arxiv.org/abs/2408.09869) | Layout analysis (DocLayNet) + table structure recognition (TableFormer); JSON/Markdown output. 版面分析＋表格結構辨識。 |
| [4] **PDF parser comparison** — Adhikari & Agarwal, 2024 | [arXiv:2410.09871](https://arxiv.org/abs/2410.09871) | 10 parsers across 6 document categories (DocLayNet); **all rule-based parsers struggled on scientific and patent documents**; learning-based tools (Nougat) did better. 規則式工具在科學論文上普遍表現不佳。 |
| [5] **OmniDocBench** — Ouyang et al., CVPR 2025 | [CVF Open Access](https://openaccess.thecvf.com/content/CVPR2025/html/Ouyang_OmniDocBench_Benchmarking_Diverse_PDF_Document_Parsing_with_Comprehensive_Annotations_CVPR_2025_paper.html) | End-to-end parsing benchmark over 9 document sources; VLMs generalise better to unusual layouts, pipeline tools handle merged-cell tables better. 文件解析評測基準。 |

## 2. Chunking for RAG / RAG 切塊

After extraction, the segmentation of text into retrieval units determines what a retriever can find. The literature identifies segmentation as a first-order design variable:

- **Structure-aware units.** Jimeno Yepes et al. [6] chunked financial reports by document element (title, paragraph, table) rather than by fixed length and reported improved retrieval-augmented generation results.
- **Retrieval granularity.** Chen et al. [7] showed that indexing propositions instead of passages improves dense retrieval, with the largest advantage at small word budgets.
- **Joint evaluation of parsing and chunking.** El Bachyr et al. [8] and Marques dos Santos et al. [9] argue that parsers and chunking strategies should be compared within a single framework and judged by downstream question-answering accuracy; [9] compared four conversion frameworks across 21 pipeline configurations.

*Implications for this work.*
- v2 replaces fixed 500-word chunks with section-labelled, sentence-aligned chunks while keeping the embedding model fixed, so retrieval differences can be attributed to the text layer.
- The low overlap between v1 and v2 top-5 results (1.8 of 5 papers) is consistent with [7]: changing the unit changes the ranking. Improvement must therefore be demonstrated by evaluation ([#3](https://github.com/kylecat/listen-to-your-rag/issues/3), [#4](https://github.com/kylecat/listen-to-your-rag/issues/4)), not assumed.

文字擷取之後，如何切分為檢索單位決定了檢索器能找到什麼。文獻將切分方式視為一級設計變因：

- **依結構切分。** Jimeno Yepes 等人 [6] 將財報依文件元素（標題、段落、表格）而非固定長度切塊，報告檢索增強生成的結果有所改善。
- **檢索粒度。** Chen 等人 [7] 證實以命題而非段落建立索引可改善密集檢索，且在字數預算較小時優勢最大。
- **解析與切塊的聯合評估。** El Bachyr 等人 [8] 與 Marques dos Santos 等人 [9] 主張應在同一框架下比較解析器與切塊策略，並以下游問答準確率評判；[9] 比較了四種轉換框架共 21 種管線組態。

*對本研究的意涵：*
- v2 以「標有章節、對齊句界」的切塊取代固定 500 字切塊，並固定向量模型，使檢索差異可歸因於文字層。
- v1 與 v2 前 5 名僅重疊 1.8 篇，與 [7] 的觀察一致：檢索單位改變即改變排名。因此改善與否必須以評測證明，不能預設。

| Work | Source | Key point / 重點 |
|---|---|---|
| [6] **Element-based chunking** — Jimeno Yepes et al., 2024 | [arXiv:2402.05131](https://arxiv.org/abs/2402.05131) | Chunking by document elements (titles, paragraphs, tables) instead of fixed size improves RAG on financial reports. 依文件元素切塊優於固定長度。 |
| [7] **Dense X Retrieval** — Chen et al., EMNLP 2024 | [arXiv:2312.06648](https://arxiv.org/abs/2312.06648) | Retrieval granularity (passage / sentence / proposition) significantly affects retrieval and downstream QA. 檢索單位粒度影響檢索品質。 |
| [8] **Parsing + chunking for financial QA** — El Bachyr et al., 2026 | [arXiv:2604.12047](https://arxiv.org/abs/2604.12047) | Compares parsers and chunking strategies within one framework. 解析器與切塊放在同一框架比較。 |
| [9] **PDF-to-Markdown frameworks for RAG** — Marques dos Santos et al., 2026 | [arXiv:2604.04948](https://arxiv.org/abs/2604.04948) | Docling, MinerU, Marker, DeepSeek OCR scored by downstream QA accuracy (Portuguese administrative documents). 以問答準確率評估轉換框架。 |

## 3. Evaluation methods / 評測方法

Retrieval effectiveness is measured against relevance judgments, whose cost has motivated two established practices:

- **Pooling.** In TREC practice [11], the top-ranked results of all compared systems are merged into a pool and judged without revealing which system retrieved them.
- **LLM relevance labelling.** Thomas et al. [10] showed that large language models can produce relevance labels with accuracy comparable to human labellers and can identify the best-performing systems, but that prompt changes and even paraphrases alter labelling accuracy.

*Implications for this work.*
- Our topic-query evaluation pools the top-10 papers from each index and judges them blind to the source system [11].
- An LLM judges all pooled pairs, and agreement with a human-judged subset is reported as Cohen's κ, following the caution in [10] ([#4](https://github.com/kylecat/listen-to-your-rag/issues/4)).
- A separate known-item set provides a judgment-free check ([#3](https://github.com/kylecat/listen-to-your-rag/issues/3)).

檢索效能須以相關性判斷衡量；判斷成本高，因而形成兩種既有做法：

- **候選池法。** TREC 的做法 [11] 是將所有受比較系統的前幾名結果合併為候選池，並在不揭露來源系統的情況下判斷。
- **以 LLM 標註相關性。** Thomas 等人 [10] 證實大型語言模型產生的相關性標註，準確度可與人工標註者相當，並能辨識表現最佳的系統；但提示詞的修改甚至改寫措辭，都會影響標註準確度。

*對本研究的意涵：*
- 主題查詢評測將兩個索引各自的前 10 篇合併為候選池，並在隱藏來源的情況下判斷 [11]。
- 由 LLM 判斷全部候選，並依 [10] 的提醒，以人工抽評子集計算 Cohen's κ 報告一致性。
- 另以已知答案查詢提供不需相關性判斷的檢核。

| Work | Source | Key point / 重點 |
|---|---|---|
| [10] **LLM relevance labelling** — Thomas et al., SIGIR 2024 | [arXiv:2309.10621](https://arxiv.org/abs/2309.10621) | LLM relevance labels can match human labellers, but prompt wording and paraphrases change accuracy → we pair LLM judgments with a human-judged subset and report Cohen's κ. LLM 可判斷相關性，但需人工抽查。 |
| [11] **Pooled relevance judgments** (TREC practice) | Voorhees & Harman (eds.), *TREC: Experiment and Evaluation in Information Retrieval*, MIT Press, 2005 *(not re-verified online)* | Pool the top-k results of all compared systems and judge relevance blind to the system. 合併各系統前幾名後盲評。 |

## 4. Read-aloud as a corpus audit / 朗讀稽核

Listening to text is a recognised proofreading aid, and speech synthesis for technical documents is an active research topic. However, we did not identify peer-reviewed work that uses read-aloud of an indexed RAG corpus as a systematic quality audit:

- **Proofreading by listening.** Vendor guidance for PDF text-to-speech readers [12] recommends listening to notice repeated or missing words and awkward sentences; this is practical advice rather than a validated method.
- **Speech for technical documents.** Hyeon et al. [13] convert OCR output for mathematical documents into spoken English, illustrating that technical notation requires an explicit spoken rewrite.

*Implications for this work.*
- Because the read-aloud tool and the index share one extraction module, the listener hears exactly the indexed text; our speakable-rewrite rules (units, statistics, abbreviations) parallel the rewrite needed in [13].
- To move from anecdote to evidence, every listener flag is logged by category and the retrieval effect of each resulting fix is measured ([#10](https://github.com/kylecat/listen-to-your-rag/issues/10)).
- This is the only element of the project that may be novel; we do not claim it as a contribution until the log supports it.

以聽讀校對文字是公認的校對輔助方式，技術文件的語音合成也是活躍的研究主題；然而，我們未找到將「朗讀已索引的 RAG 語料」作為系統化品質稽核的同儕審查研究：

- **以聽讀校對。** PDF 朗讀軟體的廠商建議 [12] 指出，聽讀有助於發現重複或遺漏的字詞與不通順的句子；此為實務建議，並非經驗證的方法。
- **技術文件的語音化。** Hyeon 等人 [13] 將數學文件的 OCR 輸出轉為英文口語念法，顯示技術符號需要明確的念法轉換。

*對本研究的意涵：*
- 朗讀工具與索引共用同一個擷取模組，聆聽者聽到的正是索引中的文字；本研究的念法轉換規則（單位、統計、縮寫）與 [13] 所需的轉換相當。
- 為使其由個案觀察成為證據，每一筆聆聽回報皆依類別記錄，並量測每項修正對檢索的影響。
- 這是本專案中唯一可能具新穎性的部分；在紀錄足以支持之前，不主張其為貢獻。

| Source | Note |
|---|---|
| [12] PDF text-to-speech reader guidance (e.g. [UPDF](https://updf.com/read-pdf/pdf-reader-with-text-to-speech/)) | Vendor guidance: listening helps notice repeated or missing words and awkward sentences. *Practical advice, not a validated method.* |
| [13] **MathReader** — Hyeon et al., 2025 | [arXiv:2501.07088](https://arxiv.org/abs/2501.07088) — TTS for mathematical documents; converts LaTeX formulas to spoken English. 數學文件 TTS。 |

No peer-reviewed work was found that uses read-aloud of the indexed text as a systematic quality audit of a RAG corpus (search date 2026-10-21).

## 5. Figures and tables (next step) / 圖表（下一步）

Quantitative results in scientific papers are frequently reported in tables and figures, which text-only pipelines discard or garble. Existing work offers both components and a first estimate of their value:

- **Figure and table extraction.** Clark and Divvala [14] extract captioned figures and tables together with their captions and bounding boxes from scholarly PDFs.
- **Table structure recognition.** Smock et al. [15] released PubTables-1M, nearly one million tables from scientific articles, with detection and structure-recognition models (Table Transformer).
- **OCR-free page retrieval.** Faysse et al. [16] retrieve document pages directly from page-image embeddings produced by a vision-language model, which can surface figures and charts that text extraction misses.
- **Value for question answering.** In a glycobiology case study, Kocbek et al. [17] found multimodal RAG only slightly more accurate than text-based RAG (0.808 vs 0.782 with GPT-4o; ColPali 0.745), with results depending on the answering model.

*Implications for this work.*
- v2 currently removes captions and table remnants, which is the largest known gap in our pipeline (for example, yields reported only in a table).
- Given the modest gains reported in [17], we adopt an incremental plan: captions first, then tables, and figure descriptions only if evaluation shows a benefit ([#6](https://github.com/kylecat/listen-to-your-rag/issues/6)–[#8](https://github.com/kylecat/listen-to-your-rag/issues/8)).

科學論文的量化結果常以表格與圖呈現，而純文字流程會將其丟棄或弄亂。既有研究同時提供了可用的元件與其價值的初步估計：

- **圖表擷取。** Clark 與 Divvala [14] 從學術 PDF 中擷取有編號說明的圖與表，連同說明文字與位置框。
- **表格結構辨識。** Smock 等人 [15] 釋出 PubTables-1M（近百萬個科學論文表格），以及表格偵測與結構辨識模型（Table Transformer）。
- **免 OCR 的頁面檢索。** Faysse 等人 [16] 以視覺語言模型產生的頁面影像向量直接檢索文件頁面，可找到文字擷取遺漏的圖與圖表。
- **對問答的價值。** Kocbek 等人 [17] 在醣生物學案例研究中發現，多模態 RAG 僅略優於純文字 RAG（GPT-4o 下為 0.808 對 0.782；ColPali 為 0.745），且結果取決於回答所用的模型。

*對本研究的意涵：*
- v2 目前會移除圖表說明與表格殘片，這是流程中已知最大的缺口（例如產量數據僅出現在表格中）。
- 鑑於 [17] 報告的增益有限，採漸進計畫：先處理圖表說明，再處理表格，圖片描述待評測顯示有益時才進行。

| Work | Source | Key point / 重點 |
|---|---|---|
| [14] **PDFFigures 2.0** — Clark & Divvala, JCDL 2016 | [AllenAI pdffigures2](https://github.com/allenai/pdffigures2) | Extracts captioned figures/tables, captions and bounding boxes from scholarly PDFs. 擷取圖表、說明與位置。 |
| [15] **PubTables-1M / Table Transformer** — Smock et al., CVPR 2022 | [arXiv:2110.00061](https://arxiv.org/abs/2110.00061) | ~1M tables from scientific articles; DETR models for table detection and structure recognition. 表格偵測與結構辨識。 |
| [16] **ColPali** — Faysse et al., 2024 (visual late-interaction page retrieval) | [arXiv:2407.01449](https://arxiv.org/abs/2407.01449); practical [overview](https://medium.com/@intuitivedl/rag-with-colpali-everything-you-need-to-know-46b7bd50901b) *(secondary)* | Retrieves pages from images without OCR; can find figures and charts; ~1,000 patch vectors per page. 以頁面影像檢索。 |
| [17] **Multimodal RAG in the biomedical domain** — Kocbek et al., 2025 | [arXiv:2512.16802](https://arxiv.org/abs/2512.16802) | 120 questions from 25 papers incl. figure/table questions: multimodal 0.808, text 0.782, ColPali 0.745 (GPT-4o); differences small and model-dependent. 多模態優勢不大且依模型而定。 |

### Planned layers / 規劃
| Layer | Approach | Cost |
|---|---|---|
| L1 | Keep figure/table captions as separate chunks with page numbers. 保留圖表說明為獨立段落。 | Low |
| L2 | Convert detected tables to Markdown chunks (e.g. Docling / TableFormer). 表格轉 Markdown。 | Medium |
| L3 | Generate labelled descriptions of figure images with a vision model. 以視覺模型產生圖片描述（標示為生成內容）。 | High |

Each layer will be evaluated with the same benchmark, extended with figure/table questions.

## References / 參考文獻

Format: authors, year, title, venue, identifier. Bibliographic data checked against arXiv, Crossref, ACL Anthology or CVF Open Access on 2026-10-21 unless marked.
格式：作者、年份、題名、出處、識別碼；除另有標註外，書目資料於 2026-10-21 對照 arXiv、Crossref、ACL Anthology 或 CVF Open Access 查證。

1. Lo, K., Wang, L. L., Neumann, M., Kinney, R., & Weld, D. S. (2020). S2ORC: The Semantic Scholar Open Research Corpus. *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics*, 4969–4983. https://doi.org/10.18653/v1/2020.acl-main.447
2. Blecher, L., Cucurull, G., Scialom, T., & Stojnic, R. (2023). Nougat: Neural Optical Understanding for Academic Documents. *arXiv:2308.13418*. https://arxiv.org/abs/2308.13418
3. Auer, C., Lysak, M., Nassar, A., Dolfi, M., Livathinos, N., Vagenas, P., Berrospi Ramis, C., Omenetti, M., et al. (2024). Docling Technical Report. *arXiv:2408.09869*. https://arxiv.org/abs/2408.09869
4. Adhikari, N. S., & Agarwal, S. (2024). A Comparative Study of PDF Parsing Tools Across Diverse Document Categories. *arXiv:2410.09871*. https://arxiv.org/abs/2410.09871
5. Ouyang, L., et al. (2025). OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations. *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 24838–24848.
6. Jimeno Yepes, A., You, Y., Milczek, J., Laverde, S., & Li, R. (2024). Financial Report Chunking for Effective Retrieval Augmented Generation. *arXiv:2402.05131*. https://arxiv.org/abs/2402.05131
7. Chen, T., Wang, H., Chen, S., Yu, W., Ma, K., Zhao, X., Zhang, H., & Yu, D. (2024). Dense X Retrieval: What Retrieval Granularity Should We Use? *Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing (EMNLP)*, 15159–15177. (arXiv:2312.06648)
8. El Bachyr, O., Song, Y., Ezzini, S., Klein, J., Bissyandé, T. F., Zilali, A., Ble, U., & Goujon, A. (2026). Empirical Evaluation of PDF Parsing and Chunking for Financial Question Answering with RAG. *arXiv:2604.12047*. https://arxiv.org/abs/2604.12047
9. Marques dos Santos, J. G., Yang, R., Pereira, R. H., Sousa, A., Faria, B. M., Lopes Cardoso, H., Duarte, J., Reis, J. L., et al. (2026). From PDF to RAG-Ready: Evaluating Document Conversion Frameworks for Domain-Specific Question Answering. *Applied Sciences*, 16, 5069. (arXiv:2604.04948)
10. Thomas, P., Spielman, S., Craswell, N., & Mitra, B. (2024). Large Language Models Can Accurately Predict Searcher Preferences. *Proceedings of the 47th International ACM SIGIR Conference (SIGIR '24)*. https://doi.org/10.1145/3626772.3657707 (arXiv:2309.10621)
11. Voorhees, E. M., & Harman, D. K. (Eds.). (2005). *TREC: Experiment and Evaluation in Information Retrieval*. MIT Press. *(not re-verified online)*
12. UPDF. *PDF Reader with Text to Speech*. https://updf.com/read-pdf/pdf-reader-with-text-to-speech/ (accessed 2026-10-21; vendor guidance, not peer-reviewed)
13. Hyeon, S., Jung, K., Kim, N.-J., Ryu, H. G., & Do, J. (2025). MathReader: Text-to-Speech for Mathematical Documents. *arXiv:2501.07088*. https://arxiv.org/abs/2501.07088
14. Clark, C., & Divvala, S. (2016). PDFFigures 2.0: Mining Figures from Research Papers. *Proceedings of the 16th ACM/IEEE-CS Joint Conference on Digital Libraries (JCDL)*, 143–152. https://doi.org/10.1145/2910896.2910904
15. Smock, B., Pesala, R., & Abraham, R. (2022). PubTables-1M: Towards Comprehensive Table Extraction from Unstructured Documents. *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 4624–4632. https://doi.org/10.1109/CVPR52688.2022.00459
16. Faysse, M., Sibille, H., Wu, T., Omrani, B., Viaud, G., Hudelot, C., & Colombo, P. (2024). ColPali: Efficient Document Retrieval with Vision Language Models. *arXiv:2407.01449*. https://arxiv.org/abs/2407.01449
17. Kocbek, P., Frkatović-Hodžić, A., Lalić, D., Hui, V., Lauc, G., & Štiglic, G. (2025). Exploration of Augmentation Strategies in Multi-modal Retrieval-Augmented Generation for the Biomedical Domain: A Case Study Evaluating Question Answering in Glycobiology. *arXiv:2512.16802*. https://arxiv.org/abs/2512.16802
