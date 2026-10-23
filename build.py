"""Build the independent publishing drafts, HTML walkthrough, and paste-ready C++."""

import argparse
import html
import json
from pathlib import Path
import re
from urllib.parse import urlparse

from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import CppLexer


ROOT = Path(__file__).resolve().parent
COMMENT_COLUMN = 52


def align_comments(source):
    # Shared, single-line example comments use one column in every publication.
    token = r'"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27|/\*.*?\*/|//[^\n]*'
    lines = []
    for line in source.split('\n'):
        for match in re.finditer(token, line):
            if match.group().startswith('//') and line[:match.start()].strip():
                code = line[:match.start()].rstrip()
                line = code.ljust(max(COMMENT_COLUMN, len(code)+2)) + match.group()
                break
        lines.append(line)
    return '\n'.join(lines)


def align_cpp_blocks(text):
    return re.sub(r'(```(?:cpp|c\+\+)\n)(.*?)(\n```)',
                  lambda match: match[1]+align_comments(match[2])+match[3], text, flags=re.S)


def stale_outputs(generated):
    return [name for name, content in generated.items()
            if not (ROOT/name).is_file() or (ROOT/name).read_text(encoding='utf-8') != content]


def stale_message(names):
    return ('Generated files need rebuilding:\n  ' + '\n  '.join(names)
            + '\nFrom the project folder, run: python build.py'
            + '\nOr from any folder: python "' + str(ROOT/'build.py') + '"'
            + '\nThen run the check again. Markdown PDF exports can also overwrite these'
            + '\nHTML files; open OrganizedOrderedSet.code-workspace to export into exports/.')

LAB = '''<section id="ordered-set-lab" class="lab" aria-labelledby="lab-title">
<h2 id="lab-title">Try the counting idea</h2>
<p class="lab-note">A schematic balanced search tree for learning rank and selection.
PBDS can choose a different balanced shape. This walkthrough uses ascending integer order.</p>
<p class="lab-note">On a small screen, swipe horizontally across the tree to read its nodes.</p>
<label for="lab-values">Values (up to 15 integers, separated by spaces or commas)</label>
<input id="lab-values" value="1, 2, 3, 5, 6, 7, 9" autocomplete="off">
<div class="lab-grid">
<label for="lab-mode">Container<select id="lab-mode"><option value="multi">Multiset: keep duplicates</option><option value="unique">Unique set</option></select></label>
<label for="lab-operation">Query<select id="lab-operation"><option value="select">Select sorted rank</option><option value="rank">Count values &lt; x</option><option value="upper">Count values &lt;= x</option></select></label>
<label for="lab-query">Rank or threshold<input id="lab-query" value="4" inputmode="numeric"></label>
</div>
<div class="lab-buttons"><button id="lab-run">Start query</button><button id="lab-next" disabled>Next step</button><button id="lab-all" class="secondary">Show all steps</button><button id="lab-reset" class="secondary">Rebuild tree</button></div>
<p id="lab-sorted" class="lab-note"></p>
<p class="legend"><span class="blue">Current node</span><span class="green">Counted or skipped group</span><span class="amber">Earlier path</span></p>
<p id="lab-status" class="status" role="status" aria-live="polite">Loading the local walkthrough…</p>
<div id="lab-tree" class="tree-panel" aria-label="Query tree diagram"></div>
<ol id="lab-trace" class="trace"></ol>
<noscript>The diagrams above remain readable. Enable JavaScript to step through a query.</noscript>
</section>'''


def source_code():
    header = (ROOT/'OrderedSet.hpp').read_text(encoding='utf-8')
    if not header.startswith('#pragma once\n\n'):
        raise ValueError('Unexpected header prefix')
    return header.removeprefix('#pragma once\n\n').rstrip()


def validate_urls(config, require_all=False):
    missing = []
    for field in ['repository_url', 'medium_url', 'interactive_url']:
        value = config.get(field, '')
        if not value:
            missing.append(field)
            continue
        parsed = urlparse(value)
        if (parsed.scheme != 'https' or not parsed.netloc or parsed.username or parsed.password
                or any(char.isspace() or char in '<>"`' for char in value)):
            raise ValueError(field + ' must be an absolute HTTPS URL without credentials')
    if require_all and missing:
        raise ValueError('Publishing links still needed: ' + ', '.join(missing))
    return missing


def paragraph_link(config, field, label):
    if config.get(field):
        return f'[{label}]({config[field]})'
    descriptions = {'repository_url': 'Repository', 'medium_url': 'Detailed Medium walkthrough',
                    'interactive_url': 'Interactive walkthrough'}
    return f'**{descriptions[field]}: publication URL pending.**'


