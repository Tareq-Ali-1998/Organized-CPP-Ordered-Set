"""Check link handling without writing fixture URLs into publication drafts."""

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import ROOT, make_files, validate_urls


class PublishingTests(unittest.TestCase):
    def setUp(self):
        self.config = {'repository_url':'https://github.com/example/ordered-set',
                       'medium_url':'https://medium.com/@example/ordered-set',
                       'interactive_url':'https://example.github.io/ordered-set/'}

    def test_unpublished_configuration_is_explicit(self):
        config = json.loads((ROOT/'publishing.json').read_text(encoding='utf-8'))
        missing = validate_urls(config)
        self.assertEqual(missing, [name for name in ['repository_url','medium_url','interactive_url'] if not config.get(name)])

    def test_release_rejects_missing_fields(self):
        config = self.config.copy()
        config['medium_url'] = ''
        with self.assertRaisesRegex(ValueError, 'medium_url'):
            validate_urls(config, require_all=True)

    def test_complete_links_are_accepted(self):
        self.assertEqual(validate_urls(self.config, require_all=True), [])

    def test_unsafe_or_incomplete_urls_are_rejected(self):
        for value in ['javascript:alert(1)', 'http://example.com', 'https://',
                      'https://user:password@example.com', 'https://example.com/\ntext',
                      'https://example.com/<script>']:
            with self.subTest(value=value):
                config = self.config.copy()
                config['medium_url'] = value
                with self.assertRaises(ValueError):
                    validate_urls(config)

    def test_links_reach_both_independent_drafts(self):
        files = make_files(self.config)
        self.assertIn(self.config['repository_url'], files['Medium.md'])
        self.assertIn(self.config['repository_url'], files['Codeforces.md'])
        self.assertIn(self.config['medium_url'], files['Codeforces.md'])
        self.assertIn(self.config['interactive_url'], files['Medium.md'])
        self.assertNotIn('publication URL pending', files['Codeforces.md'])
        self.assertNotIn('publication URL pending', files['Medium.md'])


if __name__ == '__main__':
    unittest.main()
