#!/usr/bin/env python3
"""Reuse the installed Claude library; no credentials or styles are duplicated."""
import argparse
from pathlib import Path
import sys

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--content-file', type=Path)
    p.add_argument('--style', default='notion')
    p.add_argument('--layout', default='single')
    p.add_argument('--aspect', default='16:9', choices=['16:9','21:9','1:1','3:4','4:3','9:16'])
    p.add_argument('--output', type=Path)
    p.add_argument('--provider', default='auto', choices=['auto','google-local','modelscope','zimage','volcengine','apimart'])
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--list-styles', action='store_true')
    a = p.parse_args()
    shared = Path.home() / '.claude/skills/shared-lib'
    if not (shared / 'illustration/generator.py').is_file():
        p.error(f'Claude illustration library is missing: {shared}')
    sys.path.insert(0, str(shared))
    from illustration import IllustrationGenerator
    g = IllustrationGenerator(provider=a.provider)
    if a.list_styles:
        print('\n'.join(sorted(g.list_styles())))
        return
    if a.style not in g.list_styles():
        p.error(f'Unknown style: {a.style}; use --list-styles')
    if a.layout not in g.list_layouts():
        p.error(f'Unknown layout: {a.layout}')
    if not a.content_file or (not a.dry_run and not a.output):
        p.error('--content-file and (unless --dry-run) --output are required')
    content = a.content_file.expanduser().read_text(encoding='utf-8').strip()
    if not content:
        p.error('The content file is empty')
    prompt = g.build_prompt(content=content, style=a.style, layout=a.layout)
    if a.dry_run:
        print(prompt)
        return
    output = a.output.expanduser().resolve()
    prompt_file = output.with_suffix('.prompt.txt')
    if output.exists() or prompt_file.exists():
        p.error('Output or prompt already exists; choose a new output filename')
    output.parent.mkdir(parents=True, exist_ok=True)
    prompt_file.write_text(prompt, encoding='utf-8')
    _, provider = g.generate(content=content, style=a.style, layout=a.layout,
                             aspect_ratio=a.aspect, output_path=str(output), max_retries=1)
    print(f'OUTPUT={output}\nSTYLE={a.style}\nPROVIDER={provider}\nREQUESTED_ASPECT={a.aspect}')
    from PIL import Image
    with Image.open(output) as im:
        w, h = im.size
    x, y = map(int, a.aspect.split(':'))
    print(f'ACTUAL_SIZE={w}x{h}\nEXACT_ASPECT={w*y == h*x}')

if __name__ == '__main__':
    main()
