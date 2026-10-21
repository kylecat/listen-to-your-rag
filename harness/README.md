# Harness: rebuild the system with a coding agent / 用程式代理重建系統

The code is not published. Instead, this folder gives a coding agent (Claude Code, Codex CLI or similar) what it needs to **re-implement the system from the design documents**: standing instructions, a phased build plan with gates, and ready-to-use prompts. This is how the original system was built: a human set direction and approved each phase; the agent implemented, tested and reported.

本專案不公開程式碼。這個資料夾提供程式代理（Claude Code、Codex CLI 等）**依設計文件重建系統**所需的一切：常駐指示、分階段建置計畫與驗收關卡、可直接使用的提示詞。原始系統就是這樣做出來的：人決定方向並核准每個階段，代理負責實作、測試與回報。

| File | Use |
|---|---|
| [AGENTS.md](AGENTS.md) | Standing instructions. Copy to your project root as `AGENTS.md` (Codex) or `CLAUDE.md` (Claude Code). |
| [build-plan.md](build-plan.md) | Phases P0–P6 with acceptance gates; the agent stops after each phase and reports. |
| [prompts.md](prompts.md) | Prompts to start each phase. |

## Minimal workflow / 最小流程

1. Create an empty project, copy `AGENTS.md` and the `docs/design/` folder into it.
2. Give the agent the P0 prompt from `prompts.md`.
3. Review the report; approve or correct; continue with the next phase.
4. Keep the agent's acceptance-test results and measurements with each phase report.

## What you need / 需要的環境

poppler-utils (`pdftotext` with `-bbox-layout`), Python ≥ 3.10, a vector store with fixed schemas and row deletes, an embedding model you will keep fixed, and (optional) an ONNX TTS model. A few open-access PDFs for testing — do **not** commit copyrighted papers.
