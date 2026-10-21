# Evaluation 1 — known-item queries (2026-10-21)

> Index versions: **v1** (original) vs **v2** (extractor 0.1.4, single-version rebuild). Same embedding model (`nomic-embed-text`, 768-d), cosine similarity, no query prefix — identical to the production search service. Protocol: [design/04-evaluation.md](../design/04-evaluation.md). Issue: [#3](https://github.com/kylecat/listen-to-your-rag/issues/3).

## Setup

- **Sample:** 100 papers drawn with a fixed seed (20261021) from 453 eligible papers (excluding duplicates, non-papers, Japanese-language papers and papers without a file).
- **Questions:** one English question per paper, written from the **raw PDF text** (first five pages, not from either index's chunks) by AI sub-agents (Claude Opus 5.5) following a fixed protocol: 12–35 words; answerable only by that paper; no run of more than 6 words copied from the paper; no title fragment, author, venue or year. Each question was checked automatically for copied runs and title overlap; 6 questions were rewritten during checking.
- **Quality flag:** 6 questions are marked *low* (scrambled scan text ×2, non-research front matter ×2, file/metadata mismatch ×2). Results are reported for **all 100** and for the **94** questions marked *ok*.
- **Scoring:** top-100 chunks → ranked list of unique papers; the gold paper (or a known duplicate) must appear. Hit@5, Hit@10, MRR@10, F1@5.
- **Statistics:** paired differences (v2 − v1), bootstrap 95% CI (10,000 resamples over queries), Wilcoxon signed-rank (normal approximation), exact McNemar for hit rates.

## Results

### All 100 questions

| Metric | v1 | v2 | Δ (v2 − v1) | 95% CI | p (Wilcoxon) |
|---|---|---|---|---|---|
| Hit@5 | 0.950 | 0.980 | +0.030 | −0.010 to +0.080 | 0.18 (McNemar 0.38; 4 vs 1 discordant) |
| Hit@10 | 0.970 | 1.000 | +0.030 | 0.000 to +0.070 | 0.08 (McNemar 0.25; 3 vs 0) |
| MRR@10 | 0.852 | 0.895 | +0.043 | −0.009 to +0.099 | 0.14 |
| F1@5 | 0.317 | 0.327 | +0.010 | −0.003 to +0.027 | 0.18 |

### 94 questions marked *ok*

| Metric | v1 | v2 | Δ (v2 − v1) | 95% CI | p (Wilcoxon) |
|---|---|---|---|---|---|
| Hit@5 | 0.957 | 0.979 | +0.021 | −0.021 to +0.064 | 0.32 (McNemar 0.63; 3 vs 1) |
| Hit@10 | 0.979 | 1.000 | +0.021 | 0.000 to +0.053 | 0.16 (McNemar 0.50; 2 vs 0) |
| MRR@10 | 0.861 | 0.902 | +0.041 | −0.011 to +0.093 | 0.15 |
| F1@5 | 0.319 | 0.326 | +0.007 | −0.007 to +0.021 | 0.32 |

## How to read the metrics / 指標判讀

Each question has exactly one gold paper; all metrics ask whether it was retrieved and how high it ranked. Full guide (EN + 中文): [metrics-guide.md](metrics-guide.md).
每題只有一篇正確論文，所有指標都在問「有沒有找到、排第幾名」。完整說明（中英）：[metrics-guide.md](metrics-guide.md)。

| Metric | Meaning / 意思 | Reading these results / 本次結果怎麼看 |
|---|---|---|
| **Hit@5** | gold paper in the top 5 / 正確論文在前 5 名 | 0.95 → 0.98: v1 missed 5 of 100 questions, v2 missed 2. v1 有 5 題沒進前 5 名，v2 剩 2 題。 |
| **Hit@10** | gold paper in the top 10 / 正確論文在前 10 名 | 0.97 → 1.00: v2 found every gold paper within the top 10. v2 每題都在前 10 名。 |
| **MRR@10** | rank 1 → 1, rank 2 → ½, rank 3 → ⅓ … not in top 10 → 0 / 排名倒數的平均 | 0.852 → 0.895: v2 ranks the gold paper slightly higher. v2 把正確論文排得稍前。 |
| **F1@5** | precision–recall balance in the top 5 / 前 5 名精確率與召回率的平衡 | 0.317 → 0.327: **at most 0.333** with one gold paper (precision ≤ 1/5); a rescaling of Hit@5, not a quality judgment. 每題只有 1 篇正確時最高 0.333，等同 Hit@5 換尺度，不宜用來判斷好壞。 |

**Most informative here / 本評測最有參考價值的指標：** MRR@10 and Hit@5. F1 and nDCG become informative in Evaluation 2, where each topic has several relevant papers. F1 與 nDCG 要到評測 2（每題多篇相關論文）才有意義。

## Interpretation

- **No statistically significant difference.** v2 is numerically higher on every metric (e.g. MRR@10 +0.04), but every confidence interval includes or touches zero.
- **Ceiling effect.** Both indexes find the gold paper in the top 5 for about 95–98% of questions. Known-item questions anchored on distinctive details are easy for both versions, so this benchmark has little room to separate them. The pooled topic-query evaluation ([#4](https://github.com/kylecat/listen-to-your-rag/issues/4)) is expected to be more discriminating.
- **F1@5 is bounded.** With exactly one relevant paper per question, F1@5 is at most 1/3 (precision 1/5, recall 1); it is a rescaling of Hit@5 and adds no independent information.
- **Data issues found while building the benchmark:** one paper's title in the index came from wrong publisher PDF metadata (a leftover template title); another file under a paper's name contains a different article. Both are being corrected; they do not change the scoring, which uses paper identifiers.

## Limitations

- Questions were written by an LLM from the first pages of each paper, which favours abstract/introduction content.
- 100 questions; one domain corpus; one embedding model.
- Results compare text layers only; they say nothing yet about answer quality in downstream question answering.
