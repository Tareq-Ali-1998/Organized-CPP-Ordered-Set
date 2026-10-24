"""Regressions for shared code formatting, generated pages, and maintenance commands."""

import contextlib
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build
from tools.check_code_equivalence import tokens


class CodeBlocks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag == 'pre':
            self.current = []

    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == 'pre' and self.current is not None:
            self.blocks.append(''.join(self.current))
            self.current = None


class DocumentationTests(unittest.TestCase):
    def test_comment_alignment_keeps_cpp_tokens_and_literal_slashes(self):
        source = ('cout << "https://example.com"; // URL\n'
                  "char slash = '/';    // slash\n"
                  'cout << "escaped \\\" // literal"; // output\n'
                  'cout << 5; /* block // comment */ // 5\n'
                  '    // Full-line explanation stays indented.\n')
        aligned = build.align_comments(source)
        self.assertEqual(tokens(source), tokens(aligned))
        self.assertEqual(aligned.splitlines()[-1], '    // Full-line explanation stays indented.')
        self.assertEqual(aligned.splitlines()[0][build.COMMENT_COLUMN:], '// URL')
        self.assertTrue(aligned.splitlines()[2].endswith('// output'))
        self.assertEqual(build.align_comments(aligned), aligned)

    def test_long_lines_keep_a_gap_instead_of_joining_code_and_comment(self):
        code = 'cout << "' + 'a'*70 + '";'
        self.assertEqual(build.align_comments(code+' // output'), code+'  // output')

    def test_shared_examples_are_canonically_aligned(self):
        examples = json.loads((build.ROOT/'sources/examples.json').read_text(encoding='utf-8'))
        positions = set()
        for name, snippet in examples.items():
            with self.subTest(name=name):
                self.assertEqual(snippet, build.align_comments(snippet))
                positions.update(line.index('//') for line in snippet.splitlines()
                                 if '//' in line and not line.lstrip().startswith('//'))
        self.assertEqual(positions, {build.COMMENT_COLUMN})

    def test_html_code_text_matches_the_formatted_cpp_snippets(self):
        files = build.make_files()
        examples = json.loads((build.ROOT/'sources/examples.json').read_text(encoding='utf-8'))
        for name in ['index.html', 'Medium.html', 'Medium.publish.html', 'Codeforces.html']:
            page = CodeBlocks()
            page.feed(files[name])
            self.assertIn(examples['QuickStart']+'\n', page.blocks, name)
            for block in page.blocks:
                self.assertEqual(block, build.align_comments(block), name)
        self.assertEqual(files['index.html'], files['Medium.html'])

    def test_embedded_diagrams_have_no_empty_css_declarations(self):
        files = build.make_files()
        for name in ['index.html', 'Medium.html']:
            self.assertEqual(files[name].count('<figure data-diagram='), 3)
            self.assertIsNone(re.search(r'\sstyle="[\s;]*"', files[name]))
        self.assertNotIn('id="ordered-set-lab"', files['Medium.publish.html'])

    def test_build_writes_changed_files_only_and_check_never_writes(self):
        with tempfile.TemporaryDirectory(prefix='ordered-set-build-test-') as temp:
            root = Path(temp)
            (root/'publishing.json').write_text('{}', encoding='utf-8')
            target = root/'preview.html'
            with patch.object(build, 'ROOT', root), patch.object(build, 'make_files', return_value={'preview.html':'ready'}):
                with patch.object(sys, 'argv', ['build.py']), contextlib.redirect_stdout(io.StringIO()):
                    build.main()
                    os.utime(target, (1234567890, 1234567890))
                    before = target.stat().st_mtime_ns
                    build.main()
                self.assertEqual(target.stat().st_mtime_ns, before)
                target.write_text('stale', encoding='utf-8')
                with patch.object(sys, 'argv', ['build.py', '--check']):
                    with self.assertRaisesRegex(SystemExit, 'preview.html'):
                        build.main()
                self.assertEqual(target.read_text(encoding='utf-8'), 'stale')

    def test_verifier_explains_stale_output_without_a_traceback(self):
        script = ('import sys, runpy; from unittest.mock import patch; import build; '
                  'sys.argv = ["verify.py", "--documents-only"]; '
                  'mock = patch.object(build, "stale_outputs", return_value=["Medium.html"]); '
                  'mock.start(); runpy.run_path(str(build.ROOT/"verify.py"), run_name="__main__")')
        result = subprocess.run([sys.executable, '-c', script], cwd=build.ROOT,
                                capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(result.returncode, 1)
        self.assertIn('Medium.html', result.stderr)
        self.assertIn('python build.py', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_documents_verify_when_started_in_the_parent_folder(self):
        result = subprocess.run([sys.executable, str(build.ROOT/'verify.py'), '--documents-only'],
                                cwd=build.ROOT.parent, capture_output=True, text=True,
                                encoding='utf-8', timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)


if __name__ == '__main__':
    unittest.main()
