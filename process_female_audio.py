"""Split an approved SSML batch at its one-second pauses and level syllables.
Usage: python3 process_female_audio.py batch-1 /path/to/recording.mp3
Requires built-in macOS afconvert, no downloaded executables.
"""
from pathlib import Path
import sys,json,subprocess,wave,array,math
R=Path(__file__).parent;plan=R/'female-audio-plan';out=R/'female-recordings';out.mkdir(exist_ok=True)
def process(batch,recording):
    ids=json.loads((plan/(batch+'.json')).read_text());wav=out/(batch+'.wav')
    subprocess.run(['afconvert','-f','WAVE','-d','LEI16',recording,str(wav)],check=True)
    with wave.open(str(wav)) as f:
        rate=f.getframerate();assert f.getnchannels()==1 and f.getsampwidth()==2
        a=array.array('h',f.readframes(f.getnframes()))
    step=max(1,int(rate*.01));levels=[max(map(abs,a[i:i+step]),default=0) for i in range(0,len(a),step)]
    # A relative quiet threshold detects syllables without cutting soft consonants.
    threshold=max(8,max(levels)*.002);active=[i for i,v in enumerate(levels) if v>threshold];groups=[]
    for frame in active:
        if not groups or frame-groups[-1][-1]>65:groups.append([frame])
        else:groups[-1].append(frame)
    assert len(groups)==len(ids),f'Expected {len(ids)} syllables, found {len(groups)}; manual review required'
    manifest=json.loads((out/'manifest.json').read_text()) if (out/'manifest.json').exists() else {}
    for id,g in zip(ids,groups):
        start=max(0,(g[0]-18)*step);end=min(len(a),(g[-1]+23)*step)
        raw=a[start:end];speech=[v for v in raw if abs(v)>threshold]
        assert speech,'silent clip'
        rms=math.sqrt(sum(v*v for v in speech)/len(speech))/32768;peak=max(map(abs,raw))/32768
        gain=min(10**(-19/20)/rms,10**(-2/20)/peak)
        normalized=array.array('h',(round(v*gain) for v in raw))
        target=out/(id+'.wav');encoded=out/(id+'.m4a')
        with wave.open(str(target),'wb') as f:
            f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(normalized.tobytes())
        subprocess.run(['afconvert','-f','m4af','-d','aac','-b','64000',str(target),str(encoded)],check=True,capture_output=True)
        manifest[id]={'file':encoded.name,'voice':'Emma','locale':'en-GB','gainDB':round(20*math.log10(gain),2),'duration':len(raw)/rate,'batch':batch}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print('Processed',len(ids),'syllables; review sample before publication')
if __name__=='__main__':process(sys.argv[1],sys.argv[2])
