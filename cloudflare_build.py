"""Stage the static site and its referenced audio files for Cloudflare Pages."""
import argparse
import json
from pathlib import Path
import re
import shutil


def inline_json(html, name):
    match = re.search(rf'^const {name}=(.+);$', html, re.MULTILINE)
    if not match:
        raise ValueError(f'Could not find {name} in index.html')
    return json.loads(match.group(1))


def build(source, output):
    html = (source / 'index.html').read_text(encoding='utf-8')
    index = inline_json(html, 'AUDIO_INDEX')
    words = inline_json(html, 'WORDS')
    lessons = inline_json(html, 'LESSONS')
    assets = {entry.get('pack') or entry['file'] for entry in index.values()}
    assets.update(word['audioPack'] for word in words)
    assets.update(line['audioPack'] for lesson in lessons for line in lesson['lines'])

    if re.search(r'goodjobforyou|github\.(?:com|io)', html, re.IGNORECASE):
        raise ValueError('index.html contains a GitHub account name or link')
    for name in sorted(assets):
        if not re.fullmatch(r'[a-zA-Z0-9_-]+\.(?:json|mp3|m4a|wav)', name):
            raise ValueError(f'Unexpected audio asset path: {name}')
        if not (source / name).is_file() or (source / name).is_symlink():
            raise FileNotFoundError(source / name)

    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError(f'Output directory is not empty: {output}')
    shutil.copyfile(source / 'index.html', output / 'index.html')
    for name in sorted(assets):
        shutil.copyfile(source / name, output / name)
    (output / '404.html').write_text(
        '<!doctype html><html lang="zh-CN"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>页面找不到了</title><h1>页面找不到了</h1>'
        '<p><a href="/">返回朗读小屋</a></p></html>\n',
        encoding='utf-8',
    )
    print(f'Staged index.html and {len(assets)} referenced audio assets in {output}.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path('.'))
    parser.add_argument('--output', type=Path, default=Path('dist'))
    args = parser.parse_args()
    build(args.source, args.output)
