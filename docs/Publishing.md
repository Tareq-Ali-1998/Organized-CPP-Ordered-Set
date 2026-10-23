# Publishing this project

## Links to add later

The project has been pushed to [GitHub](https://github.com/Tareq-Ali-1998/Organized-CPP-Ordered-Set) and [GitLab](https://gitlab.com/tareqali591998/organized-cpp-ordered-set). GitHub is the primary repository linked from the articles. The Medium story and hosted interactive-guide URLs are still pending:

- [x] Create both repositories and add the actual GitHub URL to `repository_url` in `publishing.json`.
- [ ] Add the actual Medium story URL to `medium_url`.
- [ ] Add the hosted interactive HTML URL to `interactive_url`.
- [ ] Run `python build.py` to put those links into both articles.
- [ ] After the Medium story and hosted guide exist, run `python build.py --release-check` before posting the Codeforces article. It rejects missing or invalid URLs and stale outputs.

Draft the Medium story first, arrange hosting for the interactive guide, and publish the story when its content and outgoing links are ready. Then save its actual public story URL in `publishing.json`, rebuild, and finish Codeforces last. The release check is the final cross-platform link check; it does not prevent starting a Medium draft before that story has a public URL.

The Codeforces draft intentionally displays a pending Medium link until that real URL exists. The repository links point to the projects' default-branch views, so readers reach the current code as new commits are pushed. No unpublished article or hosting URL is guessed.

## GitHub and GitLab

The GitHub repository is named `Organized-CPP-Ordered-Set`; the GitLab project path is `organized-cpp-ordered-set`. The **contents of this folder** form each repository's root. The parent coding-session repository, `DS`, and `Contributions` are separate work and are not dependencies of this project.

The README has a fenced `mermaid` diagram, which [GitHub renders in Markdown files](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams). [GitLab Flavored Markdown also supports Mermaid](https://docs.gitlab.com/user/markdown/#mermaid). No screenshot is needed for that README diagram. The exported SVG and PNG versions are included for other platforms.

The project includes verification configurations for GitHub Actions and GitLab CI, an MIT license, examples, a full API reference, CMake and Code::Blocks files, and local test scripts. Both CI configurations check generated outputs, publishing/build behavior, full C++ profiles, the JavaScript model, and the CMake example. GitLab saves JSON reports as job artifacts even if a check fails, using the [documented artifacts setting](https://docs.gitlab.com/ci/yaml/#artifactswhen). A compatible runner must be available for CI to execute. Actual hosted CI runs are not claimed until a repository exists and runs them.

Commit the generated articles, `index.html`, other named article previews, and the complete `assets/` directory alongside their source inputs. Consumers can read the guide immediately after downloading the project. The ignored `exports/`, build products, virtual environment, and local Markdown PDF review copies do not belong in the published repository. The supplied CI configurations verify the project; they do not deploy Pages or post articles.

The `.gitattributes` file keeps text line endings stable across Windows and Linux, so diagram/provenance hash checks survive a checkout. `.nojekyll` marks the prebuilt website for GitHub Pages without a Jekyll conversion. For a live tutorial URL, configure Pages after creating the repository; merely clicking an HTML file in the repository viewer shows its source rather than launching the website.

`index.html` and `Medium.html` contain the same interactive tutorial. They can be hosted as static files using [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site) or [GitLab Pages](https://docs.gitlab.com/user/project/pages/) after configuring hosting in the future repository. Keep the `assets` directory beside them. Static files alone cannot guarantee that Medium will embed an arbitrary hosting URL; a normal link works independently of embed support. The `repository_url` field can point to either host; choose the primary one for the articles and add the other repository as a mirror link in the README once both exist.

## Codeforces

Suggested title: **Organized C++ Ordered Set and Multiset**.

Paste the contents of `Codeforces.md` into the body. It is a distinct contest-focused article, with zero-based usage, complexity, duplicate handling, a sliding-window example, and the complete copyable implementation inside a spoiler.

Codeforces uses modified Markdown, with LaTeX for math. The source uses `$...$` inline formulas, fenced `c++` blocks, and `<spoiler summary="...">` for the implementation, following the [Codeforces formatting tutorial](https://codeforces.com/blog/entry/104522?locale=en). It is not a pure LaTeX document. Use the editor preview before publishing.

Do not paste the complete `index.html` or `Codeforces.html` into a blog post. Publish `Codeforces.md` through the site's editor, and link to the hosted interactive guide. Its HTML preview is for local reading, not an import file that installs this website inside Codeforces.

`Codeforces.html` is a local reading preview. Its simple formulas are typeset as readable text by this project’s builder; Codeforces performs the real LaTeX rendering on the site. Mermaid fences and custom scripts are not inserted into the Codeforces draft.

The introduction mentions returning after a long competitive-programming break. It does not refer to an earlier post that will be deleted. The last line discloses AI assistance.

## Medium

Title: **C++ Ordered Set and Multiset: A Practical Guide to GNU PBDS**.

Subtitle: **Rank queries, duplicate handling, and a reusable C++17 interface**.

A post on Medium is called a **story**. Clicking **Write** creates a draft; Medium saves drafts automatically. Its [first-story guide](https://help.medium.com/hc/en-us/articles/225168768-Writing-and-publishing-your-first-story) explains the editor and the separate final publishing step.

The story editor is a visual document editor. Write normal text, then select it to apply bold, headings, and links. The title is the first title line; select the line below it and use the smaller **T** to make the subtitle if needed. Medium's [editor guide](https://help.medium.com/hc/en-us/articles/215194537-Using-the-story-editor) documents these controls. Medium does not natively render LaTeX expressions; this story already writes complexities such as `O(log(n + 1))` as ordinary inline code, so no math extension is needed.

Use `Medium.publish.md` as the publishing copy and `Medium.publish.html` as a formatted reading/copying aid. `Medium.md` is the source version that keeps Mermaid diagrams available on GitHub. Medium is a rich-text editor; copying a Markdown file is not a guarantee that every formatting element will be imported automatically.

Pasting HTML source into Medium will not install the website or execute the tutorial's JavaScript. Copying rendered text can help transfer prose, but images and code blocks still need checking in Medium's own editor. Colors, layout, and custom CSS from the local preview are not promised to survive. The PNG diagrams retain their colors because those colors are part of the images.

1. Add the title, subtitle, and prose in the Medium editor.
2. Insert code through Medium’s code-block control or its triple-backtick shortcut. The [Medium code-block guide](https://help.medium.com/hc/en-us/articles/35756844492439-Using-code-blocks-and-inline-code) documents the editor controls.
3. Upload the matching PNG at each figure position. Set descriptive alt text and the caption printed after the figure in the article.
4. Add the actual repository and interactive-walkthrough links. Keep the full implementation in the repository; the Medium article explains it through smaller examples.
5. Check the story on a narrow screen and confirm the final AI-assistance disclosure remains at the end.

| Figure | Upload | Meaning |
|---|---|---|
| 1 | [subtree-sizes.png](../assets/medium/subtree-sizes.png) | Subtree sizes and a route toward six |
| 2 | [select-walk.png](../assets/medium/select-walk.png) | The three selection cases |
| 3 | [duplicate-ids.png](../assets/medium/duplicate-ids.png) | How insertion IDs distinguish equivalent occurrences |

Medium supports PNG images; it does not run custom story scripts. Its [embed documentation](https://help.medium.com/hc/en-us/articles/214981378-Using-embeds) describes supported URL-based embeds and the restriction on scripts. The colored PNGs belong in the story; the step-by-step interaction belongs in the linked HTML walkthrough. [Medium’s image guide](https://help.medium.com/hc/en-us/articles/215679797-Using-images) covers images, captions, and alt text.

## Exporting and rebuilding

Open the ready-rendered HTML files directly to read them without network access. The interactive page loads its checked-in Mermaid bundle locally; the C++ implementation has no dependency on those assets.

No build is needed to read a fresh checkout. The builder is needed only after source edits or when adding real publishing links. See [the project guide](ProjectGuide.md) for the role of each script and a stale-file troubleshooting example.

For Markdown PDF, use `Medium.publish.md` when you want a static export with images already rendered. Its image paths are relative to the Markdown file. `Codeforces.md` can also be exported for review, but the site’s preview is authoritative for its custom spoiler markup. Use `assets/article.css` as an optional extension stylesheet.

Open `OrganizedOrderedSet.code-workspace`, or open this project folder itself, for the supplied local export settings. Exports go into `exports/`, which keeps Markdown PDF output separate from the generated HTML files. Settings in this folder do not automatically apply when editing from its parent workspace. An extension export named `Medium.html` can otherwise replace the interactive page and cause the verifier to report a stale output. Use `index.html` as the main interactive entry point.

Edit the article templates in `sources`, the implementation in `OrderedSet.hpp`, and examples in `sources/examples.json`. `python build.py` regenerates the article copies, HTML files, README diagram, and standalone program. It writes only inside this folder.

After changing a `.mmd` diagram, install `requirements-render.txt` if needed and run `python tools/render_diagrams.py`. It needs a normal Chrome/Chromium installation and preserves browser sandboxing. The committed renderer is pinned; its license and provenance are retained. SVG and PNG outputs are checked against their source hashes.
