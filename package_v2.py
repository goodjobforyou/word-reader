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
 # Remove only this builder's obsolete generated audio artifacts.
 for pattern in ['u[1-6].json','clip-u*-*.json','phone-*.mp3','phone-*.m4a']:
  for old in out.glob(pattern):old.unlink()
 index={};phone_ids={s['audio'] for w in W for p in w['phonics'] for s in p['sounds']}
 for id in sorted(phone_ids):
  entry=audio[id];raw=base64.b64decode(entry['data']);ext='mp3' if entry['mime']=='audio/mpeg' else 'm4a'
  file='phone-'+hashlib.sha256(raw).hexdigest()[:16]+'.'+ext
  (out/file).write_bytes(raw);index[id]={'file':file,'mime':entry['mime']}
 packs=[]
 for u in range(1,7):
  subset=[w for w in W if w['unit']==u]
  for start in range(0,len(subset),3):
   chunk=subset[start:start+3];ids={id for w in chunk for id in [w['audio'],w['exampleAudio'],*[s['audio'] for s in w['syllables'] if s['available']]]}
   data=json.dumps({id:audio[id] for id in sorted(ids)},separators=(',',':')).encode()
   file=f'clip-u{u}-{start//3+1:02}-'+hashlib.sha256(data).hexdigest()[:12]+'.json'
   (out/file).write_bytes(data);packs.append({'file':file,'bytes':len(data),'words':[w['word'] for w in chunk]})
   for id in ids:index.setdefault(id,{'pack':file})
   for w in chunk:w['audioPack']=file
 unit_report={}
 for u in range(1,7):
  subset=[w for w in W if w['unit']==u];ids=set()
  for w in subset:
   ids.update([w['audio'],w['exampleAudio']]+[s['audio'] for s in w['syllables'] if s['available']]);ids.update(s['audio'] for p in w['phonics'] for s in p['sounds'])
  assert all(id in index for id in ids)
  unit_report[u]={'words':len(subset),'syllablesReady':sum(w['syllablesReady'] for w in subset),'audioIDs':len(ids),'packBytes':sum(p['bytes'] for p in packs if p['file'].startswith(f'clip-u{u}-'))}
 html=(R/'index.template.html').read_text().replace('__WORDS__',json.dumps(W,ensure_ascii=False,separators=(',',':'))).replace('__AUDIO_INDEX__',json.dumps(index,separators=(',',':'))).replace('__AUDIO_ENGINE__',(R/'audio-engine.js').read_text()).replace('__APP__',(R/'app.js').read_text())
 (out/'index.html').write_text(html);(out/'.nojekyll').touch();(out/'words.json').write_text(json.dumps(W,ensure_ascii=False,indent=2));(out/'audio-sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2))
 (out/'audio-index.json').write_text(json.dumps(index,separators=(',',':')))
 for name in ['app.js','audio-engine.js','index.template.html','build.py','units123.py','phonics.py','README.md','package_v2.py','prepare_female_audio.py','process_female_audio.py']:shutil.copyfile(R/name,out/name)
 report={'entries':len(W),'audioIDs':len(audio),'units':unit_report,'priorityUnitsReady':True,'deferredSyllableUnits':[u for u,v in unit_report.items() if v['syllablesReady']<v['words']],'wordPacks':len(packs),'phonemeFiles':len({index[id]['file'] for id in phone_ids}),'maxWordPackBytes':max(p['bytes'] for p in packs),'packs':packs};(R/'release-readiness.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='packs'},ensure_ascii=False,indent=2))
if __name__=='__main__':build()
