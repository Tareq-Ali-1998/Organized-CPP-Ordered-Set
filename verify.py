"""Validate the standalone project, publication copies, and reference-tested containers."""

import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from build import ROOT, make_files, source_code, stale_outputs, stale_message
from tools.example_checks import published_tests


EXPECTED = 'Passed 384000 randomized operations, 265720 exhaustive trace states, and 27073587 checks.'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(args, **kwargs):
    result = subprocess.run([str(item) for item in args], capture_output=True, text=True,
                            encoding='utf-8', errors='replace', timeout=180, **kwargs)
    require(result.returncode == 0, f'Command failed: {args}\n{result.stdout}\n{result.stderr}')
    return result.stdout


def execute(args, report, **kwargs):
    try:
        return command(args, **kwargs)
    except OSError as error:
        if getattr(error, 'winerror', None) != 4551:
            raise
        report['execution_limitations'].append({'program': Path(args[0]).name,
            'reason': 'Windows Application Control blocked execution (WinError 4551)'})
        return None


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.resources = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if tag in ('img', 'script', 'link'):
            self.resources.append(attrs.get('src') or attrs.get('href', ''))


def check_documents():
    generated = make_files()
    mismatches = stale_outputs(generated)
    if mismatches:
        raise RuntimeError(stale_message(mismatches))
    code = source_code()
    cf_blocks = re.findall(r'```c\+\+\n(.*?)\n```', generated['Codeforces.md'], re.S)
    require(cf_blocks[-1] == code, 'Published implementation differs from the header')
    require('#include "OrderedSet.hpp"' not in generated['OrderedSet.cpp'], 'Standalone code has a local dependency')
    require('$O(\\log(n+1))$' in generated['Codeforces.md'], 'Codeforces LaTeX is missing')
    require(generated['Codeforces.md'].count('<spoiler ') == generated['Codeforces.md'].count('</spoiler>') == 1,
            'Unbalanced Codeforces spoiler')
    require('```mermaid' not in generated['Medium.publish.md'], 'Medium publishing copy contains unrendered Mermaid')
    require('```mermaid' in generated['README.md'], 'README Mermaid source is missing')
    for name in ['Medium.md', 'Codeforces.md']:
        text = generated[name]
        require('years ago' not in text.lower() and '88193' not in text, 'Article refers to the old post')
        require(text.rstrip().endswith('*By Tareq Ali. This article was organized with AI assistance.*'),
                'Article attribution is missing or not at the end')
    api = (ROOT/'docs/API.md').read_text(encoding='utf-8')
    methods = ('empty size key_comp begin end cbegin cend rbegin rend crbegin crend '
               'insert emplace find contains count lower_bound upper_bound equal_range '
               'erase erase_one erase_by_order find_by_order order_of_key order_of_key_upper '
               'count_range index_of first_index last_index at front back clear swap').split()
    for name in methods:
        require(re.search(r'\b'+name+r'\s*\(', api) is not None, 'Missing API documentation: '+name)
    manifest = json.loads((ROOT/'assets/diagrams/manifest.json').read_text(encoding='utf-8'))
    for name, record in manifest['diagrams'].items():
        for field, path in [('source_sha256', ROOT/f'assets/diagrams/{name}.mmd'),
                            ('svg_sha256', ROOT/f'assets/diagrams/{name}.svg'),
                            ('png_sha256', ROOT/f'assets/medium/{name}.png')]:
            require(sha(path) == record[field], 'Stale diagram export: '+name)
    for name in [relative for relative in generated if relative.endswith('.html')]:
        parser = PageParser()
        parser.feed(generated[name])
        require(len(parser.ids) == len(set(parser.ids)), 'Duplicate HTML IDs in '+name)
        for path in parser.resources:
            require(not path.startswith(('http:', 'https:', '//')), 'HTML requests an external asset: '+path)
            require((ROOT/name).parent.joinpath(path).is_file(), 'Missing local HTML asset: '+path)
        require(re.search(r'\sstyle="[\s;]*"', generated[name]) is None,
                'Empty SVG/CSS style in '+name)
    for unit in ET.parse(ROOT/'OrganizedOrderedSet.cbp').findall('.//Unit'):
        require((ROOT/unit.attrib['filename']).is_file(), 'Broken Code::Blocks project unit')
    provenance = json.loads((ROOT/'assets/vendor/provenance.json').read_text(encoding='utf-8'))
    require(sha(ROOT/'assets/vendor/mermaid.min.js') == provenance['bundle_sha256'], 'Mermaid bundle changed')
    return generated, {'generated_files': list(generated), 'documented_method_names': len(methods),
                       'rendered_diagrams': len(manifest['diagrams']), 'offline_assets_present': True}


