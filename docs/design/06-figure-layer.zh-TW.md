# 06 · 圖表層方法（Figure layer）

[English](06-figure-layer.md) | **繁體中文**

> 狀態：10 篇論文試驗（2026-10-28）。結果見 [figure-layer-pilot-2026-10-28.md](../results/figure-layer-pilot-2026-10-28.md#繁體中文)；流程圖見 [figures/figure-layer/](../figures/figure-layer/)。

## 目的
讓只出現在圖和表裡的資訊也能被檢索，同時避免把從圖上推估的數值誤當成作者報告的數值。

## 比較的流程

| 流程 | 摘要 | 流程圖 |
|---|---|---|
| v1 | 逐頁擷取、每 500 字硬切；圖說和表格殘片混在正文裡 | [flow-v1](../figures/figure-layer/flow-v1.png) |
| v2 | 依座標的規則式擷取（見 [01](01-extraction.zh-TW.md)、[02](02-chunking-and-index.zh-TW.md)）；**圖說和表格被丟棄** | [flow-v2](../figures/figure-layer/flow-v2.png) |
| v3 | Docling 擷取正文，用 v2 的章節規則與切段；圖表模型關閉 | [flow-v3](../figures/figure-layer/flow-v3.png) |
| v3-full | Docling 開啟 OCR、表格結構、圖片分類與 SmolVLM-256M；每張圖、每個表各一段 | [flow-v3full](../figures/figure-layer/flow-v3full.png) |
| v2＋LLM 描述 | v2 正文＋每張圖一段學術描述；從圖上讀出的數值另存證據表 | [flow-v2-ai](../figures/figure-layer/flow-v2-ai.png) |
| 合併組 | v2＋LLM 描述＋Docling 的圖說、OCR 文字與表格（不含 SmolVLM 描述） | — |

所有流程使用相同的向量模型和相似度計算，差異只來自被索引的文字。

## v2＋LLM 圖表描述
1. **定位與裁切**：沿用 Docling 版面模型的圖框座標，從 PDF 裁切每張圖，不重跑整篇。
2. **向量或點陣**：檢查圖框內是 PDF 繪圖指令（向量圖）還是嵌入的圖片（點陣圖）。
3. **資料包**：從圖說解析出圖號，加上圖說、正文中引用該圖的句子，以及裁切圖。
4. **描述（LLM）**：80–180 字，用論文本身的術語寫出圖的類型、變數與單位、處理組與條件、主要趨勢。**只寫作者報告的數值**（正文、圖說、表格或印在圖上的數字），並附出處；開頭標示為 AI 產生。
5. **建索引**：每張圖一段，`section_type = figure_description`。
6. **證據表（不進索引）**：從圖上讀出的數值另外存放。

## 推估數值的規則
| 規則 | 內容 |
|---|---|
| 分開存放 | 正文和圖表描述進索引；從圖上讀出的數值只放在證據表，agent 要另外查詢 |
| 每個推估值都要標註 | `57%〔推估｜正文報告 58%（Results, p.6）〕` 或 `4.54 mmol m⁻² s⁻¹〔推估｜正文無對應描述，為自行推估結果〕` |
| 一致性欄位 | `match`（差距 ≤ 5%）、`differs`（> 5%，需人工檢查）、`not_reported` |
| 優先順序 | 作者有報告的數值優先引用，推估值只作補充 |
| 讀數方法 | 向量圖：PDF 繪圖座標＋刻度校正；點陣圖：放大量測，讀數時看不到論文正文（盲測） |

## Docling 與 SmolVLM 的架構
Docling 2.141 標準 PDF 流程（設定取自本機安裝的模型檔；流程圖 [flow-docling-smolvlm](../figures/figure-layer/flow-docling-smolvlm.png)）：

| 階段 | 元件 | v3 | v3-full |
|---|---|---|---|
| 頁面前處理 | PDF 文字與座標、頁面影像 | 開 | 開 |
| OCR | RapidOCR（PP-OCRv6 偵測＋辨識） | 關 | 開 |
| 版面分析 | Heron：RT-DETRv2 物件偵測，ResNet-50 骨幹，17 類區塊 | 開 | 開 |
| 表格結構 | TableFormer | 關 | 開 |
| 組裝 | 閱讀順序、標題階層、圖說配對 | 開 | 開 |
| 圖片分類 | EfficientNet，26 類 | 關 | 開 |
| 圖片描述 | SmolVLM-256M-Instruct | 關 | 開 |
| 圖表數據擷取 | Granite-Vision 4.1（4B） | 關 | 關（約需 8 GB 記憶體） |

SmolVLM-256M（Idefics3 架構）：圖片切成 512×512 小塊並加一張縮小的全圖；SigLIP-B/16-512 視覺編碼器（9,300 萬參數）為每塊產生 1,024 個 patch 特徵，經 pixel shuffle（×4）壓縮成 64 個視覺 token；最後由 SmolLM2-135M 產生文字。Docling 的預設值：提示詞「Describe this image in a few sentences.」、最多 200 個 token、只處理面積至少佔頁面 5% 的圖。

## 全庫的建議做法
只處理圖表，不重跑整篇：沿用版面座標；每張圖索引圖說、圖上的 OCR 文字和 LLM 學術描述；表格轉成 Markdown；不使用 SmolVLM 描述。擴大規模前，先加上「圖說與圖片配對」的自動檢查，並把作者報告值和描述分開存放。

## 參考
Auer, C. et al. (2024). *Docling Technical Report.* arXiv:2408.09869。SmolVLM-256M-Instruct 模型卡（Hugging Face）：SmolLM2-135M-Instruct＋google/siglip-base-patch16-512。
