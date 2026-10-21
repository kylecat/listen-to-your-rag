# 04 · Evaluation design / 評測設計

> Status: **planned, not yet run** ([#3](https://github.com/kylecat/listen-to-your-rag/issues/3), [#4](https://github.com/kylecat/listen-to-your-rag/issues/4)). Results will be published with date and pipeline version.

## Unit of evaluation / 評估單位

Papers, not chunks: the two indexes cut text differently, so retrieved top-k chunks are mapped to papers and de-duplicated before scoring.

## Evaluation 1 — known-item queries / 已知答案查詢

| Item | Design |
|---|---|
| Sample | 100 papers present in both indexes, fixed random seed; exclude duplicates and non-English papers |
| Questions | an LLM reads the **raw PDF text** (not either index's chunks) and writes one English question answerable only by that paper; no copied sentences, no title strings |
| Gold | that paper (and any known duplicate) |
| Metrics | Hit@5, Hit@10, MRR@10, F1@5 (with one relevant item F1@5 is a transform of Hit@5; report but do not emphasise) |

## Evaluation 2 — pooled topic queries / 主題查詢合併盲評

| Item | Design |
|---|---|
| Queries | 30 domain topics (VPD, lighting spectra, nutrient EC, tipburn, CO₂ enrichment, plant-factory energy, thermal imaging, transpiration/stomata, LLM agents in agriculture…), confirmed by the human author |
| Pool | union of top-10 papers from each index (TREC-style pooling) |
| Judging | 0 / 1 / 2 relevance, **source index hidden**, order shuffled; an LLM judges all pairs; the human author judges a 5–10 query subset |
| Agreement | Cohen's κ between LLM and human on the subset; widen human judging if κ is low (cf. Thomas et al., SIGIR 2024) |
| Metrics | P@10, R@10 (relative to the pool), F1@10, nDCG@10 |

## Statistics / 統計

Per-query paired comparison: Wilcoxon signed-rank test and bootstrap 95% CI (10,000 resamples over queries). With 30 topic queries, report direction and CI first; avoid over-reading p-values.

## Baselines / 比較組

v1 (original), v2 (this pipeline), and a learning-based extractor (GROBID or Docling) with the same chunking and embedding model ([#5](https://github.com/kylecat/listen-to-your-rag/issues/5)).

## Threats to validity / 效度威脅

- Question writer may favour easy-to-find content → fixed sampling, paraphrase requirement.
- LLM judges may be lenient → human subset and κ.
- Pooled recall is relative to what the systems found, not true corpus recall.
- One domain corpus.
