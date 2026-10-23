"""Compare a baseline header with this revision, ignoring comments, then compare example assembly."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def tokens(source):
    pattern = r'"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27|//[^\n]*|/\*[\s\S]*?\*/|\w+|[^\s]'
    return [part for part in re.findall(pattern, source)
            if not part.startswith(('//', '/*'))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    args = parser.parse_args()
    before = args.baseline.read_text(encoding='utf-8')
    after = (ROOT/'OrderedSet.hpp').read_text(encoding='utf-8')
    if tokens(before) != tokens(after):
        raise SystemExit('Non-comment C++ tokens differ')
    compiler = shutil.which('g++')
    if not compiler:
        raise SystemExit('g++ is required for the assembly comparison')
    driver = (ROOT/'Example.cpp').read_text(encoding='utf-8').replace('"OrderedSet.hpp"', '"Variant.hpp"')
    assemblies = []
    with tempfile.TemporaryDirectory(prefix='ordered-set-code-equivalence-') as temporary:
        work = Path(temporary)
        (work/'Probe.cpp').write_text(driver, encoding='utf-8')
        for idx, content in enumerate([before, after]):
            (work/'Variant.hpp').write_text(content, encoding='utf-8')
            target = work/(str(idx)+'.s')
            result = subprocess.run([compiler, '-std=c++17', '-O2', '-g0', '-S', str(work/'Probe.cpp'), '-o', str(target)],
                                    capture_output=True, text=True, timeout=90)
            if result.returncode:
                raise SystemExit(result.stderr)
            assemblies.append(target.read_bytes())
    if assemblies[0] != assemblies[1]:
        raise SystemExit('Example assembly differs; inspect before claiming generated-code equivalence')
    report = {'non_comment_cpp_tokens_identical': True,
              'token_count': len(tokens(after)),
              'token_sha256': hashlib.sha256('\n'.join(tokens(after)).encode()).hexdigest(),
              'example_optimized_assembly_identical': True,
              'assembly_bytes': len(assemblies[0]),
              'assembly_sha256': hashlib.sha256(assemblies[0]).hexdigest(),
              'compiler': subprocess.check_output([compiler,'--version'],text=True).splitlines()[0],
              'flags': '-std=c++17 -O2 -g0 -S',
              'note': 'Focused comments leave this example’s generated code unchanged. '
                      'This is not a universal benchmark comparison against other containers.'}
    (ROOT/'validation/CodeEquivalence.json').write_text(json.dumps(report,indent=4)+'\n',encoding='utf-8')
    print('Non-comment C++ tokens and optimized example assembly are identical.')


if __name__ == '__main__':
    main()
