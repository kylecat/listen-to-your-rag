# 01 · Extraction module specification / 擷取模組規格

> Version described: **0.1.4**. Purpose-agnostic: it knows nothing about RAG or speech. Pure standard library + poppler.
> 與用途無關的擷取模組：不知道 RAG 或語音的存在，只輸出乾淨的結構化文字。

## 1. Interface / 介面

```text
extract(pdf_path, use_cache=True) -> Document

Document
  pdf_path: str
  title: str                 # PDF metadata title if ≥3 words, else derived from file name
  year: int | null           # leading 19xx/20xx in file name, else first plausible year in the first 3,000 chars
  extractor_version: str
  sections: [Section]
  section(type) -> Section | null        # first section of that type
  reading_sections() -> [Section]        # excludes "front" and "back", non-empty only

Section
  type: front | abstract | introduction | methods | results | discussion | conclusion | body | back
  heading: str               # original heading text, "(abstract)" / "(body)" when inferred
  paragraphs: [str]
  word_count: int            # Latin words + CJK characters / 2
```

CLI (recommended): `python -m <module> <pdf> [--section abstract] [--json] [--no-cache]`.

**Cache:** key = SHA-1 of `resolved path | file size | mtime | extractor version`; value = the document as JSON. Bumping the version invalidates every cache entry.

## 2. Pipeline / 處理步驟

### 2.1 Raw text with reading order / 取得閱讀順序正確的文字

1. Run `pdftotext -enc UTF-8` (plain mode) once.
2. **CJK documents:** if CJK characters exceed **30%** of non-space characters, use the plain-mode text (block-level reordering fragments CJK lines in our tests).
3. Otherwise run `pdftotext -bbox-layout` and parse pages → blocks (`xMin,yMin,xMax,yMax`) → lines → words.
4. **Column ordering per page** (page width `W`, `mid = W/2`):
   - a block is **full-width** if `(xMax − xMin) > 0.55·W` **or** it straddles the middle (`xMin < mid−20` and `xMax > mid+20`);
   - walk blocks top-to-bottom; each full-width block **flushes** the current segment: emit the segment's left-column blocks (centre `< mid`) sorted by `y`, then its right-column blocks sorted by `y`, then the full-width block itself.
5. **Scan fallback:** if the reordered text has ≤ 50 words or the **median block size is < 4 words** (typical of scanned PDFs whose text layer is one word per block), use the plain-mode text instead.
6. Pages are separated by form feed (`\f`), blocks by a blank line.

### 2.2 Cleaning / 清理

| Rule | Detail |
|---|---|
| Ligatures | `ﬁ ﬂ ﬀ ﬃ ﬄ` → `fi fl ff ffi ffl`; soft hyphen and U+2010/2011 normalised |
| Page numbers | drop lines matching `^\d{1,4}$`, `page N (of M)`, `N / M` |
| Running headers/footers | normalise digits to `#`; a line among the first or last 4 lines of a page that repeats on ≥ `max(3, pages/3)` pages is removed |
| Publisher side panel | strip line prefixes such as `Article history`, `Received (in revised form)`, `Accepted`, `Available online`, `Published online` and a leading `DD Month YYYY` |
| Block joining | join lines of a block with spaces; undo end-of-line hyphenation when the next line starts lower-case; **no space between CJK characters** across line breaks |
| Broken paragraphs | merge a block into the previous one when the previous block does not end with sentence punctuation **and** (the next starts lower-case **or** the previous ends with `, ; - –` or a function word such as *and, of, the, to, in, with, which, is*) |

### 2.3 Section detection / 章節判斷

A line is a **heading** if (after normalisation) it is ≤ 60 characters and matches one of the patterns below, optionally prefixed by `1.`, `2.1`, `IV.` or Chinese numerals `一、`, and optionally followed by `:`/`：`.

Normalisation before matching: letter-spaced headings (`A B S T R A C T` → `ABSTRACT`); small caps split by PDF fonts (`A BSTRACT` → `ABSTRACT`).

| Type | Patterns (case-insensitive) |
|---|---|
| abstract | abstract, summary, 要旨, 概要, 要約, 摘要 |
| introduction | introduction, background, 緒言, はじめに, 序論, まえがき, 前言, 引言 |
| methods | (materials and / experimental) method(s), methodology, materials, experimental (design/setup), study area/site, 方法, 実験方法, 材料および方法, 研究方法 |
| results | results (and discussion), 結果(および考察) |
| discussion | discussion, 考察, 討論 |
| conclusion | conclusion(s), concluding remarks, 結論, おわりに, まとめ, 結語 |
| back (dropped) | references, literature cited, bibliography, acknowledg(e)ments, funding, author contributions, conflict(s) of interest, data availability, supplementary material, declaration of competing interest, CRediT…, abbreviations, 参考文献, 謝辞, 付録 |

**Inline label:** a block starting with `Abstract`/`Summary` followed by `. : — – -` and a capital letter opens an abstract section; the label is removed.

### 2.4 Block classification / 區塊分類

Definitions (`n` = word count, Latin words + CJK chars/2):
- **prose** — `n ≥ 40` and at least 2 sentence ends (`". "`, final `.`, `。`, `．`).
- **sentence text** — ends with `. ! ? 。 ． ！ ？` (optionally followed by a quote or bracket) or contains `". "`, `。` or `．`.
- **metadata** — counts matches of hints such as *www., edited by, reviewed by, correspondence, received:, accepted:, published:, citation:, copyright, ©, licence/license, e-mail, @, ORCID, open access, keywords:, article history, journal homepage, contents lists available, http(s)://, doi, ISSN, vol., institutional repository, personal website*. A block is metadata if hits ≥ 2, or hits = 1 and `n < 60`; **long prose (`n ≥ 120`) needs hits ≥ 4** (abstracts often mention a licence or URL).
- **caption** — starts with `Fig.`, `Figure`, `Table`, `Supplementary Fig./Table`, `図`, `表` followed by a number.

### 2.5 Assembly / 組裝

Walk the blocks in order, starting in a `front` section:
1. Heading → open a new section of that type (`back` sections collect nothing).
2. Skip captions and blocks with `n < 8`; skip non-sentence blocks with `n < 120` (table remnants).
3. In `front`: the **first prose block that is not metadata** opens an inferred `abstract` (heading `(abstract)`) — but only if no abstract was seen yet. Other `front` blocks stay in `front`.
4. An **inferred abstract takes exactly one block**; following blocks go to an inferred `body` section until the next heading.
5. Elsewhere, skip metadata that is not prose; append everything else.

## 3. Known limitations / 已知限制

- Scans with a scrambled text layer cannot be repaired by reordering.
- CJK headings split across lines (e.g. `1. 緒` / `言`) are not recognised; CJK text then lands in `body`.
- Heading detection is pattern-based; unconventional headings fall into the preceding section.
- Figures and tables are dropped by design (see roadmap).

## 4. Acceptance / 驗收

See [05-acceptance-tests.md](05-acceptance-tests.md) §1. On a real two-column journal article without an “Abstract” heading, the abstract must start with the first abstract sentence and the introduction with its first sentence (not the right column).
