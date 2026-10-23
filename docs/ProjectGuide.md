# Finding your way around

To use the C++ container, take `OrderedSet.hpp`. To explore the tree, open `index.html` with a browser. Neither action needs Python, CMake, Node.js, a server, or a build step. Keep the downloaded folder together so the local assets remain available.

## Why more than one article file?

| File | Audience and purpose |
|---|---|
| `index.html` | The interactive website: colored explanations, diagrams, and query buttons. This is the main browser entry point. |
| `Medium.html` | The same interactive website under an article-friendly filename. Its contents match `index.html`. |
| `Medium.md` | The long article in Markdown, retaining editable Mermaid diagram blocks. |
| `Medium.publish.md` | The story-preparation copy with PNG diagrams instead of Mermaid source. |
| `Medium.publish.html` | The complete static article with PNG diagrams. Copy its rendered content, or host it and give its public URL to Medium's importer. It is not a local file attachment to upload in Write. |
| `Codeforces.md` | The shorter contest article in Codeforces Markdown, including math and a full-code spoiler. Paste this version into the Codeforces editor. |
| `Codeforces.html` | A local preview for reading. Codeforces itself renders the final math and spoiler. |

The HTML pages are already generated and committed. Readers do **not** need to run `build.py` to make links or buttons work. Public repository/story/demo links stay visibly pending until their real URLs are added to `publishing.json`.

## Code, helpers, and inputs

| File or folder | What it does | Who needs it? |
|---|---|---|
| `OrderedSet.hpp` | The reusable C++17 implementation. | Anyone using the container. |
| `Example.cpp` / `Example.out` | A short usage program and its expected output. | Someone learning the interface. |
| `OrderedSet.cpp` | The same implementation plus the example driver in one pasteable file. | Contest submissions; replace the example driver with your solution. |
| `build.py` | Reads the header, templates, examples, and links; regenerates articles, HTML previews, examples, the README diagram, and the standalone C++ copy. It writes only changed outputs. | Maintainers after editing a source. |
| `verify.py` | Checks generated copies and local assets, compiles and runs C++ reference tests and article examples, compares benchmark results, and runs the independent JavaScript model tests when Node is available. | Maintainers checking a change. |
| `CMakeLists.txt` | Optional C++ build instructions for CMake: exposes the header as a target, builds the example, and optionally registers the reference tests. It does not build the website. | People who prefer CMake over a direct `g++` command. |
| `OrganizedOrderedSet.cbp` | A Code::Blocks project for the example. | Code::Blocks users. |
| `sources/Medium.template.md` | The editable prose for the long article, with placeholders for shared examples and diagrams. | Article maintainers. |
| `sources/Codeforces.template.md` | The editable contest article. Its audience and wording remain separate from Medium. | Article maintainers. |
| `sources/examples.json` | The shared C++ snippets. Trailing output comments align in one column across the published copies. | Example maintainers. |
| `publishing.json` | The real repository, Medium story, and hosted-demo URLs. Empty means not published yet. | The publisher. |
| `assets/demo-model.js` | Builds a small schematic balanced tree and calculates rank/select steps. This teaches the counting idea; it is not the C++ PBDS implementation. | Loaded automatically by the interactive HTML. |
| `assets/demo-ui.js` | Connects inputs and buttons to that model and updates the diagram. | Loaded automatically by the interactive HTML. |
| `assets/vendor/mermaid.min.js` | The pinned local Mermaid diagram renderer and its retained license. | Loaded automatically by the interactive HTML. |
| `assets/article.css` | Colors, layout, code styling, and print layout. | Loaded by generated pages; optional for Markdown PDF. |
| `assets/diagrams/` / `assets/medium/` | Mermaid sources, SVG exports, image hashes, and Medium-ready PNGs. | Maintainers and the Medium publisher. |
| `tests/` | C++ reference tests, JavaScript model tests, and Python publishing/build checks. | Maintainers and CI. |
| `validation/` | Saved test results and browser previews, including any blocked executions. | Reviewers of the evidence. |
| `.github/workflows/verify.yml` / `.gitlab-ci.yml` | Automatic checks after pushing to the respective host. Neither publishes the article or deploys the website. | Repository maintainers. |

