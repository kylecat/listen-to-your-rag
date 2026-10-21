# 01 · 擷取模組規格（Extraction module specification）

[English](01-extraction.md) | **繁體中文**

> 描述版本：**0.1.4**。與用途無關：它不知道 RAG 或語音的存在，只輸出乾淨的結構化文字。僅使用 Python 標準函式庫 + poppler。

## 1. 介面（Interface）

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

CLI（建議）：`python -m <module> <pdf> [--section abstract] [--json] [--no-cache]`。

**快取：** 鍵 = `resolved path | file size | mtime | extractor version` 的 SHA-1；值 = 以 JSON 表示的文件。提升版本號會讓所有快取項目失效。

## 2. 處理步驟（Pipeline）

### 2.1 取得閱讀順序正確的文字（Raw text with reading order）

1. 執行一次 `pdftotext -enc UTF-8`（純文字模式）。
2. **CJK 文件：** 若 CJK 字元超過非空白字元的 **30%**，使用純文字模式的文字（在我們的測試中，區塊層級重排會把 CJK 行切得支離破碎）。
3. 否則執行 `pdftotext -bbox-layout`，並依序解析頁 → 區塊（`xMin,yMin,xMax,yMax`）→ 行 → 字。
4. **逐頁欄位排序**（頁寬 `W`，`mid = W/2`）：
   - 若 `(xMax − xMin) > 0.55·W`，**或**區塊跨越中線（`xMin < mid−20` 且 `xMax > mid+20`），則該區塊為**全寬**；
   - 由上而下走訪區塊；每遇到一個全寬區塊就**清出**目前的區段：先輸出該區段的左欄區塊（中心 `< mid`）並依 `y` 排序，再輸出右欄區塊並依 `y` 排序，最後輸出該全寬區塊本身。
5. **掃描檔退回：** 若重排後的文字 ≤ 50 字，或**區塊大小中位數 < 4 字**（掃描 PDF 的典型特徵：文字層每個區塊只有一個字），改用純文字模式的文字。
6. 頁與頁之間以換頁字元（`\f`）分隔，區塊之間以空行分隔。

### 2.2 清理（Cleaning）

| 規則 | 細節 |
|---|---|
| 連字（Ligatures） | `ﬁ ﬂ ﬀ ﬃ ﬄ` → `fi fl ff ffi ffl`；軟連字號與 U+2010/2011 正規化 |
| 頁碼 | 刪除符合 `^\d{1,4}$`、`page N (of M)`、`N / M` 的行 |
| 頁首頁尾 | 將數字正規化為 `#`；位於某頁開頭或結尾 4 行之內、且在 ≥ `max(3, pages/3)` 頁重複出現的行即移除 |
| 出版社側欄 | 移除行首的 `Article history`、`Received (in revised form)`、`Accepted`、`Available online`、`Published online` 等前綴，以及開頭的 `DD Month YYYY` |
| 區塊接合 | 區塊內的各行以空格接合；下一行以小寫開頭時還原行尾斷字連字號；跨換行時 **CJK 字元之間不加空格** |
| 斷裂段落 | 當前一區塊不以句末標點結尾，**且**（下一區塊以小寫開頭，**或**前一區塊以 `, ; - –` 或功能詞如 *and, of, the, to, in, with, which, is* 結尾）時，把該區塊併入前一區塊 |

### 2.3 章節判斷（Section detection）

一行若（正規化後）≤ 60 個字元，且符合下列任一模式，即為**標題**；模式前可選擇性帶有 `1.`、`2.1`、`IV.` 或中文數字 `一、` 等編號，後面可選擇性接 `:`/`：`。

比對前的正規化：字母間隔開的標題（`A B S T R A C T` → `ABSTRACT`）；被 PDF 字型拆開的小型大寫字（`A BSTRACT` → `ABSTRACT`）。

| 類型 | 模式（不分大小寫） |
|---|---|
| abstract | abstract, summary, 要旨, 概要, 要約, 摘要 |
| introduction | introduction, background, 緒言, はじめに, 序論, まえがき, 前言, 引言 |
| methods | (materials and / experimental) method(s), methodology, materials, experimental (design/setup), study area/site, 方法, 実験方法, 材料および方法, 研究方法 |
| results | results (and discussion), 結果(および考察) |
| discussion | discussion, 考察, 討論 |
| conclusion | conclusion(s), concluding remarks, 結論, おわりに, まとめ, 結語 |
| back（捨棄） | references, literature cited, bibliography, acknowledg(e)ments, funding, author contributions, conflict(s) of interest, data availability, supplementary material, declaration of competing interest, CRediT…, abbreviations, 参考文献, 謝辞, 付録 |

**行內標籤：** 以 `Abstract`/`Summary` 開頭、後接 `. : — – -` 再接大寫字母的區塊，會開啟一個 abstract 章節；標籤本身會被移除。

### 2.4 區塊分類（Block classification）

定義（`n` = 字數，即拉丁字詞數 + CJK 字元數/2）：
- **正文段落（prose）** — `n ≥ 40`，且至少有 2 個句末（`". "`、結尾的 `.`、`。`、`．`）。
- **句子文字（sentence text）** — 以 `. ! ? 。 ． ！ ？` 結尾（後面可接引號或括號），或包含 `". "`、`。` 或 `．`。
- **投稿資訊（metadata）** — 計算提示詞的命中數，例如 *www., edited by, reviewed by, correspondence, received:, accepted:, published:, citation:, copyright, ©, licence/license, e-mail, @, ORCID, open access, keywords:, article history, journal homepage, contents lists available, http(s)://, doi, ISSN, vol., institutional repository, personal website*。命中數 ≥ 2，或命中數 = 1 且 `n < 60` 時，該區塊即為投稿資訊；**長篇正文段落（`n ≥ 120`）需命中數 ≥ 4**（摘要常會提到授權條款或網址）。
- **圖表說明（caption）** — 以 `Fig.`、`Figure`、`Table`、`Supplementary Fig./Table`、`図`、`表` 開頭並後接數字。

### 2.5 組裝（Assembly）

依序走訪區塊，起始於 `front` 章節：
1. 標題 → 開啟該類型的新章節（`back` 章節不收集任何內容）。
2. 略過圖表說明與 `n < 8` 的區塊；略過 `n < 120` 的非句子區塊（表格殘餘）。
3. 在 `front` 中：**第一個非投稿資訊的正文段落區塊**會開啟一個推斷的 `abstract`（標題為 `(abstract)`）——但僅限於尚未出現過 abstract 的情況。其他 `front` 區塊留在 `front`。
4. **推斷的 abstract 恰好只收一個區塊**；之後的區塊進入推斷的 `body` 章節，直到下一個標題為止。
5. 其他位置：略過非正文段落的投稿資訊；其餘全部附加進去。

## 3. 已知限制（Known limitations）

- 文字層錯亂的掃描檔無法靠重排修復。
- 跨行拆開的 CJK 標題（例如 `1. 緒` / `言`）無法辨識；此時 CJK 文字會落入 `body`。
- 標題偵測以模式比對為基礎；非慣例的標題會被併入前一個章節。
- 圖與表依設計刻意捨棄（見路線圖）。

## 4. 驗收（Acceptance）

見 [05-acceptance-tests.zh-TW.md](05-acceptance-tests.zh-TW.md) §1。對一篇沒有「Abstract」標題的真實雙欄期刊論文，abstract 必須從摘要的第一句開始，introduction 必須從其第一句開始（而不是右欄）。
