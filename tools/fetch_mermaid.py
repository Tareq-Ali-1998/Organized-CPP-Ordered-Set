"""Fetch one pinned Mermaid bundle and its license; verify npm's tarball integrity."""

import base64
import hashlib
import io
import json
from pathlib import Path
import tarfile
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
VERSION = '11.12.0'


def read(url):
    with urllib.request.urlopen(url, timeout=45) as response:
        return response.read()


def main():
    metadata = json.loads(read(f'https://registry.npmjs.org/mermaid/{VERSION}'))
    assert metadata['name'] == 'mermaid' and metadata['version'] == VERSION
    url = metadata['dist']['tarball']
    assert url == f'https://registry.npmjs.org/mermaid/-/mermaid-{VERSION}.tgz'
    payload = read(url)
    integrity = metadata['dist']['integrity']
    algorithm, expected = integrity.split('-', 1)
    assert algorithm == 'sha512'
    assert base64.b64encode(hashlib.sha512(payload).digest()).decode() == expected
    with tarfile.open(fileobj=io.BytesIO(payload), mode='r:gz') as archive:
        bundle = archive.extractfile('package/dist/mermaid.min.js').read()
        licenses = [entry for entry in archive.getnames()
                    if entry.lower() in ('package/license', 'package/license.md', 'package/license.txt')]
        if licenses:
            license_text = archive.extractfile(licenses[0]).read()
        else:
            revision = metadata['gitHead']
            assert len(revision) == 40 and all(c in '0123456789abcdef' for c in revision)
            license_text = read(f'https://raw.githubusercontent.com/mermaid-js/mermaid/{revision}/LICENSE')
    target = ROOT / 'assets/vendor'
    target.mkdir(parents=True, exist_ok=True)
    (target/'mermaid.min.js').write_bytes(bundle)
    (target/'MERMAID-LICENSE.txt').write_bytes(license_text)
    provenance = {
        'package': 'mermaid', 'version': VERSION, 'source': url,
        'npm_integrity': integrity,
        'bundle_sha256': hashlib.sha256(bundle).hexdigest(),
        'license_sha256': hashlib.sha256(license_text).hexdigest(),
    }
    (target/'provenance.json').write_text(json.dumps(provenance, indent=4)+'\n', encoding='utf-8')
    print(f'Fetched Mermaid {VERSION}: {len(bundle)} bytes; npm integrity verified.')


if __name__ == '__main__':
    main()
