"""Prepare explicit, supported British IPA for one female voice.
No network requests; generated SSML is reviewed before synthesis.
"""
from pathlib import Path
import json,re,html,hashlib
R=Path(__file__).parent
# Textbook /e r tʃ dʒ/ are converted to the provider's IPA notation.
def provider_ipa(ipa):
    ipa=ipa.replace('ɡ','g').replace('r','ɹ').replace('tʃ','t͡ʃ').replace('dʒ','d͡ʒ')
    ipa=re.sub(r'e(?!ɪ)','ɛ',ipa)
    # Happy-vowel /i/ is supported and must not be lengthened.
    ipa={'fl':'fəl','sn':'sən'}.get(ipa,ipa)
    return ipa

def main():
    words=json.loads((R/'words.json').read_text())
    jobs={}
    for w in words:
        for s in w['syllables']:
            # Do not replace a weak vowel by a differently pronounced English word.
            phonetic=provider_ipa(s['ipa'])
            key=hashlib.sha256(('Emma|'+phonetic+'|v3').encode()).hexdigest()[:16]
            jobs.setdefault(key,{'id':key,'ipa':s['ipa'],'providerIPA':phonetic,'text':s['text'],'references':[]})['references'].append({'word':w['word'],'audio':s['audio']})
    out=R/'female-audio-plan';out.mkdir(exist_ok=True)
    (out/'jobs.json').write_text(json.dumps(list(jobs.values()),ensure_ascii=False,indent=2))
    batches=[];current=[];length=0
    for job in jobs.values():
        token=f'<phoneme alphabet="ipa" ph="{html.escape(job["providerIPA"],quote=True)}">{html.escape(job["text"])}</phoneme><break time="1s"/>'
        if length+len(token)>2500 and current:batches.append(current);current=[];length=0
        current.append((job['id'],token));length+=len(token)
    if current:batches.append(current)
    for i,b in enumerate(batches):
        text='<prosody rate="85%">'+''.join(x[1] for x in b)+'</prosody>'
        (out/f'batch-{i+1}.ssml').write_text(text)
        (out/f'batch-{i+1}.json').write_text(json.dumps([x[0] for x in b]))
    samples=[j for j in jobs.values() if any(r['word'] in ['different','heavy'] for r in j['references'])]
    text='<prosody rate="85%">'+''.join(f'<phoneme alphabet="ipa" ph="{html.escape(j["providerIPA"],quote=True)}">{html.escape(j["text"])}</phoneme><break time="1s"/>' for j in samples)+'</prosody>'
    (out/'quality-sample.ssml').write_text(text)
    (out/'quality-sample.json').write_text(json.dumps([j['id'] for j in samples]))
    print(len(jobs),'unique syllables;',len(batches),'batches; sample',len(text),'characters')
if __name__=='__main__':main()
