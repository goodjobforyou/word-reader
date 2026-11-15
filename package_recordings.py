from pathlib import Path
import json,base64,subprocess,wave,array
R=Path(__file__).parent; A=R/'recordings'; W=json.loads((R/'words.json').read_text());P=json.loads((A/'phonemes.json').read_text());D=json.loads((A/'words.json').read_text());E=json.loads((A/'extra.json').read_text());plan=json.loads((A/'syllable-plan.json').read_text())
def split(name,labels):
 source=A/(name+'.mp3');wav=A/(name+'.wav')
 subprocess.run(['afconvert','-f','WAVE','-d','LEI16',str(source),str(wav)],check=True)
 with wave.open(str(wav)) as f:rate=f.getframerate();ch=f.getnchannels();a=array.array('h',f.readframes(f.getnframes()))
 step=int(rate*.01)*ch;groups=[]
 for x in range(0,len(a),step):
  if max(map(abs,a[x:x+step]),default=0)<=150:continue
  if not groups or x-groups[-1][-1]>.65*rate*ch:groups.append([x])
  else:groups[-1].append(x)
 assert len(groups)==len(labels),(name,len(groups),len(labels))
 result={}
 for i,(label,g) in enumerate(zip(labels,groups)):
  target=A/f'{name}-{i}.wav';audio=A/f'{name}-{i}.m4a'
  with wave.open(str(target),'wb') as f:
   f.setnchannels(ch);f.setsampwidth(2);f.setframerate(rate);f.writeframes(a[max(0,g[0]-int(rate*.1)*ch):min(len(a),g[-1]+step+int(rate*.12)*ch)].tobytes())
  subprocess.run(['afconvert','-f','m4af','-d','aac','-b','64000',str(target),str(audio)],check=True,capture_output=True)
  result[label]={'file':audio.name,'source':'Amazon Polly Amy en-GB; IPA via ttsMP3'}
 return result
G=split('amy-syllables',list(plan['generated']));special=split('amy-special',['close','wind']);D.update(special)
sy={ipa:E[f'syllable-{i}'] for i,ipa in enumerate(plan['homophones'])};sy.update(P);sy.update(G);sy.update(split('amy-rent',['rənt']))
audio={};manifest={}
def put(id,item):
 file=A/item['file'];raw=file.read_bytes();assert len(raw)>500
 audio[id]={'mime':'audio/mp4' if file.suffix=='.m4a' else ('audio/wav' if file.suffix=='.wav' else 'audio/mpeg'),'data':base64.b64encode(raw).decode()};manifest[id]=item
for w in W:
 put(w['audio'],D[w['word']]);put(w['exampleAudio'],E[f'example-{w["id"]}'])
 for s in w['syllables']:put(s['audio'],D[w['word']] if len(w['syllables'])==1 else sy[s['ipa']])
 for p in w['phonics']:
  for s in p['sounds']:put(s['audio'],P[s['ipa']])
for u in (4,5,6):
 ids=set()
 for w in W:
  if w['unit']==u:
   ids.update([w['audio'],w['exampleAudio']]+[s['audio'] for s in w['syllables']]);ids.update(s['audio'] for p in w['phonics'] for s in p['sounds'])
 target=R/f'u{u}.json';target.write_text(json.dumps({i:audio[i] for i in sorted(ids)},separators=(',',':')));print(u,len(ids),target.stat().st_size)
(R/'audio-sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
html=(R/'index.template.html').read_text().replace('__WORDS__',json.dumps(W,ensure_ascii=False,separators=(',',':'))).replace('__APP__',(R/'app.js').read_text());(R/'index.html').write_text(html)
print('Replaced',len(audio),'audio IDs; no Apple voices')
