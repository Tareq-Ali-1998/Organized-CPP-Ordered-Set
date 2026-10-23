# Publishing this project

## Links to add later

The project has been pushed to [GitHub](https://github.com/Tareq-Ali-1998/Organized-CPP-Ordered-Set) and [GitLab](https://gitlab.com/tareqali591998/organized-cpp-ordered-set). GitHub is the primary repository linked from the articles. The [interactive guide](https://tareq-ali-1998.github.io/Organized-CPP-Ordered-Set/) and [Medium import page](https://tareq-ali-1998.github.io/Organized-CPP-Ordered-Set/Medium.publish.html) are live on GitHub Pages; both pages and all three article diagrams were checked with successful HTTP responses. The Medium story URL is still pending:

- [x] Create both repositories and add the actual GitHub URL to `repository_url` in `publishing.json`.
- [ ] Add the actual Medium story URL to `medium_url`.
- [x] Confirm the hosted website and add its actual URL to `interactive_url`.
- [ ] Run `python build.py` to put those links into both articles.
- [ ] After the Medium story and hosted guide exist, run `python build.py --release-check` before posting the Codeforces article. It rejects missing or invalid URLs and stale outputs.

Push the generated article with its confirmed interactive-guide link, wait for Pages to update, and import the hosted article into Medium. Publish the story when its content and outgoing links are ready. Then save its actual public story URL in `publishing.json`, rebuild, and finish Codeforces last. The release check is the final cross-platform link check; it does not prevent starting a Medium draft before that story has a public URL.

The Codeforces draft intentionally displays a pending Medium link until that real URL exists. The repository links point to the projects' default-branch views, so readers reach the current code as new commits are pushed. No unpublished article or hosting URL is guessed.

## GitHub and GitLab

The GitHub repository is named `Organized-CPP-Ordered-Set`; the GitLab project path is `organized-cpp-ordered-set`. The **contents of this folder** form each repository's root. The parent coding-session repository, `DS`, and `Contributions` are separate work and are not dependencies of this project.

The README has a fenced `mermaid` diagram, which [GitHub renders in Markdown files](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams). [GitLab Flavored Markdown also supports Mermaid](https://docs.gitlab.com/user/markdown/#mermaid). No screenshot is needed for that README diagram. The exported SVG and PNG versions are included for other platforms.

The project includes verification configurations for GitHub Actions and GitLab CI, an MIT license, examples, a full API reference, CMake and Code::Blocks files, and local test scripts. Both CI configurations check generated outputs, publishing/build behavior, full C++ profiles, the JavaScript model, and the CMake example. GitLab saves JSON reports as job artifacts even if a check fails, using the [documented artifacts setting](https://docs.gitlab.com/ci/yaml/#artifactswhen). A compatible runner must be available for CI to execute. Actual hosted CI runs are not claimed until a repository exists and runs them.

Commit the generated articles, `index.html`, other named article previews, and the complete `assets/` directory alongside their source inputs. Consumers can read the guide immediately after downloading the project. The ignored `exports/`, build products, virtual environment, and local Markdown PDF review copies do not belong in the published repository. The supplied CI configurations verify the project; they do not deploy Pages or post articles.

The `.gitattributes` file keeps text line endings stable across Windows and Linux, so diagram/provenance hash checks survive a checkout. `.nojekyll` marks the prebuilt website for GitHub Pages without a Jekyll conversion. For a live tutorial URL, configure Pages after creating the repository; merely clicking an HTML file in the repository viewer shows its source rather than launching the website.

`index.html` and `Medium.html` contain the same interactive tutorial. This project's live site is served by [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site). [GitLab Pages](https://docs.gitlab.com/user/project/pages/) is an alternative if separately configured; mirroring the Git repository there does not enable a second website automatically. Keep the `assets` directory beside the HTML files. Static files alone cannot guarantee that Medium will embed an arbitrary hosting URL; a normal link works independently of embed support. The `repository_url` field points to the primary GitHub repository, and the README links to its GitLab mirror.

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

Use `Medium.publish.md` as the publishing source and `Medium.publish.html` as the complete static article with PNG diagrams. `Medium.md` retains Mermaid diagram sources. Medium's Write editor does not turn a local HTML or Markdown file attachment into a finished story. You do not need to retype the article paragraph by paragraph: import a public webpage URL, or copy the rendered article into a draft.

Pasting HTML source into Medium will not install the website or execute the tutorial's JavaScript. Copying rendered text can help transfer prose, but images and code blocks still need checking in Medium's own editor. Colors, layout, and custom CSS from the local preview are not promised to survive. The PNG diagrams retain their colors because those colors are part of the images.

### Recommended: import the hosted article

Medium's [Import a story tool](https://help.medium.com/hc/en-us/articles/214550207-Importing-a-post-to-Medium) accepts a public article URL. The files are already prepared; hosting makes that HTML and its images available to the importer.

1. Build and push the current files, including the updated title and repository links, to GitHub. GitLab can receive the same commit.
2. In the GitHub repository, open **Settings → Pages**. Choose **Deploy from a branch**, branch **main**, folder **/(root)**, then **Save**. These are the [GitHub Pages branch-publishing settings](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site). No additional site generator is needed: this project includes prebuilt HTML and `.nojekyll`.
3. Wait for deployment and open the actual website URL shown by GitHub. Confirm that both its main page and `Medium.publish.html` load, including the images. Do not use the repository's `github.com/.../blob/...` source-view URL as the article URL.
4. Save the confirmed main website URL in `interactive_url` in `publishing.json`, rebuild, verify, and push. Wait for the updated article to deploy so its interactive-guide link is filled before importing.
5. In Medium, open **Stories → Import a story**, paste the public URL ending in `/Medium.publish.html`, click **Import**, then **See your story**. This creates an imported draft; the earlier manually started draft can remain saved.
6. Review the title, subtitle, all three diagrams, captions, code blocks, repository/interactive links, and final AI-assistance line. Medium applies its own formatting. Importing is a best-effort conversion, not a guarantee that every element transfers correctly. The importer also sets a canonical link to the original page.
7. Publish the reviewed story. Save its actual public Medium URL in `medium_url`, rebuild, and finish the Codeforces article last.

The website URL is filled in only after its deployment is confirmed. A file on your computer is not a public URL, and pushing HTML into a repository does not by itself enable Pages hosting. Medium does not run the website's JavaScript; the story links to the interactive page.

### Fallback: copy the complete rendered article

If import fails, use Medium's [documented manual migration process](https://help.medium.com/hc/en-us/articles/360033931713-Trouble-importing-content-using-the-import-tool). Open `Medium.publish.html` in a browser, select the article body from the opening paragraph through the final attribution, and copy it. Exclude the navigation/sidebar and the title/subtitle if those are already in the draft. Paste into the draft with normal **Ctrl+V** to retain available formatting; **Ctrl+Shift+V** strips formatting.

Review headings and links, restore any missing images, and repair code blocks with Medium's **{ }** control. You can transfer the whole body in one paste; the smaller paragraph-by-paragraph steps are optional. The [code-block guide](https://help.medium.com/hc/en-us/articles/35756844492439-Using-code-blocks-and-inline-code) documents the controls. Keep the full implementation in the repository and the smaller examples in the story.

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
