# Build plan / 建置計畫

| Phase | Build | Gate (must pass before continuing) |
|---|---|---|
| **P0** | Environment check: poppler `-bbox-layout`, Python, vector store, embedding model, free memory | report of versions and available memory |
| **P1** | Extraction module: data model, cleaning, block joining, column ordering, scan/CJK fallbacks, sections, cache, CLI | tests E1–E7 pass; E8 on one open-access two-column paper; extraction time per paper reported |
| **P2** | Chunker + index builder: schema, sentence-aligned chunks, embedding with retry, resumable batches, fallback, skip list | tests I1–I5, I7; a 5-paper pilot then full rebuild into a **new** table; stats: chunks, share of `other`, abstracts found |
| **P3** | Path recovery and de-duplication (content matching, MD5 duplicates, copy-in) | recovered / review / not-found lists reviewed by a human before applying |
| **P4** | Non-English handling: CJK extraction paths, labelled English summary chunks | test I6; retrieval spot-check with English queries |
| **P5** | Read-aloud: speakable rewrite, TTS with automatic device choice, delivery order, flag log | tests S1–S13, C1–C4; TTS time and peak memory on CPU and GPU |
| **P6** | Evaluation: known-item set, pooled topic set, human subset, statistics | `docs/design/04-evaluation.md` protocol followed; results versioned; then decide on switching |

Rule of thumb from our build: keep each agent step under ~20 minutes of wall time; run anything longer as a background job and poll its log.
