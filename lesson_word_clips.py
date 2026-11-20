"""Create reusable British-English word clips for the lesson panel on macOS."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parent
RECORDINGS = ROOT / 'lesson-word-recordings'
WORD = re.compile(r"[A-Za-z]+(?:['’\-][A-Za-z]+)*")
VOICE = 'Daniel'
BASE_WORDS_PER_MINUTE = 175
RATE = round(BASE_WORDS_PER_MINUTE * .75)


def word_key(text):
    return text.replace('’', "'").lower()


def collect_words(lessons):
    words = {}
    for lesson in lessons:
        for line in lesson['lines']:
            for match in WORD.finditer(line['text']):
                words.setdefault(word_key(match.group()), match.group())
    return words


def clip_id(key):
    signature = f'en-GB|{VOICE}|{RATE}|{key}'
    return 'lesson-word-' + hashlib.sha256(signature.encode()).hexdigest()[:16]


def record(pair):
    key, display = pair
    # These spellings disambiguate the verb and initialisms when read alone.
    spoken = {'close': 'cloze', 'pe': 'P E', 'tv': 'T V'}.get(key, display)
    name = clip_id(key) + '.m4a'
    target = RECORDINGS / name
    if not target.is_file():
        with TemporaryDirectory(dir=RECORDINGS) as tmp:
            aiff = Path(tmp) / 'speech.aiff'
            clip = Path(tmp) / name
            subprocess.run(['/usr/bin/say', '-v', VOICE, '-r', str(RATE),
                            '-o', str(aiff), spoken], check=True, timeout=25)
            subprocess.run(['/usr/bin/afconvert', '-f', 'm4af', '-d', 'aac',
                            '-b', '48000', str(aiff), str(clip)], check=True,
                           capture_output=True, timeout=25)
            if clip.stat().st_size < 1200:
                raise ValueError(f'Synthesis did not produce audio for {key}')
            clip.replace(target)
    return key, {'file': name, 'voice': VOICE, 'locale': 'en-GB',
                 'wordsPerMinute': RATE, 'text': display}


def main():
    RECORDINGS.mkdir(exist_ok=True)
    words = collect_words(json.loads((ROOT / 'lessons.json').read_text()))
    with ThreadPoolExecutor(max_workers=3) as workers:
        manifest = {}
        for i, (key, entry) in enumerate(workers.map(record, sorted(words.items())), 1):
            manifest[key] = entry
            if i % 50 == 0:
                print(f'Generated {i}/{len(words)} recordings', flush=True)
    (RECORDINGS / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f'Generated or reused {len(manifest)} recordings.')


if __name__ == '__main__':
    main()
