# Validation

Fresh results for this standalone project are recorded in [validation/Results.json](../validation/Results.json). The reference suite, article examples, diagram exports, and independent JavaScript walkthrough model are checked separately.

The suite checks 384,000 randomized operations, 265,720 bounded exhaustive trace states, and 27,073,587 conditions per successful full run. Article examples include 34,495 recipe checks against brute-force inversion counts and sorted-window medians. These finite checks are evidence for the contracts, not a claim of correctness for invalid comparators or every possible key type.

Compiler execution restrictions are recorded explicitly. A successful compile is not labeled a successful runtime check when an operating-system policy blocked execution. `--require-execution` makes such a limitation fail CI.

The original contribution directory is protected by [ContributionsBaseline.json](../validation/ContributionsBaseline.json). When running in the original coding-session workspace, the verifier checks those files remain byte-for-byte unchanged. That check is not applicable in a standalone GitHub checkout where the old directory is absent.

The original compiler matrix remains in `validation/Results.json`. After the publication polish, a separate GCC17 run in [PublicationRun.json](../validation/PublicationRun.json) passed the container suite, all article/recipe checks, the standalone example, paired benchmark checks, and the walkthrough model with no execution restrictions. This preserves the earlier compiler matrix rather than replacing it with a shorter run.

The polish also passed five publishing-link tests and eight documentation/tool regressions, including comment alignment in rendered code blocks, freshness checks without file writes, and launching verification from the parent directory. [PublicationPolish.json](../validation/PublicationPolish.json) records those checks and editor diagnostics. VS Code's built-in HTML/CSS service originally reported 30 errors and 25 warnings from empty Mermaid style attributes in `index.html`; all five generated HTML pages now report zero errors and zero warnings. This fixes the generated markup instead of disabling validation.

The CodePen setup now passes twelve documentation/tool regressions, including exact form-payload serialization, a round-trip check of the Classic HTML copy box, and rejection of document wrappers in that copy. Its tree controls, prefill data, clipboard success, clipboard denial, and missing Clipboard API passed 34 browser checks at each of the desktop/mobile viewports; see [CodePenBrowser.json](../validation/CodePenBrowser.json). The Classic markup, placed in a normal document's body as the editor does, passed 27 checks per viewport while loading its actual configured HTTPS renderer; see [CodePenManualBrowser.json](../validation/CodePenManualBrowser.json). The earlier reconstructed HTML/CSS/JavaScript payload also passed 27 checks per viewport using the same pinned renderer; see [CodePenPayloadBrowser.json](../validation/CodePenPayloadBrowser.json).

The publisher encountered **Something Went Wrong** at CodePen's automatic prefill endpoint. That error did not identify a cause. Manual copying into a blank Pen bypasses that endpoint. Browser checks exercise the generated files, not CodePen's account/editor service; they do not publish a Pen or prove that Medium has accepted its embed. Saving a Pen and verifying it inside the actual story remain external publishing steps.

<!-- BEGIN RESULTS -->
| Profile | Container suite | Article checks | Standalone example |
|---|---|---|---|
| gcc17 | 27,073,587 checks passed | 6 snippets + 34,495 recipe checks passed | Compiled; execution blocked |
| clang17 | Compiled; execution blocked | 6 snippets + 34,495 recipe checks passed | Output matched |
| gcc20 | 27,073,587 checks passed | 6 snippets + 34,495 recipe checks passed | Output matched |
| gcc17_ubsan_traps | 27,073,587 checks passed | Compiled; execution blocked | Output matched |

All builds used strict compiler warnings, including `-Werror`. Windows reported WinError 4551 for blocked runs; those executables were not retried under renamed paths or with security policies disabled.

**Walkthrough model:** Passed 430847 walkthrough-model checks.

**Real browser:**
- Desktop: 27 checks at 1440 × 1080 pixels.
- Mobile: 27 checks at 390 × 844 pixels.

The browser checks exercise actual buttons and rendered SVGs, covering duplicate handling, lower/upper ranks, selection, missing ranks, invalid inputs, unique mode, SVG IDs, and page-width overflow. Desktop and mobile previews are saved in `validation/Medium-desktop.png` and `validation/Medium-mobile.png`.

**Code comments:** 3599 non-comment C++ tokens match the baseline. The optimized example assembly is byte-identical with `-std=c++17 -O2 -g0 -S`. This confirms that the explanatory comments add no generated instructions to that example; it is not a universal speed claim.

**Build files:** CMake configuration and the example target passed. The Code::Blocks project XML and its source paths were validated; an interactive IDE launch is not claimed.

**Benchmark:** five rotated fresh-process trials per mode, 300,000 input values per trial. All 15 raw/wrapper trial pairs produced matching checksums and remaining sizes. Timings are saved with the workload in `validation/Results.json`; performance varies by workload and toolchain.

**Publishing tools:** all five link-handling tests passed. The release check correctly refuses the current unpublished configuration until the repository, Medium, and hosted-demo URLs are supplied.

**Preservation:** all 22 original contribution files matched the saved baseline. The C++ runtime checks preceded the final MIT notice; comment-stripped tokens and optimized example assembly were checked unchanged after that notice was added.

**Scope:** the future GitHub Actions / GitLab CI jobs and live platform publication have not run locally. The checked-in articles use verified platform syntax, but the final Codeforces/Medium editor preview remains part of publishing.
<!-- END RESULTS -->
