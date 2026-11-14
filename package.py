from pathlib import Path
import json,subprocess,base64,concurrent.futures,struct,math,wave
root=Path(__file__).parent
words=json.loads((root/'words.json').read_text())
jobs=json.loads((root/'jobs.json').read_text())
temp=Path('/tmp/word-reader-audio')
def convert(job):
    source=temp/(job['id']+'.wav'); target=temp/(job['id']+'.m4a')
    assert source.stat().st_size>5000,source
    raw=source.read_bytes(); pos=12; chunks={}
    while pos+8<=len(raw):
        tag=raw[pos:pos+4]; size=struct.unpack_from('<I',raw,pos+4)[0]
        chunks[tag]=raw[pos+8:pos+8+size];pos+=8+size+(size%2)
    fmt=struct.unpack_from('<HHIIHH',chunks[b'fmt ']);data=chunks[b'data']
    assert fmt[0]==3 and fmt[1]==1 and fmt[5]==32,fmt
    samples=struct.unpack('<'+'f'*(len(data)//4),data)
    assert all(math.isfinite(v) for v in samples),job
    peak=max(map(abs,samples));assert peak>.001,(job,peak)
    gain=min(16,.65/peak)
    pcm=[0]*int(fmt[2]*.08)+[round(max(-1,min(1,v*gain))*32767) for v in samples]+[0]*int(fmt[2]*.12)
    normalized=temp/('normalized-'+job['id']+'.wav')
    with wave.open(str(normalized),'wb') as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(fmt[2]);out.writeframes(struct.pack('<'+'h'*len(pcm),*pcm))
    subprocess.run(['/usr/bin/afconvert','-f','m4af','-d','aac','-b','48000',str(normalized),str(target)],check=True,capture_output=True)
    assert target.stat().st_size>1000,target
    return job['id'],base64.b64encode(target.read_bytes()).decode()
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    audio=dict(pool.map(convert,jobs))
for unit in (4,5,6):
    ids=set()
    for w in words:
        if w['unit']==unit:
            ids.update([w['audio'],w['exampleAudio']]+[s['audio'] for s in w['syllables']])
            ids.update(s['audio'] for p in w['phonics'] for s in p['sounds'])
    target=root/f'u{unit}.json'
    target.write_text(json.dumps({key:audio[key] for key in sorted(ids)},separators=(',',':')))
    print(target.name,len(ids),target.stat().st_size)
html=(root/'index.template.html').read_text().replace('__WORDS__',json.dumps(words,ensure_ascii=False,separators=(',',':')))
html=html.replace('__APP__',(root/'app.js').read_text())
(root/'index.html').write_text(html)
print('HTML',len(html.encode()),'bytes')
