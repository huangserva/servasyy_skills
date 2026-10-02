#!/usr/bin/env python3
"""Store reusable image prompts with category, provenance and approval status."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--title', required=True)
    p.add_argument('--category', required=True, choices=['article', 'design', 'portrait', 'art', 'scene', 'edit'])
    p.add_argument('--prompt-file', type=Path, required=True)
    p.add_argument('--tag', action='append', default=[])
    p.add_argument('--image', type=Path)
    p.add_argument('--source', default='')
    p.add_argument('--model', default='unspecified')
    p.add_argument('--status', choices=['draft', 'approved'], default='draft')
    p.add_argument('--feedback', default='')
    p.add_argument('--store', type=Path, default=Path(__file__).resolve().parents[1] / 'collection')
    a = p.parse_args()
    if not a.title.strip():
        p.error('Title is empty')
    if not a.prompt_file.expanduser().is_file():
        p.error('Prompt file does not exist')
    prompt = a.prompt_file.expanduser().read_text(encoding='utf-8').strip()
    if not prompt:
        p.error('Prompt file is empty')
    if a.status == 'approved' and not a.feedback.strip():
        p.error('Approved entries require the user feedback verbatim')
    image = a.image.expanduser().resolve() if a.image else None
    if image and not image.is_file():
        p.error('Image does not exist')
    data = {'schema_version': 1, 'title': a.title.strip(), 'category': a.category,
            'tags': a.tag, 'prompt': prompt, 'image': str(image) if image else None,
            'source': a.source, 'model': a.model, 'status': a.status,
            'feedback': a.feedback, 'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    identity = [data[k] for k in ['prompt', 'category', 'model', 'image', 'status']]
    digest = hashlib.sha256(json.dumps(identity, ensure_ascii=False).encode()).hexdigest()
    store = a.store.expanduser().resolve()
    store.mkdir(parents=True, exist_ok=True)
    target = store / (digest + '.json')
    # Exclusive create prevents concurrent writers from overwriting an existing collection entry.
    try:
        with target.open('x', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
    except FileExistsError:
        print(json.dumps({'path': str(target), 'created': False}, ensure_ascii=False))
        return
    print(json.dumps({'path': str(target), 'created': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
