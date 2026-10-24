"""Exercise the real HTML walkthrough in a browser and save desktop/mobile previews."""

import json
import argparse
import base64
import re
import subprocess
from pathlib import Path
import tempfile
import time
import websocket
from urllib.parse import urlsplit

from render_diagrams import ROOT, browser_path


TEST_SCRIPT = r'''
const browserErrors = [];
window.addEventListener('error', event => browserErrors.push(event.message || 'Resource loading failed'));
window.addEventListener('unhandledrejection', event => browserErrors.push(String(event.reason)));
window.addEventListener('load', async () => {
    const results = [];
    const report = document.createElement('pre');
    report.id = 'render-result';
    report.style.display = 'none';
    document.body.appendChild(report);
    function Check(ok, label) {
        if (!ok) throw new Error(label);
        results.push(label);
    }
    function SetInput(id, value) { document.getElementById(id).value = value; }
    function Click(id) { document.getElementById(id).click(); }
    async function WaitFor(test) {
        for (let i = 0; i < 500; i++) {
            if (test()) return;
            await new Promise(resolve => setTimeout(resolve, 10));
        }
        throw new Error('Timed out waiting for a rendered query');
    }
    async function Query(values, mode, operation, value, expected) {
        SetInput('lab-values', values); SetInput('lab-mode', mode);
        SetInput('lab-operation', operation); SetInput('lab-query', value);
        const previous = document.getElementById('lab-tree').getAttribute('data-render-revision');
        Click('lab-run'); Click('lab-all');
        Check(document.getElementById('lab-status').textContent === expected, expected);
        await WaitFor(() => document.getElementById('lab-tree').getAttribute('data-render-revision') !== previous);
        Check(!document.getElementById('lab-tree').hasAttribute('data-render-error'), 'No Mermaid error: ' + expected);
    }
    try {
        await WaitFor(() => document.querySelector('#lab-tree svg'));
        Check(innerWidth === EXPECT_WIDTH, 'Viewport matches requested width');
        Check(document.querySelectorAll('figure[data-diagram] svg').length === EXPECT_FIGURES, 'Static diagram count matches the page');
        await Query('1,2,3,5,6,7,9', 'multi', 'select', '4', 'Rank 4 contains 6.');
        Check(document.getElementById('lab-trace').children.length === 3, 'Select trace has the expected three decisions');
        await Query('1,2,3,5,6,7,9', 'multi', 'rank', '6', '4 entries are strictly before 6.');
        await Query('7,2,7,5', 'multi', 'rank', '7', '2 entries are strictly before 7.');
        await Query('7,2,7,5', 'multi', 'upper', '7', '4 entries are before or equal to 7.');
        await Query('7,2,7,5', 'multi', 'select', '4', 'No such rank: find_by_order returns end().');
        await Query('7,2,7,5', 'unique', 'select', '2', 'Rank 2 contains 7.');
        Check(document.getElementById('lab-sorted').textContent === 'Sorted values: [2, 5, 7]', 'Unique mode removes equivalent values');
        await Query('', 'multi', 'select', '0', 'No such rank: find_by_order returns end().');
        Check(document.getElementById('lab-tree').textContent.includes('Empty container'), 'Empty container is drawn');
        SetInput('lab-values', '1,bad,3'); Click('lab-reset');
        Check(document.getElementById('lab-status').textContent.includes('whole numbers'), 'Invalid input is explained');
        SetInput('lab-values', '<script>'); Click('lab-reset');
        Check(document.getElementById('lab-status').textContent.includes('whole numbers'), 'Markup input is rejected as data');
        await Query('1,2,3,5,6,7,9', 'multi', 'select', '4', 'Rank 4 contains 6.');
        const ids = [...document.querySelectorAll('[id]')].map(node => node.id);
        Check(new Set(ids).size === ids.length, 'No duplicate HTML/SVG IDs');
        Check(document.documentElement.scrollWidth <= innerWidth + 1, 'No page-width overflow');
        Check(document.querySelectorAll('script[src^="http"]').length === 0, 'All scripts are local');
        Check(browserErrors.length === 0, 'No browser script or resource errors');
        report.textContent = JSON.stringify({status:'passed', viewport:[innerWidth,innerHeight], checks:results});
    }
    catch (error) {
        report.textContent = JSON.stringify({status:'failed', message:String(error), checks:results});
    }
});
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--page', default='index.html')
    parser.add_argument('--report', default='validation/Browser.json')
    parser.add_argument('--screenshot-prefix', default='validation/Medium')
    parser.add_argument('--no-screenshots', action='store_true')
    args = parser.parse_args()
    browser = browser_path(None)
    source = ROOT/args.page
    original = source.read_text(encoding='utf-8')
    figures = original.count('<figure data-diagram=')
    def local_resource(match):
        value = match[2]
        if urlsplit(value).scheme or value.startswith(('#', '//')):
            return match.group()
        return match[1]+'="'+(source.parent/value).resolve().as_uri()+'"'
    original = re.sub(r'\b(src|href)="([^"]+)"', local_resource, original)
    reports = {}
    with tempfile.TemporaryDirectory(prefix='organized-ordered-set-browser-') as temporary:
        work = Path(temporary)
        process = subprocess.Popen([browser, '--headless', '--disable-gpu', '--disable-background-networking',
            '--disable-component-update', '--no-first-run', '--no-default-browser-check',
            '--remote-debugging-port=0', '--user-data-dir='+str(work/'profile'), 'about:blank'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        connection = None
        try:
            active = work/'profile/DevToolsActivePort'
            for _ in range(150):
                if active.exists():
                    break
                if process.poll() is not None:
                    raise RuntimeError('Browser exited before its local debugging connection was ready')
                time.sleep(.1)
            port, endpoint = active.read_text().splitlines()[:2]
            connection = websocket.create_connection('ws://127.0.0.1:'+port+endpoint,
                                                     suppress_origin=True, timeout=30)
            next_id = 0
            session = None
            def call(method, params=None, attached=True):
                nonlocal next_id
                next_id += 1
                message = {'id':next_id, 'method':method, 'params':params or {}}
                if attached and session:
                    message['sessionId'] = session
                connection.send(json.dumps(message))
                while True:
                    response = json.loads(connection.recv())
                    if response.get('id') == next_id:
                        if 'error' in response:
                            raise RuntimeError(str(response['error']))
                        return response.get('result', {})
            target = call('Target.createTarget', {'url':'about:blank'}, False)['targetId']
            session = call('Target.attachToTarget', {'targetId':target, 'flatten':True}, False)['sessionId']
            call('Page.enable')
            def evaluate(expression):
                result = call('Runtime.evaluate', {'expression':expression, 'returnByValue':True})
                if result.get('exceptionDetails'):
                    raise RuntimeError(str(result['exceptionDetails']))
                return result.get('result', {}).get('value')
            def wait(expression):
                for _ in range(300):
                    value = evaluate(expression)
                    if value:
                        return value
                    time.sleep(.1)
                raise RuntimeError('Browser check timed out: '+expression)
            for name, width, height in [('desktop',1440,1080), ('mobile',390,844)]:
                call('Emulation.setDeviceMetricsOverride', {'width':width, 'height':height,
                    'deviceScaleFactor':1, 'mobile':name=='mobile'})
                page = work/(name+'-check.html')
                checks = TEST_SCRIPT.replace('EXPECT_WIDTH',str(width)).replace('EXPECT_FIGURES',str(figures))
                harness = original.replace('</body>', '<script>'+checks+'</script></body>')
                page.write_text(harness, encoding='utf-8')
                call('Page.navigate', {'url':page.as_uri()})
                payload = wait("document.getElementById('render-result')?.textContent")
                result = json.loads(payload)
                reports[name] = result
                if result['status'] != 'passed':
                    raise RuntimeError(json.dumps(result))
                if not args.no_screenshots:
                    preview = work/(name+'.html')
                    preview.write_text(original, encoding='utf-8')
                    call('Page.navigate', {'url':preview.as_uri()})
                    wait("document.querySelector('#lab-tree svg') && document.readyState === 'complete'")
                    png = call('Page.captureScreenshot', {'format':'png', 'captureBeyondViewport':False})['data']
                    (ROOT/f'{args.screenshot_prefix}-{name}.png').write_bytes(base64.b64decode(png))
                print(name+': passed '+str(len(result['checks']))+' real-browser checks at '+str(width)+'px.', flush=True)
        finally:
            if connection:
                connection.close()
            process.terminate()
            process.wait(timeout=10)
    (ROOT/args.report).write_text(json.dumps(reports, indent=4)+'\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
