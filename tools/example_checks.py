"""Compile the exact article snippets and compare its recipes with brute force."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECIPE_TESTS = (ROOT/"tests/RecipeChecks.inc").read_text(encoding="utf-8")

SNIPPET_OUTPUTS = {
    'QuickStart': '3 4 2 7 2 4 2 3 1 0 2 5',
    'RawPBDS': '2 5',
    'Construction': '2 2 4 8 3 1',
    'Descending': '9 2 4 3 0',
    'CustomKeys': 'Ali Tareq 2 100',
    'NarrowId': '5',
}

def require(condition,message):
    if not condition:
        raise RuntimeError(message)


def published_tests(article):
    snippets = dict(re.findall(r'<!-- example: (\w+) -->\n```cpp\n(.*?)\n```',
                               article, flags=re.S))
    require(set(snippets) == set(SNIPPET_OUTPUTS) | {'Inversions', 'SlidingMedian'},
            'Unexpected or missing article snippets')
    source = '#include "Published.hpp"\n\nusing namespace std;\n\n'
    source += snippets['Inversions'] + '\n\n' + snippets['SlidingMedian'] + '\n\n'
    source += RECIPE_TESTS + '\n'
    for name in SNIPPET_OUTPUTS:
        source += f'void {name}() {{\n\n{snippets[name]}\n\n}}\n\n'
    source += 'int main() {\n\n    try {\n'
    for name, expected in SNIPPET_OUTPUTS.items():
        source += ('        {\n'
                   '            ostringstream captured;\n'
                   '            streambuf* old = cout.rdbuf(captured.rdbuf());\n'
                   f'            {name}();\n'
                   '            cout.rdbuf(old);\n'
                   '            istringstream input(captured.str());\n'
                   '            vector<string> values{istream_iterator<string>(input), {}};\n'
                   f'            istringstream reference("{expected}");\n'
                   '            vector<string> expected{istream_iterator<string>(reference), {}};\n'
                   f'            Check(values == expected, "{name} output differs");\n'
                   '        }\n')
    source += ('        ExhaustiveRecipes();\n'
               '        cout << "Passed 6 runnable snippets and " << recipeChecks;\n'
               '        cout << " recipe checks.\\n";\n'
               '    }\n'
               '    catch (const exception& error) {\n'
               '        cerr << error.what() << "\\n";\n'
               '        return 1;\n'
               '    }\n'
               '    return 0;\n\n}\n')
    return source
