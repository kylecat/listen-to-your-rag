# How to read the evaluation metrics / 評測指標判讀說明

> Applies to all results in this folder. Retrieval is scored at the **paper level**: retrieved chunks are mapped to papers and de-duplicated before scoring.
> 本資料夾所有結果皆適用。檢索以**論文**為單位計分：取回的段落先換算成論文並去除重複，再計分。

## English

### Metrics for known-item queries (Evaluation 1)

Each question has exactly **one** correct ("gold") paper. All metrics ask: *was the gold paper retrieved, and how high was it ranked?*

| Metric | Meaning | Computation | In plain words |
|---|---|---|---|
| **Hit@5** | top-5 hit rate | 1 if the gold paper is in the top 5, else 0; averaged over questions | "Look at the first 5 papers — how often is the right one there?" |
| **Hit@10** | top-10 hit rate | same, within the top 10 | "Looking a little further — how often is it found?" |
| **MRR@10** | mean reciprocal rank | rank 1 → 1, rank 2 → 0.5, rank 3 → 0.33 … rank 10 → 0.1, not in top 10 → 0; averaged | "Not only whether it is found, but **how high** it ranks" |
| **F1@5** | harmonic mean of precision and recall in the top 5 | precision = share of the top 5 that is correct; recall = share of correct papers found; F1 = 2PR/(P+R) | Meaningful when a query has **several** relevant papers |

**Why F1@5 looks low here.** With one gold paper per question, even a perfect retrieval (gold at rank 1) has precision 1/5 and recall 1, so F1@5 is at most **2 × 0.2 × 1 / 1.2 = 0.333**. In Evaluation 1 it is a rescaling of Hit@5 and should not be used to judge quality.

**Reading the Evaluation 1 numbers (2026-10-21).**
- Hit@5 0.95 → 0.98: of 100 questions, v1 missed the gold paper in the top 5 for 5 questions, v2 for 2.
- Hit@10 0.97 → 1.00: within the top 10, v2 found every gold paper.
- MRR@10 0.852 → 0.895: v2 also ranks the gold paper slightly higher. As an illustration, an MRR around 0.85 is what you get when the gold paper is usually first and occasionally second or third.
- F1@5 0.317 → 0.327: bounded by 0.333 (see above).

**Which metric matters most?** For known-item queries: **MRR@10** (ranking) and **Hit@5** (findability).

### Metrics for topic queries (Evaluation 2, planned)

Each topic has **several** relevant papers, judged 0 (not relevant), 1 (partly relevant) or 2 (highly relevant).

| Metric | Meaning |
|---|---|
| **P@10** | precision at 10 — share of the top 10 papers that are relevant |
| **R@10** | recall at 10 — share of all relevant papers in the judged pool that appear in the top 10 (relative to the pool, not to the whole corpus) |
| **F1@10** | harmonic mean of P@10 and R@10 — now informative, because precision and recall vary independently |
| **nDCG@10** | normalised discounted cumulative gain — rewards highly relevant papers near the top, using the graded 0/1/2 judgments; 1.0 = ideal ordering |

### Statistics

| Term | Meaning |
|---|---|
| **Δ (v2 − v1)** | mean per-question difference; positive favours v2 |
| **95% CI** | bootstrap confidence interval of Δ (10,000 resamples over questions). If it includes 0, the difference is not established |
| **Wilcoxon p** | paired signed-rank test on per-question differences; p < 0.05 is the usual threshold |
| **McNemar** | paired test for hit/miss outcomes, based only on questions where the two versions disagree ("discordant pairs") |
| **Ceiling effect** | when both versions score near the maximum, a benchmark cannot show differences between them |

## 繁體中文

### 已知答案查詢的指標（評測 1）

每一題只有**一篇**正確論文。四個指標都在問：**正確論文有沒有被找出來、排在第幾名？**

| 指標 | 意思 | 怎麼算 | 白話 |
|---|---|---|---|
| **Hit@5** | 前 5 名命中率 | 正確論文排在前 5 名就算 1，否則算 0，再對所有題目取平均 | 「查一次，看前 5 篇，找得到的比例」 |
| **Hit@10** | 前 10 名命中率 | 同上，範圍放寬到前 10 名 | 「多看幾篇的話，找得到的比例」 |
| **MRR@10** | 平均倒數排名 | 第 1 名得 1 分、第 2 名 0.5、第 3 名 0.33……第 10 名 0.1，沒進前 10 名得 0，再取平均 | 「除了有沒有找到，**還看排得多前面**」 |
| **F1@5** | 前 5 名精確率與召回率的調和平均 | 精確率＝前 5 篇裡正確的比例；召回率＝正確論文被找到的比例；F1 = 2PR/(P+R) | 用在「一題有**很多篇**正確答案」時才有意義 |

**為什麼這裡的 F1@5 看起來很低**：每題只有 1 篇正確論文，就算排在第 1 名，前 5 篇裡也只有 1 篇是對的，精確率最多 1/5、召回率 1，所以 F1@5 **最高只有 2 × 0.2 × 1 / 1.2 = 0.333**。在評測 1 中它只是 Hit@5 換個尺度，**不建議拿來判斷好壞**。

**評測 1 的數字怎麼看（2026-10-21）**
- Hit@5：0.95 → 0.98。100 題裡，v1 有 5 題的正確論文沒進前 5 名，v2 只剩 2 題。
- Hit@10：0.97 → 1.00。放寬到前 10 名，v2 每一題都找得到。
- MRR@10：0.852 → 0.895。v2 也把正確論文排得稍微前面一些。舉例來說，MRR 約 0.85 大致相當於「多數排第 1、偶爾排第 2～3」。
- F1@5：0.317 → 0.327。上限是 0.333（見上方說明）。

**哪個指標最有參考價值**：已知答案查詢主要看 **MRR@10**（排得多前面）和 **Hit@5**（找不找得到）。

### 主題查詢的指標（評測 2，規劃中）

每個主題會有**好幾篇**相關論文，相關程度分為 0（不相關）、1（部分相關）、2（高度相關）。

| 指標 | 意思 |
|---|---|
| **P@10** | 前 10 篇中相關論文的比例（精確率） |
| **R@10** | 候選池中所有相關論文，有多少比例出現在前 10 篇（召回率；相對於候選池，不是整個文獻庫） |
| **F1@10** | P@10 與 R@10 的調和平均；此時精確率與召回率會各自變動，F1 才有意義 |
| **nDCG@10** | 正規化折損累積增益：依 0/1/2 的相關程度，越相關的論文排得越前面分數越高；1.0 代表理想排序 |

### 統計用語

| 用語 | 意思 |
|---|---|
| **Δ（v2 − v1）** | 每題差異的平均；正值代表 v2 較好 |
| **95% 信賴區間** | 以 bootstrap（對題目重抽 10,000 次）估計的 Δ 區間；區間包含 0 時，不能斷定有差異 |
| **Wilcoxon p** | 對每題差異做配對符號等級檢定；一般以 p < 0.05 為顯著門檻 |
| **McNemar** | 針對「命中／未命中」的配對檢定，只看兩版結果不一致的題目 |
| **天花板效應** | 兩版都接近滿分時，評測無法拉開差距 |
