# Agent instructions — literature RAG text layer + read-aloud

You are implementing the system specified in `docs/design/` (00–05). Treat those documents as the source of truth; if they are ambiguous or wrong, stop and ask instead of guessing.

## Working rules
1. **Phase by phase.** Follow `harness/build-plan.md`. At the end of each phase stop and report: what was built, test results, measurements, open questions. Do not start the next phase without approval.
2. **Tests first for rules.** Every extraction, cleaning and speakable-rewrite rule gets a unit test taken from `docs/design/05-acceptance-tests.md` before or with its implementation.
3. **Measure, don't assume.** Report wall time and peak memory for extraction batches, embedding and TTS on the actual hardware. Prefer the cheaper option that meets the target; record why.
4. **Never destroy data.** Build new indexes beside old ones; move instead of delete; keep a fallback for every failure path; make batch jobs resumable and idempotent.
5. **Long jobs in the background** with a state file and a log; keep each interactive step short.
6. **Version everything.** The extractor has a version string that is part of the cache key; numbers in reports state date and version; finish with a single-version run before publishing numbers.
7. **Label generated content.** Translations, figure descriptions and LLM relevance judgments must carry a visible label naming the model.
8. **Respect copyright and privacy.** Do not commit PDFs, extracted text, caches, credentials, host names or personal data.
9. **Disclose AI use.** Commits include a co-author trailer for the AI model; the README states model name, version and role.

## Definition of done (per phase)
- acceptance tests for the phase pass;
- measurements reported;
- documentation updated if behaviour differs from the design (and the design doc updated with the reason).