The files in `tools/` have narrower jobs:

| Tool | Purpose |
|---|---|
| `fetch_mermaid.py` | Fetch the pinned public renderer and verify its provenance when refreshing that dependency. Normal builds use the copy already present. |
| `render_diagrams.py` | Render changed `.mmd` files into SVG and PNG with Chrome/Chromium, then record hashes. |
| `browser_check.py` | Exercise the actual tutorial buttons and diagrams at desktop and mobile widths, and save screenshots. |
| `example_checks.py` | Produce a C++ harness for the published snippets and brute-force recipe comparisons. Used by `verify.py`. |
| `check_code_equivalence.py` | Compare C++ tokens and example assembly against an explicitly supplied baseline header. |
| `summarize_validation.py` | Refresh the written validation summary from saved result files. |

## Editing and rebuilding

Edit `OrderedSet.hpp` for container code, `Example.cpp` for the driver, article prose in `sources/*.template.md`, examples in `sources/examples.json`, and API contracts in `docs/API.md`. Generated article files carry copies of those inputs, so edits made directly to a generated file will be replaced on the next build.

From the project folder:

```bash
python -m pip install -r requirements-dev.txt
python build.py
python tests/PublishingTests.py
python tests/DocumentationTests.py
python verify.py
```

`python build.py --check` checks freshness without writing anything. `python verify.py --documents-only` checks the documents without compiling C++. `--full` enables the additional compiler profiles. `--require-execution` makes blocked or unavailable runtime checks fail the command, as the CI jobs require. `--report validation/MyRun.json` keeps a separate report.

Running `verify.py` by absolute path from a parent folder works too. The scripts locate their inputs beside themselves, rather than assuming the terminal's current directory is the project.

### “Generated files need rebuilding”

This means a generated copy differs from what the current sources produce. It can follow a template/header edit, an incomplete build, or an extension exporting over a generated HTML filename. It does not mean a C++ test returned a wrong answer: document checks happen first.

Save any intentional prose edits back into the appropriate source template, run `python build.py`, then rerun the check. The error prints the affected filenames and the full builder path. The verifier reports the mismatch; it does not silently replace files.

For Markdown PDF, open `OrganizedOrderedSet.code-workspace`, or open this project folder itself in VS Code. Both include settings that send extension exports to the ignored `exports/` folder. Those settings do not automatically apply when editing from the parent coding-session folder. Older Markdown PDF exports beside their `.md` inputs are local review artifacts and are excluded from this project's Git files; they are not maintained by `build.py`.

The generated diagrams omit empty Mermaid `style=";"` and `style=""` attributes, which otherwise cause CSS squiggles in VS Code. Browser checks still exercise the rendered diagrams and their controls.

## If you prefer CMake

You can still compile directly with `g++`; CMake is optional. With a GCC toolchain configured, this builds just the example:

```bash
cmake -S . -B build -DBUILD_TESTING=OFF
cmake --build build
```

The executable goes under `build/`; its exact location depends on the generator. On Windows, choose a GCC-compatible generator such as MinGW Makefiles if CMake would otherwise select MSVC, because MSVC does not supply GNU PBDS. Leave `BUILD_TESTING` enabled to build the C++ reference test target as well, then run `ctest --test-dir build --output-on-failure`.

## Publishing

Follow [Publishing.md](Publishing.md) for GitHub, GitLab, Codeforces, and Medium. For Medium, the recommended bulk-transfer route is to host `Medium.publish.html` and use **Stories → Import a story** with its public URL. Copying the complete rendered article is the fallback; retyping it section by section is unnecessary. Review the converted story before publishing.

Publishing the repository and publishing the articles are separate steps. Remember to add the real URLs to `publishing.json` when they exist; the release check deliberately refuses missing links. The local HTML is a complete offline website, while the story platforms use their own editors.