def expand(template, config, examples, code):
    replacements = {
        'repository': paragraph_link(config, 'repository_url', 'Code, examples, and complete API reference'),
        'medium': paragraph_link(config, 'medium_url', 'Read the detailed visual walkthrough on Medium'),
        'interactive': paragraph_link(config, 'interactive_url', 'Open the interactive rank/select walkthrough') + '\n\n<!-- INTERACTIVE LAB -->',
        'implementation': '```c++\n' + code + '\n```',
    }
    def replace(match):
        name = match.group(1)
        if name.startswith('example:'):
            key = name.split(':', 1)[1]
            return f'<!-- example: {key} -->\n```cpp\n{examples[key]}\n```'
        if name.startswith('diagram:'):
            key = name.split(':', 1)[1]
            diagram = (ROOT/f'assets/diagrams/{key}.mmd').read_text(encoding='utf-8').rstrip()
            return f'<!-- diagram: {key} -->\n```mermaid\n{diagram}\n```'
        return replacements[name]
    return re.sub(r'\{\{([^{}]+)\}\}', replace, template)


def diagram_images(text, png=False):
    pattern = r'<!-- diagram: ([\w-]+) -->\n```mermaid\n.*?\n```'
    def replace(match):
        name = match.group(1)
        label = name.replace('-', ' ').capitalize()
        if png:
            return f'![{label} diagram](assets/medium/{name}.png)'
        svg = (ROOT/f'assets/diagrams/{name}.svg').read_text(encoding='utf-8')
        # Mermaid emits empty declarations such as style=";". Browsers ignore them,
        # but VS Code correctly flags the invalid CSS. No visible styling is removed.
        svg = re.sub(r'\sstyle="[\s;]*"', '', svg)
        # Separate Mermaid renders can reuse edge IDs. Scope every inline SVG's IDs.
        ids = set(re.findall(r'\bid="([^"]+)"', svg))
        mapping = {value: 'figure-'+name+'-'+value for value in ids}
        svg = re.sub(r'\bid="([^"]+)"', lambda item: 'id="'+mapping[item.group(1)]+'"', svg)
        if ids:
            pattern = r'#('+'|'.join(re.escape(value) for value in sorted(ids, key=len, reverse=True))+r')(?![\w-])'
            svg = re.sub(pattern, lambda item: '#'+mapping[item.group(1)], svg)
        svg = re.sub(r'(aria-labelledby|aria-describedby)="([^"]+)"',
                     lambda item: item.group(1)+'="'+' '.join(mapping.get(value, value) for value in item.group(2).split())+'"', svg)
        return f'<figure data-diagram="{name}" aria-label="{label}">\n{svg}\n</figure>'
    return re.sub(pattern, replace, text, flags=re.S)


def math_preview(text):
    # These drafts use simple inline formulas. Codeforces performs its own LaTeX rendering.
    pieces = re.split(r'(```[^\n]*\n.*?^```)', text, flags=re.M | re.S)
    def replace(match):
        expression = match.group(1)
        plain = expression.replace('\\log', 'log').replace('\\', '')
        return '<span class="math" title="' + html.escape(expression, quote=True) + '">' + html.escape(plain) + '</span>'
    for idx in range(0, len(pieces), 2):
        pieces[idx] = re.sub(r'\$([^$\n]+)\$', replace, pieces[idx])
    return ''.join(pieces)


def render_html(text, title, interactive=False, prefix=''):
    formatter = HtmlFormatter(nowrap=True)
    def color_code(code, language, attrs):
        if language in ('cpp', 'c++'):
            return highlight(code, CppLexer(), formatter)
        return html.escape(code)
    text = re.sub(r'<!-- example: \w+ -->\n', '', text)
    text = re.sub(r'<spoiler summary="([^"]+)">', r'<details><summary>\1</summary>', text)
    text = text.replace('</spoiler>', '</details>')
    text = text.replace('<!-- INTERACTIVE LAB -->', LAB if interactive else '')
    text = math_preview(text)
    md = MarkdownIt('commonmark', {'html': True, 'highlight': color_code}).enable('table')
    if not text.lstrip().startswith('# '):
        text = '# Organized C++ Ordered Set and Multiset\n\n' + text
    tokens = md.parse(text)
    if (len(tokens) > 5 and tokens[0].type == 'heading_open' and tokens[0].tag == 'h1'
            and tokens[3].type == 'heading_open' and tokens[3].tag == 'h2'):
        tokens[3].type, tokens[3].tag = 'paragraph_open', 'p'
        tokens[3].attrSet('class', 'subtitle')
        tokens[5].type, tokens[5].tag = 'paragraph_close', 'p'
    used = {}
    toc = []
    for idx, token in enumerate(tokens):
        if token.type == 'heading_open':
            label = tokens[idx+1].content
            slug = re.sub(r'[^\w -]', '', label.lower()).strip().replace(' ', '-')
            count = used.get(slug, 0)
            used[slug] = count+1
            anchor = slug + (f'-{count}' if count else '')
            token.attrSet('id', anchor)
            if token.tag == 'h2':
                toc.append(f'<a href="#{anchor}">{html.escape(label)}</a>')
    body = md.renderer.render(tokens, md.options, {})
    if interactive:
        toc.insert(0, '<a href="#ordered-set-lab">Try the tree walkthrough</a>')
    style = (ROOT/'assets/article.css').read_text(encoding='utf-8')
    style += '\n' + formatter.get_style_defs('pre')
    scripts = ''
    if interactive:
        scripts = ''.join(f'<script defer src="{prefix}assets/{path}"></script>\n'
                          for path in ['vendor/mermaid.min.js', 'demo-model.js', 'demo-ui.js'])
    navigation = ('<header class="topbar"><span class="brand">Organized C++ Ordered Set</span><nav>'
                  f'<a href="{prefix}index.html">Visual guide</a>'
                  f'<a href="{prefix}Codeforces.html">For contests</a>'
                  f'<a href="{prefix}docs/API.html">API</a></nav></header>')
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{html.escape(title)}</title><style>\n{style}\n</style>{scripts}</head>'
            f'<body>{navigation}<div class="layout"><aside class="toc"><strong>IN THIS GUIDE</strong>'
            + ''.join(toc) + f'</aside><article>{body}</article></div></body></html>\n')