def check_preserved_contributions():
    baseline = json.loads((ROOT/'validation/ContributionsBaseline.json').read_text(encoding='utf-8'))
    if not (ROOT.parent/'Contributions').exists():
        return {'status': 'not applicable in a standalone checkout'}
    for name, expected in baseline.items():
        require((ROOT.parent/name).is_file() and sha(ROOT.parent/name) == expected,
                'Original Contributions content changed: '+name)
    return {'status': 'unchanged', 'files': len(baseline)}


def save(report, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=4)+'\n', encoding='utf-8', newline='\n')


def node_command(supplied=None):
    node = supplied or shutil.which('node')
    env = os.environ.copy()
    if not node and os.name == 'nt' and shutil.which('code'):
        candidate = Path(shutil.which('code')).resolve().parent.parent/'Code.exe'
        if candidate.exists():
            node = str(candidate)
            env['ELECTRON_RUN_AS_NODE'] = '1'
    return node, env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full', action='store_true')
    parser.add_argument('--documents-only', action='store_true')
    parser.add_argument('--require-execution', action='store_true')
    parser.add_argument('--node')
    parser.add_argument('--report', default='validation/Results.json',
                        help='JSON report path, relative to this project unless absolute')
    args = parser.parse_args()
    generated, documents = check_documents()
    preserved = check_preserved_contributions()
    report_path = ROOT/args.report
    if args.documents_only:
        print('Documents, diagram exports, API coverage, and preserved Contributions checked.')
        return

    report = {'status': 'running', 'started_at_utc': datetime.now(timezone.utc).isoformat(),
              'documents': documents, 'preserved_contributions': preserved,
              'profiles': [], 'execution_limitations': [], 'benchmark': {}, 'sha256': {}}
    save(report, report_path)
    try:
        profiles = [('gcc17', 'g++', 'c++17', False)]
        if args.full:
            profiles += [('clang17', 'clang++', 'c++17', False), ('gcc20', 'g++', 'c++20', False),
                         ('gcc17_ubsan_traps', 'g++', 'c++17', True)]
        with tempfile.TemporaryDirectory(prefix='organized-cpp-ordered-set-') as temp:
            work = Path(temp)
            (work/'Published.hpp').write_text(source_code()+'\n', encoding='utf-8')
            (work/'ArticleTests.cpp').write_text(published_tests(generated['Medium.md']), encoding='utf-8')
            for name, compiler_name, standard, sanitized in profiles:
                compiler = shutil.which(compiler_name)
                require(compiler is not None, 'Missing compiler: '+compiler_name)
                flags = [compiler, '-std='+standard, '-O1' if sanitized else '-O2',
                         '-Wall', '-Wextra', '-Wshadow', '-pedantic', '-Werror']
                if sanitized:
                    flags += ['-D_GLIBCXX_ASSERTIONS', '-fsanitize=undefined',
                              '-fsanitize-undefined-trap-on-error', '-fno-sanitize=vptr']
                result = {'name': name, 'compiler': command([compiler, '--version']).splitlines()[0], 'flags': flags[1:]}
                report['profiles'].append(result)
                print(name+': container suite...', flush=True)
                suite = work/(name+'-suite.exe')
                command(flags+[ROOT/'tests/OrderedSetTests.cpp', '-o', suite])
                output = execute([suite], report)
                require(output is None or output.strip() == EXPECTED, 'Unexpected container-suite result')
                result['container_suite'] = output.strip() if output is not None else 'compiled; execution blocked'
                save(report, report_path)

                article = work/(name+'-articles.exe')
                command(flags+[work/'ArticleTests.cpp', '-o', article])
                output = execute([article], report)
                result['article_examples'] = output.strip() if output is not None else 'compiled; execution blocked'
                require(output is None or output.strip() == 'Passed 6 runnable snippets and 34495 recipe checks.',
                        'Unexpected recipe-check result')
                standalone = work/(name+'-example.exe')
                command(flags+[ROOT/'OrderedSet.cpp', '-o', standalone])
                output = execute([standalone], report)
                if output is not None:
                    require(output.split() == (ROOT/'Example.out').read_text(encoding='utf-8').split(), 'Standalone output differs')
                result['standalone_example'] = 'matched Example.out' if output is not None else 'compiled; execution blocked'
                print(name+': '+result['container_suite']+'; '+result['article_examples'], flush=True)
                save(report, report_path)

            benchmark = work/'benchmark.exe'
            compiler = shutil.which('g++')
            command([compiler, '-std=c++17', '-O2', '-DNDEBUG', ROOT/'tests/OrderedSetBenchmark.cpp', '-o', benchmark])
            modes = ['raw_set', 'set', 'raw_multi64', 'multi64', 'raw_multi32', 'multi32']
            trials = {name: [] for name in modes}
            for repeat in range(5 if args.full else 1):
                for mode in modes[repeat:]+modes[:repeat]:
                    output = execute([benchmark, mode, '300000'], report)
                    if output is None:
                        break
                    trials[mode].append(json.loads(output))
                else:
                    continue
                break
            pairs_checked = 0
            for raw, wrapper in zip(modes[::2], modes[1::2]):
                for left, right in zip(trials[raw], trials[wrapper]):
                    require((left['checksum'], left['remaining']) == (right['checksum'], right['remaining']), 'Benchmark pair differs')
                    pairs_checked += 1
            report['benchmark'] = {'n': 300000, 'trials': trials, 'matching_trial_pairs': pairs_checked,
                'median_total_seconds': {mode: statistics.median(run['total_seconds'] for run in runs)
                                         for mode, runs in trials.items() if runs},
                'note': 'One seeded workload; object sizes exclude allocated nodes; no universal speed claim.'}
            save(report, report_path)

        node, env = node_command(args.node)
        if node:
            report['walkthrough_model'] = command([node, ROOT/'tests/DemoModelTests.js'], env=env).strip()
        else:
            report['walkthrough_model'] = 'not run: Node.js unavailable'
            report['execution_limitations'].append({'program': 'walkthrough model', 'reason': 'Node.js unavailable'})
        report['status'] = 'completed_with_execution_limitations' if report['execution_limitations'] else 'passed'
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = str(error)
        raise
    finally:
        for relative in ['OrderedSet.hpp', 'OrderedSet.cpp', 'Medium.md', 'Codeforces.md', 'sources/examples.json',
                         'tests/OrderedSetTests.cpp', 'tests/OrderedSetBenchmark.cpp', 'assets/demo-model.js', 'verify.py']:
            report['sha256'][relative] = sha(ROOT/relative)
        report['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
        save(report, report_path)
    print(report['status']+': '+str(report_path), flush=True)
    if args.require_execution and report['execution_limitations']:
        raise SystemExit('Required executions were blocked or unavailable; see '+str(report_path))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError, OSError) as error:
        raise SystemExit('Verification stopped: '+str(error)) from None
