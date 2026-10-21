# 05 · Acceptance tests / 驗收測試

**English** | [繁體中文](05-acceptance-tests.zh-TW.md)

> Behavioural tests a re-implementation should pass. They mirror the unit tests of our (unpublished) code; inputs are synthetic text unless stated.

## 1. Extraction module

| # | Input | Expected |
|---|---|---|
| E1 | headings `2. MATERIALS AND METHODS`, `References`, `Introduction`; sentence “This is a sentence about introduction of plants.” | methods, back, introduction; the sentence is **not** a heading |
| E2 | lines `the measure-` + `ment was …` | `the measurement was …` |
| E3 | `ﬁeld measure-⏎ment⏎12⏎` (pasted text) | `field measurement` (ligature fixed, page number dropped) |
| E4 | page width 600; blocks L1 (x 50–290, y 100), R1 (310–560, y 90), L2 (50–290, y 320), TITLE (40–560, y 40) | order TITLE, L1, L2, R1 |
| E5 | journal metadata block (published/doi), “Edited by / Reviewed by / Correspondence”, two prose paragraphs, `INTRODUCTION`, prose, `References`, a reference | abstract = first prose paragraph; introduction exists; reference text absent everywhere |
| E6 | `Abstract—` + prose, then `1 Introduction` + prose | abstract starts with the prose (label removed) |
| E7 | introduction with a caption `Figure 2. …` and a table row `CSX2027 CSX8521 …` between prose paragraphs | caption and table row absent |
| E8 *(real PDF)* | a two-column open-access journal article without an “Abstract” heading | abstract starts with its first sentence; introduction starts with its first sentence, not right-column text |

## 2. Speakable rewrite

| # | Input | Expected (substring of output) |
|---|---|---|
| S1 | `Yield rose [12] and fell [3–5], [1, 2].` | citations removed |
| S2 | `(Smith et al., 2023)`, `(Kim and Lee, 2019; Wang, 2020a)` | removed |
| S3 | `at 25 °C` | twenty-five degrees Celsius |
| S4 | `EC of 1.5 dS/m` | one point five deciSiemens per meter |
| S5 | `200 µmol m⁻² s⁻¹` | two hundred micromoles per square meter per second |
| S6 | `17 mol m-2 d-1` | seventeen moles per square meter per day |
| S7 | `(p < 0.05, R² = 0.87, n = 30)` | p less than zero point zero five · R squared equals zero point eight seven · n equals thirty |
| S8 | `VPD was high. Later VPD dropped.` (glossary VPD) | `vapor pressure deficit was high. Later VPD dropped.` |
| S9 | `The vapour pressure deficit (VPD) rose. VPD fell.` | `The vapour pressure deficit rose. VPD fell.` |
| S10 | `α and σ` | alpha and sigma |
| S11 | `Then y = a + b × x^2 / (c + d) holds. Plants grew.` | equation sentence omitted; `Plants grew.` kept |
| S12 | URL and `doi: 10.3389/…` in a sentence | both removed |
| S13 | `In 2022 yield rose 15%.` | twenty twenty-two · fifteen percent |

## 3. Sentence chunker (read-aloud)

| # | Input | Expected |
|---|---|---|
| C1 | `Dr. Smith measured 1.5 dS/m, e.g. in Fig. 2. It worked.` | 2 sentences (no split at Dr., e.g., Fig., decimal) |
| C2 | `Why? Nobody knows! Really.` | 3 sentences |
| C3 | 28-word sentence with commas | shadowing splits into 2 parts at the comma nearest the middle; parts rejoin to the original |
| C4 | 40 seven-word sentences | “paper” mode: every chunk ≤ 150 words, ≥ 2 chunks, chunks rejoin to the original |

## 4. Index builder

| # | Scenario | Expected |
|---|---|---|
| I1 | rerun a batch | no duplicate rows (batch rows deleted before insert) |
| I2 | crash mid-batch | nothing written for that batch; rerun completes it |
| I3 | PDF missing | v1 chunks copied, reason recorded |
| I4 | scan with < 300 extracted words | v1 chunks copied, `extract_too_short` |
| I5 | id on skip list | no rows, reason and `dup_of` recorded |
| I6 | Japanese paper with translation | v2 chunks + one `translation_en` chunk with a visible translation label |
| I7 | embedding server error on a long chunk | retried with shorter input; batch continues |
