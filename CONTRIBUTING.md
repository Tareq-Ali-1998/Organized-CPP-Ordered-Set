# Contributing

For a bug report, include the compiler/library version, a minimal program, the expected behavior, and the actual behavior. Say whether the problem concerns the unique set, multiset, article, or walkthrough.

For code changes, keep public keys immutable and the comparator strict. Preserve the current spacing and naming. Add a reference-based regression test for a new behavioral case; avoid tests that simply repeat the implementation.

Run `python build.py`, `python verify.py --full`, and `node tests/DemoModelTests.js` before proposing a change. Documentation edits should keep both article audiences distinct. Edit article templates in `sources`, not the generated articles. Every API change also needs a corresponding reference update in `docs/API.md`.

Diagrams are authored in `assets/diagrams/*.mmd`. Regenerate their SVG/PNG exports with `python tools/render_diagrams.py` after changing a source. The exact renderer version and source hashes are recorded alongside the outputs.

For walkthrough or layout changes, also install `requirements-render.txt` and run `python tools/browser_check.py`. It exercises the real UI at 1440px and 390px widths, including duplicates, missing ranks, invalid inputs, and SVG identity. Keep browser sandboxing enabled. `python tests/PublishingTests.py` checks publishing-link behavior without writing fixture URLs into the drafts.

Run `python tests/DocumentationTests.py` for shared snippet formatting, generated HTML text, build freshness/idempotence, and useful error messages. Trailing example comments use one column in all article versions. Keep Markdown PDF exports under the ignored `exports/` folder; the provided VS Code folder/workspace settings configure that destination. `docs/ProjectGuide.md` explains which inputs generate each output.

Claims about performance should include the workload, flags, compiler/library, and repeated measurements. Do not replace the ordering invariant with an assertion that finite tests prove every possible use correct.
