from pathlib import Path
import asyncio,json,urllib.request
import edge_tts
R=Path(__file__).parent;out=R/'lesson-recordings';out.mkdir(exist_ok=True)
lessons=json.loads((R/'lessons.json').read_text());jobs={s['audio']:s for l in lessons for s in l['lines']}
p=out/'manifest.json';manifest=json.loads(p.read_text()) if p.exists() else {}
proxy=urllib.request.getproxies().get('https') or urllib.request.getproxies().get('http')
failures=[];count=0
async def main():
 sem=asyncio.Semaphore(3)
 async def one(id,s):
  global count
  async with sem:
   file=out/(id+'.mp3')
   for attempt in range(3):
    try:
     if not file.exists() or file.stat().st_size<1000:
      await edge_tts.Communicate(s['text'],s['voice'],rate='-20%',proxy=proxy,connect_timeout=20,receive_timeout=40).save(str(file))
     manifest[id]={'file':file.name,'voice':s['voice'],'locale':'en-GB','rate':'-20%','text':s['text'],'source':'Microsoft Edge Read Aloud'}
     p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2));count+=1
     if count%25==0:print('Prepared',count,'/',len(jobs),flush=True)
     return
    except Exception as e:
     if file.exists():file.unlink()
     if attempt==2:failures.append({'id':id,'error':type(e).__name__})
     else:await asyncio.sleep(1)
 await asyncio.gather(*(one(id,s) for id,s in jobs.items()))
 (out/'failures.json').write_text(json.dumps(failures));print('Prepared',count,'Failed',len(failures),flush=True)
asyncio.run(main())
