# 03 · Read-aloud and listening audit / 朗讀與聽力稽核

> Turns the same section text the index uses into speech, so a listener hears what the retriever sees. Originally built as English listening practice; the audit is a side effect we now use deliberately.

## 1. Flow / 流程

```text
request (paper by title/keyword/random, or "next")
  → extraction module (cached) → pick section (default: abstract; fallback: first readable section)
  → take ≤ ~250 words, sentence-aligned; remember position (paper, section, paragraph, offset)
  → speakable rewrite (§2)              # only the audio version is rewritten
  → TTS (§3) → OGG/Opus voice message
  → then: source line (title, year, section, part) → original text (hidden/spoiler) → 1–3 vocabulary items
  → optional explanation clearly labelled as AI-written, separate from the paper's content
  → listener may flag a problem → logged for extraction-rule fixes (§4)
```

## 2. Speakable rewrite rules / 念法轉換

Applied in this order; each rule has a unit test ([05](05-acceptance-tests.md) §2).

| Rule | Example → spoken form |
|---|---|
| PDF artefacts | `measure-⏎ment`, `ﬁeld` → measurement, field |
| URLs, DOIs | removed |
| Numeric citations | `[12]`, `[3–5]`, `[1, 2]` → removed |
| Author–year citations | `(Smith et al., 2023)`, `(Kim and Lee, 2019; Wang, 2020a)` → removed |
| Statistics (before equation check) | `p < 0.05` → p less than zero point zero five; `R² = 0.87` → R squared equals …; `n = 30` → n equals thirty |
| Equations | sentence with ≥ 4 math symbols (`= + × ∑ ∫ ^ / < > ≤ ≥ { }`) and more symbols than 3-letter words → dropped from audio |
| Abbreviations | glossary: first occurrence → full form, later → abbreviation; if the text already writes “full form (ABBR)”, drop the bracket; British/US spelling treated as equal when matching |
| Units after numbers | `25 °C` → twenty-five degrees Celsius; `1.5 dS/m` → … deciSiemens per meter; `200 µmol m⁻² s⁻¹` → … micromoles per square meter per second; `17 mol m-2 d-1` → … moles per square meter per day |
| Latin abbreviations | e.g. → for example; i.e. → that is; vs. → versus |
| Greek letters | α → alpha, σ → sigma … |
| ± and = | plus or minus; equals |
| Percent, years, numbers | `15%` → fifteen percent; `2022` → twenty twenty-two; decimals read digit by digit |

Unit grammar: a number followed by a sequence of unit tokens, each optionally with an exponent (`^-2`, `-2`, superscript `⁻²`) or a leading `/`; negative exponent → “per”, |exponent| 2/3 → “square/cubic”; the first positive unit is plural.

## 3. Speech synthesis / 語音合成

| Decision | Choice and reason |
|---|---|
| Engine | Kokoro-82M, ONNX |
| Precision | **fp32**: on our ARM CPU int8 was ~3× slower (84 s vs 30 s for 44 s of audio) |
| Device | **automatic**: GPU if available memory ≥ 3,000 MB, else CPU; GPU failure falls back to CPU |
| Measured (44 s audio) | GPU: ~5 s, peak ~2.1 GB · CPU: ~30 s, peak ~0.9 GB |
| Concurrency | one synthesis at a time (file lock) |
| Format | OGG/Opus mono, written directly by libsndfile (no ffmpeg); ~260 KB per minute |
| Voice | American English with expressive intonation (`af_bella`) for shadowing practice |
| Speed | listening 1.0 · paper 0.9 · shadowing 0.85 |

Long texts are split into ~30–60 s pieces at sentence boundaries; shadowing sends one sentence per message (long sentences split at the comma nearest the middle, > 22 words).

## 4. Listening audit log / 稽核紀錄

Each flag records: time, paper id, section, part, the listener's description, and a category:

| Category | Typical cause |
|---|---|
| column mix-up | reading order |
| broken / merged sentence | block joining, hyphenation |
| wrong section (e.g. body read as abstract) | section detection |
| noise read aloud (headers, metadata, captions) | cleaning rules |
| garbled text | scan / text layer |
| mispronunciation | speakable rewrite (not an index problem) |

Each fix references the flags it resolves; affected papers are re-extracted and re-indexed, and the before/after retrieval effect is measured with the evaluation set. This log is what would turn the audit from anecdote into evidence (see the related-work note).
