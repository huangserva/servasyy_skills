#!/usr/bin/env python3
"""File-based entry to the user's existing Hermes image backend."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prompt-file', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--aspect', choices=['1:1', '16:9', '9:16', '4:3', '3:4'], default='16:9')
    p.add_argument('--resolution', choices=['1k', '2k', '4k'], default='2k')
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()
    backend = Path.home() / '.hermes/skills/creative/image-generator/scripts/generate.py'
    if not backend.is_file():
        p.error(f'Existing backend is missing: {backend}')
    if not a.prompt_file.expanduser().is_file():
        p.error('Prompt file does not exist')
    prompt = a.prompt_file.expanduser().read_text(encoding='utf-8').strip()
    if not prompt:
        p.error('Prompt file is empty')
    out = a.output.expanduser().resolve()
    saved_prompt = out.with_suffix('.prompt.txt')
    metadata = out.with_suffix('.request.json')
    if any(x.exists() for x in [out, saved_prompt, metadata]):
        p.error('Output or sidecar already exists; choose a new filename')
    request = {'model': 'gpt-image-2', 'aspect': a.aspect, 'resolution': a.resolution,
               'output': str(out), 'backend': str(backend)}
    if a.dry_run:
        print(json.dumps({**request, 'prompt': prompt, 'sent': False}, ensure_ascii=False, indent=2))
        return
    from PIL import Image
    out.parent.mkdir(parents=True, exist_ok=True)
    with saved_prompt.open('x', encoding='utf-8') as f:
        f.write(prompt + '\n')
    with metadata.open('x', encoding='utf-8') as f:
        json.dump(request, f, ensure_ascii=False, indent=2)
    cmd = [sys.executable, str(backend), prompt, '--model', 'gpt-image-2',
           '--ratio', a.aspect, '--resolution', a.resolution, '--output', str(out)]
    result = subprocess.run(cmd, timeout=360)
    if result.returncode != 0 or not out.is_file():
        raise SystemExit('Generation failed; prompt and request retained. No alternative backend was used.')
    with Image.open(out) as im:
        im.load()
        w, h = im.size
    x, y = map(int, a.aspect.split(':'))
    print(json.dumps({'output': str(out), 'width': w, 'height': h,
                      'exact_aspect': w * y == h * x}, ensure_ascii=False))


if __name__ == '__main__':
    main()
