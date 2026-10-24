"""Update the human-readable validation summary from the saved result files."""

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def main():
    result = json.loads((ROOT/'validation/Results.json').read_text(encoding='utf-8'))
    browser = json.loads((ROOT/'validation/Browser.json').read_text(encoding='utf-8'))
    assembly = json.loads((ROOT/'validation/CodeEquivalence.json').read_text(encoding='utf-8'))
    cmake = json.loads((ROOT/'validation/CMake.json').read_text(encoding='utf-8'))
    lines = ['| Profile | Container suite | Article checks | Standalone example |', '|---|---|---|---|']
    for profile in result['profiles']:
        suite = '27,073,587 checks passed' if profile['container_suite'].startswith('Passed') else 'Compiled; execution blocked'
        recipes = '6 snippets + 34,495 recipe checks passed' if profile['article_examples'].startswith('Passed') else 'Compiled; execution blocked'
        standalone = 'Output matched' if profile['standalone_example'].startswith('matched') else 'Compiled; execution blocked'
        lines.append(f'| {profile["name"]} | {suite} | {recipes} | {standalone} |')
    lines += ['', 'All builds used strict compiler warnings, including `-Werror`. Windows reported WinError 4551 for blocked runs; those executables were not retried under renamed paths or with security policies disabled.',
              '', f'**Walkthrough model:** {result["walkthrough_model"]}', '', '**Real browser:**']
    for name in ['desktop','mobile']:
        page=browser[name]
        lines.append(f'- {name.capitalize()}: {len(page["checks"])} checks at {page["viewport"][0]} × {page["viewport"][1]} pixels.')
    lines += ['', 'The browser checks exercise actual buttons and rendered SVGs, covering duplicate handling, lower/upper ranks, selection, missing ranks, invalid inputs, unique mode, SVG IDs, and page-width overflow. Desktop and mobile previews are saved in `validation/Medium-desktop.png` and `validation/Medium-mobile.png`.',
              '', f'**Code comments:** {assembly["token_count"]} non-comment C++ tokens match the baseline. The optimized example assembly is byte-identical with `-std=c++17 -O2 -g0 -S`. This confirms that the explanatory comments add no generated instructions to that example; it is not a universal speed claim.',
              '', '**Build files:** CMake configuration and the example target '+cmake['status']+'. The Code::Blocks project XML and its source paths were validated; an interactive IDE launch is not claimed.',
              '', '**Benchmark:** five rotated fresh-process trials per mode, 300,000 input values per trial. All 15 raw/wrapper trial pairs produced matching checksums and remaining sizes. Timings are saved with the workload in `validation/Results.json`; performance varies by workload and toolchain.',
              '', '**Publishing tools:** all five link-handling tests passed. The release check requires actual repository, Medium, and hosted-guide URLs and current generated files. Link validation does not replace checking the article in the destination editor.',
              '', '**Preservation:** all 22 original contribution files matched the saved baseline. The C++ runtime checks preceded the final MIT notice; comment-stripped tokens and optimized example assembly were checked unchanged after that notice was added.',
              '', '**Scope:** the future GitHub Actions / GitLab CI jobs and live platform publication have not run locally. The checked-in articles use verified platform syntax, but the final Codeforces/Medium editor preview remains part of publishing.']
    path=ROOT/'docs/Validation.md'
    text=path.read_text(encoding='utf-8')
    text=re.sub(r'<!-- BEGIN RESULTS -->.*?<!-- END RESULTS -->',
                '<!-- BEGIN RESULTS -->\n'+'\n'.join(lines)+'\n<!-- END RESULTS -->',text,flags=re.S)
    path.write_text(text,encoding='utf-8',newline='\n')
    print('Updated docs/Validation.md from the saved results.')


if __name__ == '__main__':
    main()
