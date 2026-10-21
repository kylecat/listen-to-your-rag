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

**Summary.** Scientific PDFs store positioned glyphs, not paragraphs and sections; multi-column layouts, running headers, equations and tables break naive text extraction. The work below recovers structure either with layout-aware pipelines (GROBID in S2ORC, Docling) or end-to-end vision models (Nougat), and benchmarks show the choice of parser matters most on scientific and patent documents.
**Contribution.** These studies establish that (a) section-structured full text can be extracted at scale, (b) learning-based tools outperform rule-based ones on scientific layouts, and (c) parser quality varies by document type, so it must be measured on the target corpus.
**Relevance to our experiment.** Our v1 index failed exactly where these papers predict (column interleaving, lost sections). Our v2 extractor is a **rule-based** member of this family, so the literature sets both its justification and its main risk: a learning-based baseline (GROBID or Docling) must be part of our evaluation ([#5](https://github.com/kylecat/listen-to-your-rag/issues/5)).

**摘要**：科學論文 PDF 存的是有座標的字元，不是段落與章節；多欄排版、頁首頁尾、公式和表格都會破壞直接擷取的文字。下列研究以版面感知流程（S2ORC 用的 GROBID、Docling）或端到端視覺模型（Nougat）還原結構；評測顯示，解析工具的選擇在科學論文與專利上影響最大。
**貢獻**：這些研究確立了（一）可以大規模擷取依章節組織的全文；（二）在科學論文版面上，學習式工具優於規則式工具；（三）解析品質會隨文件類型變化，必須在目標語料上實測。
**與本實驗的關係**：v1 索引出問題的地方（欄位混雜、章節遺失）正是這些研究預測的地方。v2 擷取器屬於其中的**規則式**做法，所以文獻同時提供了它的依據與主要風險：評測必須納入學習式工具（GROBID 或 Docling）當比較組。


| Work | Source | Key point / 重點 |
|---|---|---|
| **S2ORC** — Lo et al., ACL 2020 | [ACL Anthology 2020.acl-main.447](https://aclanthology.org/2020.acl-main.447) | Uses GROBID to extract section-organised paragraphs and figure/table captions; structured full text for 8.1M open-access papers. 用 GROBID 抽出依章節組織的全文。 |
| **Nougat** — Blecher et al., 2023 | [arXiv:2308.13418](https://arxiv.org/abs/2308.13418) | Page image → structured Markdown including equations and tables; notes that PDFs lose most semantic structure. 頁面影像直接轉結構化 Markdown。 |
| **Docling** — IBM, 2024 | [arXiv:2408.09869](https://arxiv.org/abs/2408.09869) | Layout analysis (DocLayNet) + table structure recognition (TableFormer); JSON/Markdown output. 版面分析＋表格結構辨識。 |
| **PDF parser comparison** — Adhikari & Agarwal, 2024 | [arXiv:2410.09871](https://arxiv.org/abs/2410.09871) | 10 parsers across 6 document categories (DocLayNet); **all rule-based parsers struggled on scientific and patent documents**; learning-based tools (Nougat) did better. 規則式工具在科學論文上普遍表現不佳。 |
| **OmniDocBench** — Ouyang et al., CVPR 2025 | [CVF Open Access](https://openaccess.thecvf.com/content/CVPR2025/html/Ouyang_OmniDocBench_Benchmarking_Diverse_PDF_Document_Parsing_with_Comprehensive_Annotations_CVPR_2025_paper.html) | End-to-end parsing benchmark over 9 document sources; VLMs generalise better to unusual layouts, pipeline tools handle merged-cell tables better. 文件解析評測基準。 |

## 2. Chunking for RAG / RAG 切塊

**Summary.** Once text is extracted, how it is cut into retrieval units changes what a retriever finds. Element-based chunking (titles, paragraphs, tables) outperformed fixed-size chunks on financial reports; at a fixed word budget, finer units (propositions) retrieved better than passages; recent studies argue that parsing and chunking must be compared together rather than in isolation.
**Contribution.** They show that retrieval unit and document structure are first-order design variables in RAG, not implementation details, and provide comparison protocols that judge them by downstream question-answering accuracy.
**Relevance to our experiment.** v2 moves from fixed 500-word cuts to **section-labelled, sentence-aligned** chunks while keeping the embedding model fixed, so any retrieval difference can be attributed to the text layer. These works also explain why our top-5 overlap between versions was low (1.8/5): changing the unit changes the ranking — which is why we evaluate rather than assume improvement.

**摘要**：文字擷取出來後，怎麼切成檢索單位會改變檢索結果。在財報上，依文件元素（標題、段落、表格）切塊優於固定長度；在相同字數預算下，較細的單位（命題）檢索效果優於段落；近期研究主張解析與切塊必須一起比較，而非分開評估。
**貢獻**：這些研究說明檢索單位與文件結構是 RAG 的一級設計變因、不是實作細節，並提供以下游問答準確率評估的比較方法。
**與本實驗的關係**：v2 從固定 500 字硬切改為**標有章節、對齊句界**的切塊，同時固定向量模型，使檢索差異可歸因於文字層。這些研究也說明了新舊版前 5 名重疊率偏低（1.8/5）的原因：檢索單位一變，排名就跟著變——因此我們以評測判斷優劣，不預設改善。


| Work | Source | Key point / 重點 |
|---|---|---|
| **Element-based chunking** — Jimeno Yepes et al., 2024 | [arXiv:2402.05131](https://arxiv.org/abs/2402.05131) | Chunking by document elements (titles, paragraphs, tables) instead of fixed size improves RAG on financial reports. 依文件元素切塊優於固定長度。 |
| **Dense X Retrieval** — Chen et al., EMNLP 2024 | [arXiv:2312.06648](https://arxiv.org/abs/2312.06648) | Retrieval granularity (passage / sentence / proposition) significantly affects retrieval and downstream QA. 檢索單位粒度影響檢索品質。 |
| **Parsing + chunking for financial QA**, 2026 | [arXiv:2604.12047](https://arxiv.org/abs/2604.12047) | Compares parsers and chunking strategies within one framework. 解析器與切塊放在同一框架比較。 |
| **PDF-to-Markdown frameworks for RAG**, 2026 | [arXiv:2604.04948](https://arxiv.org/abs/2604.04948) | Docling, MinerU, Marker, DeepSeek OCR scored by downstream QA accuracy (Portuguese administrative documents). 以問答準確率評估轉換框架。 |

## 3. Evaluation methods / 評測方法

**Summary.** Retrieval quality is measured against relevance judgments. TREC practice pools the top results of the systems being compared and judges them blind to the system; recent work shows LLMs can label relevance about as accurately as human assessors, but are sensitive to prompt wording.
**Contribution.** Pooling makes judging feasible for small teams; LLM labelling makes it scalable, provided agreement with humans is checked.
**Relevance to our experiment.** Our evaluation design follows both: pooled top-10 from v1, v2 (and a baseline) judged blind, with an LLM judge checked against a human-judged subset via Cohen's κ ([#4](https://github.com/kylecat/listen-to-your-rag/issues/4)); a separate known-item set gives an automatic check ([#3](https://github.com/kylecat/listen-to-your-rag/issues/3)).

**摘要**：檢索品質要對照相關性判斷來衡量。TREC 的做法是把各受比較系統的前幾名合併成候選池，在不知道來源系統的情況下判斷；近期研究顯示 LLM 標註相關性的準確度可接近人工，但對提示詞措辭敏感。
**貢獻**：候選池讓小團隊也做得到人工判斷；LLM 標註讓判斷可以擴大規模，前提是要檢查與人工的一致性。
**與本實驗的關係**：我們的評測同時採用兩者：v1、v2（及比較組）的前 10 名合併後盲評，由 LLM 判斷並以人工抽評的 Cohen's κ 檢核；另以已知答案查詢做自動檢查。


| Work | Source | Key point / 重點 |
|---|---|---|
| **LLM relevance labelling** — Thomas et al., SIGIR 2024 | [arXiv:2309.10621](https://arxiv.org/abs/2309.10621) | LLM relevance labels can match human labellers, but prompt wording and paraphrases change accuracy → we pair LLM judgments with a human-judged subset and report Cohen's κ. LLM 可判斷相關性，但需人工抽查。 |
| **Pooled relevance judgments** (TREC practice) | Voorhees & Harman (eds.), *TREC: Experiment and Evaluation in Information Retrieval*, MIT Press, 2005 *(not re-verified online)* | Pool the top-k results of all compared systems and judge relevance blind to the system. 合併各系統前幾名後盲評。 |

## 4. Read-aloud as a corpus audit / 朗讀稽核

**Summary.** Listening to text is an established proofreading aid — it exposes missing or repeated words, awkward sentences and wrong reading order — and TTS for technical material (e.g. mathematical documents) is an active topic. We found no peer-reviewed work that uses read-aloud of an **indexed RAG corpus** as a systematic quality audit.
**Contribution.** The sources below are practical guidance and adjacent research, not evidence that the audit works; they motivate the idea and point to the failure types listening can reveal.
**Relevance to our experiment.** Because our read-aloud tool and our index share one extraction module, what is heard is what is indexed. To turn this from anecdote into evidence we log every flag by category and measure the retrieval effect of each resulting fix ([#10](https://github.com/kylecat/listen-to-your-rag/issues/10)). This is the one element of the project that may be new; we will not claim it until the log supports it.

**摘要**：以聽讀校對文字是既有的做法——能聽出漏字、重複字、不通順的句子和錯誤的閱讀順序；技術文件（例如數學文件）的 TTS 也是研究主題。但我們找不到任何同儕審查研究，把「朗讀**已索引的 RAG 語料**」當成系統化的品質稽核。
**貢獻**：下列來源是實務建議與鄰近研究，不是「稽核有效」的證據；它們提供了這個想法的動機，並指出聽讀能抓到的錯誤類型。
**與本實驗的關係**：我們的朗讀工具與索引共用同一個擷取模組，所以聽到的就是索引裡的內容。為了讓它從個案變成證據，我們依類別記錄每一次回報，並量測每項修正對檢索的影響。這可能是本專案唯一的新元素；在紀錄足以支持之前，我們不會主張它是貢獻。


| Source | Note |
|---|---|
| PDF text-to-speech reader guidance (e.g. [UPDF](https://updf.com/read-pdf/pdf-reader-with-text-to-speech/)) | Vendor guidance: listening helps notice repeated or missing words, awkward sentences and column-order errors. *Practical advice, not a validated method.* |
| **MathReader** — 2025 | [arXiv:2501.07088](https://arxiv.org/abs/2501.07088) — TTS for mathematical documents; converts LaTeX formulas to spoken English. 數學文件 TTS。 |

No peer-reviewed work was found that uses read-aloud of the indexed text as a systematic quality audit of a RAG corpus (search date 2026-10-21).

## 5. Figures and tables (next step) / 圖表（下一步）

**Summary.** Key quantitative results in scientific papers often live in tables and figures, which text pipelines discard or garble. Dedicated tools extract captioned figures and tables (PDFFigures 2.0) or recover table structure (Table Transformer trained on PubTables-1M); page-image retrieval (ColPali) skips OCR altogether. A biomedical study found multimodal RAG only slightly ahead of text RAG, with results depending on the answering model.
**Contribution.** These works provide reusable components and a first, cautious estimate of how much figures and tables add to RAG accuracy.
**Relevance to our experiment.** Our v2 currently drops captions and table remnants — the largest known gap (e.g. yields reported only in a table). The modest gains reported in the literature argue for an incremental plan: captions first (cheap), then tables, and figure descriptions only if the evaluation shows a benefit ([#6](https://github.com/kylecat/listen-to-your-rag/issues/6)–[#8](https://github.com/kylecat/listen-to-your-rag/issues/8)).

**摘要**：科學論文的關鍵數據常在表格與圖中，而文字流程會丟棄或弄亂它們。專門工具可以擷取有說明的圖表（PDFFigures 2.0）或還原表格結構（以 PubTables-1M 訓練的 Table Transformer）；頁面影像檢索（ColPali）則完全跳過 OCR。一項生醫研究發現，多模態 RAG 只比純文字 RAG 略好，且結果取決於回答用的模型。
**貢獻**：這些研究提供了可重用的元件，並對「圖表能為 RAG 增加多少準確度」給出初步而保守的估計。
**與本實驗的關係**：v2 目前會濾掉圖表說明與表格殘片，這是已知最大的缺口（例如產量數據只出現在表格裡）。文獻報告的增益有限，因此採漸進計畫：先做圖表說明（便宜），再做表格，圖片描述等評測顯示有幫助才做。


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
