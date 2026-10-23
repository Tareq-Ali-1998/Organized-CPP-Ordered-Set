"""Render the checked-in Mermaid sources to SVG and Medium-ready PNG images."""

import argparse
import hashlib
from html.parser import HTMLParser
import html
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]


class ResultParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'pre' and dict(attrs).get('id') == 'render-result':
            self.active = True

    def handle_endtag(self, tag):
        if tag == 'pre' and self.active:
            self.active = False

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)


def browser_path(supplied):
    candidates = [supplied, shutil.which('google-chrome'), shutil.which('chromium'),
                  shutil.which('chromium-browser'),
                  'C:/Program Files/Google/Chrome/Application/chrome.exe',
                  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe']
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(Path(candidate).resolve())
    raise RuntimeError('Chrome/Chromium is required; pass --browser PATH')


def run(browser, work, page, extra):
    args = [browser, '--headless', '--disable-gpu', '--disable-background-networking',
            '--disable-component-update', '--no-first-run', '--no-default-browser-check',
            '--window-size=1440,1500', '--user-data-dir=' + str(work/'profile'),
            '--virtual-time-budget=10000', *extra, page.as_uri()]
    result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8',
                            errors='replace', timeout=50)
    if result.returncode:
        raise RuntimeError('Browser render failed: ' + result.stderr[-1800:])
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser')
    args = parser.parse_args()
    browser = browser_path(args.browser)
    vendor = ROOT/'assets/vendor/mermaid.min.js'
    if not vendor.exists():
        raise RuntimeError('Run tools/fetch_mermaid.py first')
    diagrams = {file.stem: file.read_text(encoding='utf-8')
                for file in sorted((ROOT/'assets/diagrams').glob('*.mmd'))}
    source_data = json.dumps(diagrams).replace('<', '\\u003c')
    page = '''<!doctype html><meta charset="utf-8"><body>
<pre id="render-result">pending</pre>
<script src="VENDOR"></script>
<script>
mermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:'base',
    deterministicIds:true, deterministicIDSeed:'organized-cpp-ordered-set',
    themeVariables:{fontFamily:'Arial'},flowchart:{htmlLabels:false,useMaxWidth:false}});
(async () => {
    const output = {};
    try {
        for (const [name, source] of Object.entries(DIAGRAMS)) {
            output[name] = (await mermaid.render('diagram-' + name, source)).svg;
        }
        document.getElementById('render-result').textContent = JSON.stringify({status:'ok', diagrams:output});
    }
    catch (error) {
        document.getElementById('render-result').textContent = JSON.stringify({status:'error', message:String(error)});
    }
})();
</script></body>'''.replace('VENDOR', html.escape(vendor.as_uri(), quote=True)).replace('DIAGRAMS', source_data)
    with tempfile.TemporaryDirectory(prefix='organized-ordered-set-diagrams-') as temp:
        work = Path(temp)
        source = work/'render.html'
        source.write_text(page, encoding='utf-8')
        parsed = ResultParser()
        parsed.feed(run(browser, work, source, ['--dump-dom']))
        raw = ''.join(parsed.parts)
        if not raw or raw == 'pending':
            raise RuntimeError('Mermaid did not finish; no successful render is claimed')
        rendered = json.loads(raw)
        if rendered['status'] != 'ok':
            raise RuntimeError(rendered['message'])
        from PIL import Image, ImageChops
        manifest = {'renderer': 'Mermaid 11.12.0 in headless Chrome/Chromium', 'diagrams': {}}
        for name, svg in rendered['diagrams'].items():
            source_hash = hashlib.sha256(diagrams[name].encode()).hexdigest()
            svg = f'<!-- Mermaid source SHA256: {source_hash} -->\n' + svg
            (ROOT/f'assets/diagrams/{name}.svg').write_text(svg, encoding='utf-8', newline='\n')
            preview = work/(name+'.html')
            preview.write_text('<!doctype html><meta charset="utf-8"><style>'
                               'body{margin:0;padding:32px;background:white} '
                               'svg{width:1376px!important;max-width:none!important;height:auto}'
                               '</style>' + svg, encoding='utf-8')
            screenshot = work/(name+'.png')
            view_box = re.search(r'viewBox="([^"]+)"', svg)
            if not view_box:
                raise RuntimeError('Diagram has no viewBox: '+name)
            _, _, width, height = map(float, view_box.group(1).split())
            viewport_height = max(700, math.ceil(height * 1376 / width) + 150)
            run(browser, work, preview, ['--window-size=1440,' + str(viewport_height),
                                        '--screenshot=' + str(screenshot)])
            with Image.open(screenshot) as image:
                image = image.convert('RGB')
                bounds = ImageChops.difference(image, Image.new('RGB', image.size, 'white')).getbbox()
                if not bounds:
                    raise RuntimeError('Empty diagram screenshot: '+name)
                if bounds[3] >= image.height - 1:
                    raise RuntimeError('Diagram screenshot is clipped: '+name)
                image = image.crop((0, 0, image.width, min(image.height, bounds[3]+32)))
                target = ROOT/f'assets/medium/{name}.png'
                image.save(target)
                dimensions = list(image.size)
            manifest['diagrams'][name] = {
                'source_sha256': source_hash,
                'svg_sha256': hashlib.sha256(svg.encode()).hexdigest(),
                'png_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                'png_dimensions': dimensions,
            }
            print(f'Rendered {name}: SVG and {dimensions[0]} x {dimensions[1]} PNG', flush=True)
        (ROOT/'assets/diagrams/manifest.json').write_text(json.dumps(manifest, indent=4)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
