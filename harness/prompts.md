# Prompts / 提示詞

Use one at a time; wait for the report before the next.

**P0** — “Read `AGENTS.md` and `docs/design/00-overview.md`. Check the environment for P0 in `harness/build-plan.md` and report versions, free memory and anything missing. Do not install system packages without asking.”

**P1** — “Implement the extraction module exactly as in `docs/design/01-extraction.md`. Write tests E1–E7 from `05-acceptance-tests.md` first, then the code. Run E8 on `<open-access two-column PDF>`. Report test results, per-paper time and any rule you had to change (with the reason). Stop after P1.”

**P2** — “Implement chunking and the batch index builder per `02-chunking-and-index.md` into a new table next to the existing one. Run a 5-paper pilot, show the per-paper stats, wait for approval, then run the full rebuild in the background and report the final stats.”

**P3** — “Find papers whose stored file path is missing. Propose matches by content (02 §5) as three lists: auto, review, not found. Do not move or copy any file until I approve.”

**P4** — “Add CJK handling (01 §2.1, 02 §7). For each Japanese paper draft an English summary from the original text, labelled as a translation by you; show them to me before indexing.”

**P5** — “Build the read-aloud path per `03-read-aloud.md`. Tests S1–S13 and C1–C4 first. Measure TTS on CPU and GPU (time, peak memory) and implement automatic device selection. Send one test clip.”

**P6** — “Prepare evaluation per `04-evaluation.md`: the 100 known-item questions (show 10 samples first) and the 30-topic list for my approval. Then run, judge blind, compute metrics with CIs, and write a dated, versioned results document.”
