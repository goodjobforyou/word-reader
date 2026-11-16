"""Build the U1–U6 site. U4/U5 syllables are required; others may be pending."""
from pathlib import Path
import json,base64,hashlib,shutil
R=Path(__file__).parent

def build():
 W=json.loads((R/'words.json').read_text());P=json.loads((R/'recordings/phonemes.json').read_text());D=json.loads((R/'special-word-recordings.json').read_text())
 full=json.loads((R/'female-full/manifest.json').read_text());syllables=json.loads((R/'female-recordings/manifest.json').read_text());plan=json.loads((R/'female-audio-plan/jobs.json').read_text())
 audio={};sources={}
 def put(id,folder,item):
  file=folder/item['file'];raw=file.read_bytes();assert len(raw)>500
  mime='audio/wav' if raw[:4]==b'RIFF' else ('audio/mp4' if raw[4:8]==b'ftyp' else 'audio/mpeg')
  audio[id]={'mime':mime,'data':base64.b64encode(raw).decode()};sources[id]={**item,'file':str(file.relative_to(R)),'sha256':hashlib.sha256(raw).hexdigest()}
 for item in full.values():
  for id in item['references']:put(id,R/'female-full',item)
 for w in W:
  if w['word'] in ['close','wind','Mrs']:put(w['audio'],R/'recordings',D[w['word']])
  for group in w['phonics']:
   for sound in group['sounds']:put(sound['audio'],R/'recordings',P[sound['ipa']])
 for w in W:
  if len(w['syllables'])==1:
   id=w['syllables'][0]['audio'];audio[id]=audio[w['audio']];sources[id]=sources[w['audio']]
 for job in plan:
  if job['id'] in syllables:
   for ref in job['references']:
    # Prefer the full word for a monosyllable, preserving its natural delivery.
    if ref['audio'] not in audio:put(ref['audio'],R/'female-recordings',syllables[job['id']])
 for w in W:
  mandatory=[w['audio'],w['exampleAudio']]+[s['audio'] for p in w['phonics'] for s in p['sounds']]
  assert all(id in audio for id in mandatory),w['word']
  for s in w['syllables']:s['available']=s['audio'] in audio
  w['syllablesReady']=all(s['available'] for s in w['syllables'])
  if w['unit'] in [4,5]:assert w['syllablesReady'],w['word']
 out=R/'release';out.mkdir(exist_ok=True)
 unit_report={}
 for u in range(1,7):
  subset=[w for w in W if w['unit']==u];ids=set()
  for w in subset:
   ids.update([w['audio'],w['exampleAudio']]+[s['audio'] for s in w['syllables'] if s['available']]);ids.update(s['audio'] for p in w['phonics'] for s in p['sounds'])
  (out/f'u{u}.json').write_text(json.dumps({i:audio[i] for i in sorted(ids)},separators=(',',':')))
  unit_report[u]={'words':len(subset),'syllablesReady':sum(w['syllablesReady'] for w in subset),'audioIDs':len(ids),'bytes':(out/f'u{u}.json').stat().st_size}
 html=(R/'index.template.html').read_text().replace('__WORDS__',json.dumps(W,ensure_ascii=False,separators=(',',':'))).replace('__APP__',(R/'app.js').read_text())
 (out/'index.html').write_text(html);(out/'.nojekyll').touch();(out/'words.json').write_text(json.dumps(W,ensure_ascii=False,indent=2));(out/'audio-sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2))
 for name in ['app.js','index.template.html','build.py','units123.py','phonics.py','README.md','package_v2.py','prepare_female_audio.py','process_female_audio.py']:shutil.copyfile(R/name,out/name)
 report={'entries':len(W),'audioIDs':len(audio),'units':unit_report,'priorityUnitsReady':True,'deferredSyllableUnits':[1,2,3,6]};(R/'release-readiness.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':build()
