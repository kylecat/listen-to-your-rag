# 05 · 驗收測試（Acceptance tests）
[English](05-acceptance-tests.md) | **繁體中文**

> 重新實作的版本應通過的行為測試。這些測試對應我們（未公開）程式碼的單元測試；除非另有說明，輸入皆為合成文字。

## 1. 擷取模組

| # | 輸入 | 預期 |
|---|---|---|
| E1 | 標題 `2. MATERIALS AND METHODS`、`References`、`Introduction`；句子 “This is a sentence about introduction of plants.” | methods、back、introduction；該句**不是**標題 |
| E2 | 兩行 `the measure-` + `ment was …` | `the measurement was …` |
| E3 | `ﬁeld measure-⏎ment⏎12⏎`（貼上的文字） | `field measurement`（修正連字、刪除頁碼） |
| E4 | 頁寬 600；區塊 L1（x 50–290，y 100）、R1（310–560，y 90）、L2（50–290，y 320）、TITLE（40–560，y 40） | 順序 TITLE, L1, L2, R1 |
| E5 | 期刊中繼資料區塊（published/doi）、“Edited by / Reviewed by / Correspondence”、兩段正文、`INTRODUCTION`、正文、`References`、一筆參考文獻 | abstract = 第一段正文；存在 introduction；參考文獻文字在任何地方都不出現 |
| E6 | `Abstract—` + 正文，接著 `1 Introduction` + 正文 | abstract 從正文開始（標籤已移除） |
| E7 | introduction 的正文段落之間夾有圖說 `Figure 2. …` 與表格列 `CSX2027 CSX8521 …` | 圖說與表格列皆不出現 |
| E8 *（真實 PDF）* | 一篇沒有 “Abstract” 標題的雙欄開放取用期刊論文 | abstract 從其第一句開始；introduction 從其第一句開始，而不是右欄文字 |

## 2. 念法轉換

| # | 輸入 | 預期（輸出中的子字串） |
|---|---|---|
| S1 | `Yield rose [12] and fell [3–5], [1, 2].` | 引用已移除 |
| S2 | `(Smith et al., 2023)`、`(Kim and Lee, 2019; Wang, 2020a)` | 移除 |
| S3 | `at 25 °C` | twenty-five degrees Celsius |
| S4 | `EC of 1.5 dS/m` | one point five deciSiemens per meter |
| S5 | `200 µmol m⁻² s⁻¹` | two hundred micromoles per square meter per second |
| S6 | `17 mol m-2 d-1` | seventeen moles per square meter per day |
| S7 | `(p < 0.05, R² = 0.87, n = 30)` | p less than zero point zero five · R squared equals zero point eight seven · n equals thirty |
| S8 | `VPD was high. Later VPD dropped.`（詞彙表含 VPD） | `vapor pressure deficit was high. Later VPD dropped.` |
| S9 | `The vapour pressure deficit (VPD) rose. VPD fell.` | `The vapour pressure deficit rose. VPD fell.` |
| S10 | `α and σ` | alpha and sigma |
| S11 | `Then y = a + b × x^2 / (c + d) holds. Plants grew.` | 方程式句被略去；保留 `Plants grew.` |
| S12 | 句中含 URL 與 `doi: 10.3389/…` | 兩者皆移除 |
| S13 | `In 2022 yield rose 15%.` | twenty twenty-two · fifteen percent |

## 3. 斷句器（朗讀用）

| # | 輸入 | 預期 |
|---|---|---|
| C1 | `Dr. Smith measured 1.5 dS/m, e.g. in Fig. 2. It worked.` | 2 句（不在 Dr.、e.g.、Fig.、小數點處切開） |
| C2 | `Why? Nobody knows! Really.` | 3 句 |
| C3 | 含逗號的 28 字句子 | 跟讀模式在最接近中間的逗號處切成 2 段；各段接回後與原文相同 |
| C4 | 40 個 7 字句子 | “paper” 模式：每個段落（切塊）≤ 150 字、≥ 2 個段落，段落接回後與原文相同 |

## 4. 索引建構器

| # | 情境 | 預期 |
|---|---|---|
| I1 | 重跑一個批次 | 沒有重複資料列（插入前先刪除該批次的資料列） |
| I2 | 批次中途當掉 | 該批次不寫入任何資料；重跑即可完成 |
| I3 | 缺少 PDF | 複製 v1 段落，並記錄原因 |
| I4 | 擷取字數 < 300 的掃描檔 | 複製 v1 段落，`extract_too_short` |
| I5 | id 在略過清單上 | 不產生資料列，記錄原因與 `dup_of` |
| I6 | 附翻譯的日文論文 | v2 段落 + 一個帶有可見翻譯標註的 `translation_en` 段落 |
| I7 | 長段落觸發向量伺服器錯誤 | 以較短輸入重試；批次繼續執行 |
