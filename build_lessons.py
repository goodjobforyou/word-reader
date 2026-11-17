from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
import re,json,hashlib
R=Path(__file__).parent
SOURCE=R.parent/'output/docx/五年级上册英语_Lets_talk全册课文.docx'
FEMALE={'Miss White','Sarah','Chen Jie','Amy','Mum','Mrs Green',"Mike's mum"}
MALE={'Mike','Zhang Peng','Binbin','Oliver','John','Grandpa','Sam',"Mike's dad",'Mr Liu'}
with ZipFile(SOURCE) as z:root=E.fromstring(z.read('word/document.xml'))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
lessons=[];unit=None;lesson=None
for p in root.findall('.//w:p',ns):
 text=''.join(t.text or '' for t in p.findall('.//w:t',ns)).strip()
 m=re.match(r'Unit (\d)\s+(.+)',text)
 if m:unit=int(m[1]);title=m[2];continue
 m=re.match(r'Part ([AB]).*page (\d+)',text)
 if m:
  lesson={'id':f'u{unit}{m[1].lower()}','unit':unit,'part':m[1].lower(),'title':title,'page':int(m[2]),'lines':[]};lessons.append(lesson);continue
 if lesson and ': ' in text:
  role,speech=text.split(': ',1)
  assert role in FEMALE|MALE,role
  gender='female' if role in FEMALE else 'male';voice='en-GB-SoniaNeural' if gender=='female' else 'en-GB-RyanNeural'
  for sentence in re.split(r'(?<=[.!?])\s+',speech):
   key=hashlib.sha256((voice+'|-20%|'+sentence).encode()).hexdigest()[:16]
   lesson['lines'].append({'speaker':role,'gender':gender,'text':sentence,'audio':'text-'+key,'voice':voice})
assert len(lessons)==12 and all(x['lines'] for x in lessons)
(R/'lessons.json').write_text(json.dumps(lessons,ensure_ascii=False,indent=2))
print({'lessons':len(lessons),'sentences':sum(len(x['lines']) for x in lessons),'characters':sum(len(s['text']) for x in lessons for s in x['lines'])})
