"""Re-render retained lesson HTML without changing teaching data or its compute AST.

Development/showcase operation, never assessment generation. Retains the original
generation and trace separately and stamps both generation and renderer revisions.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from check_entropy_oracle import _runtime_payload
from runtime import render, _serialize


class Node:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    def text(self):
        return ''.join(x.text() if isinstance(x, Node) else x for x in self.children).strip()

    def find(self, tag=None, cls=None):
        result = []
        if (tag is None or self.tag == tag) and (cls is None or cls in self.attrs.get('class', '').split()):
            result.append(self)
        for child in self.children:
            if isinstance(child, Node):
                result.extend(child.find(tag, cls))
        return result


class Tree(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs)
        self.stack[-1].children.append(n)
        if tag not in ('meta', 'input', 'br', 'hr', 'img', 'link'):
            self.stack.append(n)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def recover(html):
    tree = Tree(html).root
    spec = copy.deepcopy(_runtime_payload(html)['spec'])
    lesson_notes = tree.find(cls='lesson-notes')
    if not lesson_notes:
        raise ValueError('Only retained lesson-notes format is supported; original left unchanged')
    notes = lesson_notes[0].find('p')
    spec.update(version=1, title=tree.find('h1')[0].text(),
                audience=notes[0].text().removeprefix('Audience:').strip(),
                plan=notes[1].text().removeprefix('Plan:').strip(),
                starting_point=dict(idea=tree.find(cls='lead')[0].text(),
                                    why=tree.find(cls='why')[0].text().removeprefix('Why it matters:').strip(),
                                    explanation=tree.find(cls='mechanism-note')[0].text()),
                limitation=tree.find(cls='limitation')[0].find('p')[0].text())
    spec['symbols'] = [dict(zip(('symbol','meaning','units'), [n.text() for n in row.find('td')]))
                       for row in tree.find(cls='notation')[0].find('tbody')[0].find('tr')]
    labels = {'FROM PAPER':'excerpt', 'TOY EXAMPLE':'example',
              'SIMPLIFICATION':'simplification', 'UNVERIFIED':'unverified'}
    spec['grounding'] = []
    for item in tree.find(cls='grounding-list')[0].find('li'):
        label = item.find('span')[0].text()
        paper, claim = item.find('strong')[0].text(), item.find('p')[0].text()
        locator = ''.join(x for x in item.children if isinstance(x, str)).strip().lstrip('—').strip()
        spec['grounding'].append(dict(paper=paper, locator=locator, support=labels[label], claim=claim))
    return spec


def rerender(html):
    payload = _runtime_payload(html)
    spec = recover(html)
    # The renderer compiles a syntactic scaffold; it is never executed. Replace
    # its inert JSON with the unchanged original computational payload/AST.
    spec['compute_js'] = 'function compute(inputs) { return {}; }'
    result = render(spec)
    result, count = re.subn(r'(<script type="application/json" id="runtime-data">).*?(</script>)',
                           lambda m: m.group(1)+_serialize(payload)+m.group(2), result, count=1, flags=re.S)
    if count != 1 or _runtime_payload(result) != payload:
        raise ValueError('Retained computational payload changed')
    if recover(result) != {k:v for k,v in spec.items() if k != 'compute_js'}:
        raise ValueError('Retained teaching fields changed')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--producing-sha', required=True)
    args = p.parse_args()
    original = args.source.read_text(encoding='utf-8')
    rendered = rerender(original)
    if args.source.resolve() == args.output.resolve():
        raise ValueError('Never overwrite the retained original')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding='utf-8')
    print(json.dumps(dict(label='re-rendered, NOT freshly generated',
                         generating_sha=args.producing_sha,
                         renderer_sha=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
                         renderer_worktree_changes=subprocess.check_output(['git','diff','--name-only','--','runtime.py','templates'], cwd=ROOT, text=True).splitlines(),
                         source=str(args.source), output=str(args.output),
                         original_sha256=hashlib.sha256(original.encode()).hexdigest(),
                         rendered_sha256=hashlib.sha256(rendered.encode()).hexdigest(),
                         computational_payload_unchanged=True, teaching_fields_unchanged=True), indent=2))


if __name__ == '__main__':
    main()