def make_files(config=None):
    config = config or json.loads((ROOT/'publishing.json').read_text(encoding='utf-8'))
    validate_urls(config)
    examples = {name: align_comments(snippet) for name, snippet in
                json.loads((ROOT/'sources/examples.json').read_text(encoding='utf-8')).items()}
    code = source_code()
    medium = expand((ROOT/'sources/Medium.template.md').read_text(encoding='utf-8'), config, examples, code)
    cf = expand((ROOT/'sources/Codeforces.template.md').read_text(encoding='utf-8'), config, examples, code)
    cf = cf.replace('```cpp\n', '```c++\n')
    cf = re.sub(r'<!-- example: \w+ -->\n', '', cf)
    publish = diagram_images(medium, png=True).replace('<!-- INTERACTIVE LAB -->', '')
    publish = re.sub(r'<!-- example: \w+ -->\n', '', publish)
    example = (ROOT/'Example.cpp').read_text(encoding='utf-8')
    if example.count('#include "OrderedSet.hpp"') != 1:
        raise ValueError('Unexpected example include')
    standalone = example.replace('#include "OrderedSet.hpp"', code)
    readme = align_cpp_blocks((ROOT/'README.md').read_text(encoding='utf-8'))
    overview = (ROOT/'assets/diagrams/overview.mmd').read_text(encoding='utf-8').rstrip()
    readme = re.sub(r'<!-- BEGIN DIAGRAM overview -->.*?<!-- END DIAGRAM overview -->',
                    '<!-- BEGIN DIAGRAM overview -->\n```mermaid\n'+overview+'\n```\n<!-- END DIAGRAM overview -->', readme, flags=re.S)
    examples_doc = '# Examples\n\nInclude `OrderedSet.hpp` first. Body snippets go inside a function; recipe function definitions go above `main`. All indices are zero-based.\n\n'
    for name, snippet in examples.items():
        examples_doc += f'## {name}\n\n<!-- example: {name} -->\n```cpp\n{snippet}\n```\n\n'
    medium_html = render_html(diagram_images(medium), 'The Missing Index in C++ Sets', interactive=True)
    files = {
        'README.md': readme, 'OrderedSet.cpp': standalone,
        'Medium.md': medium, 'Medium.publish.md': publish, 'Codeforces.md': cf,
        'Medium.html': medium_html, 'index.html': medium_html,
        'Medium.publish.html': render_html(publish, 'The Missing Index in C++ Sets — publishing copy'),
        'Codeforces.html': render_html(cf, 'Organized C++ Ordered Set — Codeforces preview'),
        'docs/Examples.md': examples_doc,
        'docs/API.html': render_html((ROOT/'docs/API.md').read_text(encoding='utf-8'), 'Ordered set API', prefix='../'),
    }
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--release-check', action='store_true')
    args = parser.parse_args()
    config = json.loads((ROOT/'publishing.json').read_text(encoding='utf-8'))
    try:
        validate_urls(config, require_all=args.release_check)
    except ValueError as error:
        parser.error(str(error))
    mismatches = []
    for relative, content in make_files(config).items():
        target = ROOT/relative
        if args.check or args.release_check:
            if not target.exists() or target.read_text(encoding='utf-8') != content:
                mismatches.append(relative)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.is_file() or target.read_text(encoding='utf-8') != content:
                target.write_text(content, encoding='utf-8', newline='\n')
    if mismatches:
        raise SystemExit(stale_message(mismatches))
    print('Generated outputs are current.' if args.check or args.release_check else 'Built articles, HTML, API examples, README diagram, and standalone C++.')


if __name__ == '__main__':
    main()
