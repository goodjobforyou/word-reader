import json, pathlib, subprocess, base64, hashlib
from phonics import PHONICS
ROOT = pathlib.Path(__file__).parent
# unit | bold | starred | word | IPA | meaning | syllables (spelling~IPA) | example | translation
RAW = '''4|0|0|stay|steɪ|待；保持；继续是|stay~steɪ|We should stay healthy.|我们应该保持健康。
4|0|1|should|ʃʊd|（提出或征询建议）该，可以|should~ʃʊd|You should drink some water.|你应该喝点水。
4|0|0|flu|fluː|流行性感冒；流感|flu~fluː|He has the flu.|他得了流感。
4|0|0|else|els|其他的；别的|else~els|What else can we do?|我们还能做什么？
4|1|1|exercise|ˈeksəsaɪz|锻炼；训练；操练|ex~eks;er~ə;cise~saɪz|Let's exercise together!|让我们一起锻炼吧！
4|0|0|enough|ɪˈnʌf|足够的；充足的；充分的|e~ɪ;nough~nʌf|We need enough sleep.|我们需要充足的睡眠。
4|0|0|if|ɪf|如果；假若；倘若|if~ɪf|If you are tired, take a rest.|如果你累了，就休息一下。
4|0|0|habit|ˈhæbɪt|习惯|ha~hæ;bit~bɪt|Reading every day is a good habit.|每天阅读是个好习惯。
4|0|1|show|ʃəʊ|（电视或广播）节目|show~ʃəʊ|This is my favourite TV show.|这是我最喜欢的电视节目。
4|1|1|phone|fəʊn|电话；电话机|phone~fəʊn|The phone is on the desk.|电话在书桌上。
4|0|1|then|ðen|那么；因此；既然如此|then~ðen|Then let's go home.|那么我们回家吧。
4|1|0|rest|rest|休息；放松|rest~rest|Let's have a rest.|我们休息一下吧。
4|0|0|take care of|teɪk keə əv|爱护；照顾|take~teɪk;care~keə;of~əv|We should take care of our eyes.|我们应该爱护眼睛。
4|1|0|check|tʃek|查看；查明|check~tʃek|Please check your homework.|请检查你的作业。
4|1|0|less|les|（与不可数名词连用）较少的，更少的|less~les|We should eat less sugar.|我们应该少吃糖。
4|1|0|brush|brʌʃ|（用刷子）刷净，刷亮，刷平顺|brush~brʌʃ|I brush my teeth every morning.|我每天早上刷牙。
4|1|0|tooth|tuːθ|牙；齿（复数 teeth /tiːθ/）|tooth~tuːθ|This tooth is loose.|这颗牙松了。
4|0|0|twice|twaɪs|两次；两遍|twice~twaɪs|I brush my teeth twice a day.|我每天刷两次牙。
4|0|1|hour|ˈaʊə|小时|hour~aʊə|I read for an hour every day.|我每天读书一小时。
4|0|1|free|friː|没有安排活动的；空闲的|free~friː|Are you free this afternoon?|你今天下午有空吗？
5|0|1|hungry|ˈhʌŋɡri|感到饿的|hun~hʌŋ;gry~ɡri|I'm hungry. Let's have lunch.|我饿了。我们吃午饭吧。
5|1|0|beef|biːf|牛肉|beef~biːf|I'd like some beef.|我想吃一些牛肉。
5|1|1|ice cream|ˌaɪs ˈkriːm|（一份）冰激凌|ice~aɪs;cream~kriːm|I like ice cream.|我喜欢冰激凌。
5|0|1|little|ˈlɪtl|少许；一点|lit~lɪt;tle~əl|There is a little milk in the cup.|杯子里有一点牛奶。
5|1|0|dumpling|ˈdʌmplɪŋ|饺子；汤圆|dump~dʌmp;ling~lɪŋ|This dumpling is delicious.|这个饺子很好吃。
5|1|1|tea|tiː|茶叶；茶；茶水|tea~tiː|Would you like some tea?|你想喝点茶吗？
5|1|0|hamburger|ˈhæmbɜːɡə|汉堡包；汉堡牛肉饼|ham~hæm;bur~bɜː;ger~ɡə|I'd like a hamburger.|我想要一个汉堡包。
5|0|1|Mrs|ˈmɪsɪz|（用于女子的姓氏或姓名前）太太，夫人|Mrs~mɪ;Mrs~sɪz|Mrs Green is our teacher.|格林夫人是我们的老师。
5|0|0|coconut|ˈkəʊkənʌt|椰子|co~kəʊ;co~kə;n ut~nʌt|This coconut is big.|这个椰子很大。
5|0|1|interesting|ˈɪntrəstɪŋ|有趣的；有吸引力的|in~ɪn;teres~trəs;ting~tɪŋ|This book is interesting.|这本书很有趣。
5|1|0|seed|siːd|种子；籽|seed~siːd|Put the seed in the soil.|把种子放进土里。
5|0|0|pull|pʊl|拔出；抽出|pull~pʊl|Let's pull up the carrot.|我们把胡萝卜拔出来吧。
5|1|0|stem|stem|（花草的）茎；（花或叶的）梗，柄|stem~stem|The stem is green.|茎是绿色的。
5|1|0|root|ruːt|根；根茎|root~ruːt|The root is under the ground.|根在地下。
5|0|0|lotus|ˈləʊtəs|莲属植物|lo~ləʊ;tus~təs|A lotus grows in the lake.|一株莲花生长在湖中。
5|0|1|lake|leɪk|湖；湖泊|lake~leɪk|The lake is beautiful.|这个湖很美。
5|0|1|world|wɜːld|世界；地球；天下|world~wɜːld|We live in a beautiful world.|我们生活在一个美丽的世界里。
5|0|0|round|raʊnd|圆形的；环形的；球形的|round~raʊnd|The ball is round.|球是圆的。
5|0|0|different|ˈdɪfrənt|不同的；有区别的；有差异的|dif~dɪf;ferent~rənt|We like different colours.|我们喜欢不同的颜色。
5|0|1|way|weɪ|方法；手段；途径；方式|way~weɪ|This is a good way to learn.|这是一个很好的学习方法。
6|1|1|river|ˈrɪvə|河；江|riv~rɪv;er~ə|There is a river near my school.|我的学校附近有一条河。
6|0|0|nature|ˈneɪtʃə|自然界；大自然|na~neɪ;ture~tʃə|We love nature.|我们热爱大自然。
6|1|0|waterfall|ˈwɔːtəfɔːl|瀑布|wa~wɔː;ter~tə;fall~fɔːl|Look at that waterfall!|看那道瀑布！
6|1|0|forest|ˈfɒrɪst|森林；林区|for~fɒr;est~ɪst|There are many trees in the forest.|森林里有许多树。
6|0|1|famous|ˈfeɪməs|著名的；出名的|fa~feɪ;mous~məs|This city is famous for its tea.|这座城市因茶而闻名。
6|1|0|mountain|ˈmaʊntən|高山；山岳|moun~maʊn;tain~tən|The mountain is very high.|这座山很高。
6|0|0|wind|wɪnd|风；气流|wind~wɪnd|The wind is strong today.|今天风很大。
6|0|0|trip|trɪp|（尤指短程往返的）旅行，旅游，出行|trip~trɪp|We are going on a school trip.|我们要去参加学校组织的旅行。
6|0|0|dangerous|ˈdeɪndʒərəs|有危险的；不安全的|dan~deɪn;ge~dʒə;rous~rəs|It is dangerous to swim here.|在这里游泳很危险。
6|0|1|heavy|ˈhevi|程度大的；严重的|hea~he;vy~vi|There is heavy rain today.|今天有大雨。
6|0|0|hotel|həʊˈtel|旅馆；旅社|ho~həʊ;tel~tel|We stay at a small hotel.|我们住在一家小旅馆里。
6|0|1|close|kləʊz|关；关闭；闭上|close~kləʊz|Please close the window.|请关上窗户。
6|0|1|umbrella|ʌmˈbrelə|伞；雨伞|um~ʌm;brel~bre;la~lə|Take your umbrella.|带上你的雨伞。
6|0|0|raincoat|ˈreɪnkəʊt|雨衣|rain~reɪn;coat~kəʊt|Put on your raincoat.|穿上你的雨衣。
6|0|1|worry|ˈwʌri|担心；担忧；发愁|wor~wʌ;ry~ri|Don't worry. I'm fine.|别担心。我很好。
6|0|1|fine|faɪn|晴朗的|fine~faɪn|It's a fine day today.|今天是个晴天。
6|1|0|fog|fɒɡ|雾|fog~fɒɡ|We can't see the road in the fog.|雾中我们看不清道路。
6|1|0|flood|flʌd|洪水；水灾|flood~flʌd|The heavy rain caused a flood.|大雨引发了洪水。
6|1|1|fire|ˈfaɪə|火；火灾|fire~faɪə|Stay away from the fire.|远离火。
6|0|1|know|nəʊ|知道；了解|know~nəʊ|Do you know this place?|你知道这个地方吗？
6|0|1|before|bɪˈfɔː|在……之前|be~bɪ;fore~fɔː|Wash your hands before lunch.|午饭前洗手。
6|0|0|go hiking|ɡəʊ ˈhaɪkɪŋ|徒步旅行|go~ɡəʊ;hi~haɪ;king~kɪŋ|Let's go hiking this Sunday.|我们这周日去徒步旅行吧。
6|0|1|bring|brɪŋ|带……到某处；带来；取来|bring~brɪŋ|Please bring some water.|请带些水来。'''

words=[]
jobs={}
def sound(text, ipa=None, voice=None):
    voice=voice or ('male' if ipa else 'female')
    key=hashlib.sha256((text+'|'+str(ipa)+'|'+voice).encode()).hexdigest()[:14]
    jobs[key]={'id':key,'text':text,'ipa':ipa,'voice':voice}
    return key
for i,line in enumerate(RAW.splitlines()):
    unit,bold,star,word,ipa,meaning,parts,example,translation=line.split('|')
    parts=parts.replace('n ut','nut')
    syllables=[]
    for part in parts.split(';'):
        spelling,phonetic=part.split('~')
        syllables.append({'text':spelling,'ipa':phonetic,'audio':sound(spelling,phonetic)})
    phonics=[]
    for item in PHONICS[word].split(';'):
        spelling,phones=item.split('~')
        phonics.append({'text':spelling,'sounds':[{'ipa':p,'audio':sound('sound',p)} for p in phones.split(',') if p]})
    voice='male' if i%2==0 else 'female'
    words.append({'id':i,'unit':int(unit),'bold':bold=='1','star':star=='1','word':word,'ipa':ipa,'meaning':meaning,'syllables':syllables,'phonics':phonics,'example':example,'translation':translation,'audio':sound('Missus' if word=='Mrs' else word,voice=voice),'exampleAudio':sound(example,voice='female' if voice=='male' else 'male')})
assert len(words)==63
for unit in (4,5,6):
    subset=[w for w in words if w['unit']==unit]
    print(unit,len(subset),'bold',sum(w['bold'] for w in subset))
(ROOT/'words.json').write_text(json.dumps(words,ensure_ascii=False,indent=2))
(ROOT/'jobs.json').write_text(json.dumps(list(jobs.values()),ensure_ascii=False))
print('Audio jobs:',len(jobs))
