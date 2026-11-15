'use strict';
const $ = id => document.getElementById(id);
const speaker = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M11 5 6 9H3v6h3l5 4V5Z"/><path d="M15 8a6 6 0 0 1 0 8M18 5a10 10 0 0 1 0 14"/></svg>';
const playIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m8 5 11 7-11 7V5Z"/></svg>';
let unit=4, group='bold', position=0, filtered=[], generation=0, auto=false, active=null, cancelPending=null, slowFactor=1;
const player=$('player'), audioCache={}, loading={}, objectURLs={};
function status(message='') { $('status').textContent=message; }
function resetActive() {
  if (!active) return;
  active.classList.remove('is-playing'); active.setAttribute('aria-pressed','false'); active.removeAttribute('aria-busy'); active=null;
}
function renderAuto() {
  $('auto').innerHTML=auto?'Ⅱ <span>暂停</span>':playIcon+'<span>连续朗读</span>';
  $('auto').setAttribute('aria-pressed',String(auto));
}
function stop() {
  generation++; auto=false;
  if(cancelPending) cancelPending();
  player.pause(); player.onended=null; player.onerror=null; resetActive(); renderAuto();
}
async function loadAudio(u) {
  if(audioCache[u]) return audioCache[u];
  if(!loading[u]) {
    const controller=new AbortController(), timer=setTimeout(()=>controller.abort(),20000);
    loading[u]=fetch('u'+u+'.json?v=20261115',{signal:controller.signal})
      .then(r=>{if(!r.ok)throw Error('network');return r.json();})
      .then(data=>audioCache[u]=data)
      .catch(e=>{delete loading[u];throw e;})
      .finally(()=>clearTimeout(timer));
  }
  return loading[u];
}
function audioURL(id) {
  if(objectURLs[id]) return objectURLs[id];
  const entry=audioCache[unit]?.[id]; if(!entry) throw Error('missing');
  const b64=typeof entry==='string'?entry:entry.data;
  const raw=atob(b64), bytes=new Uint8Array(raw.length);
  for(let i=0;i<raw.length;i++)bytes[i]=raw.charCodeAt(i);
  return objectURLs[id]=URL.createObjectURL(new Blob([bytes],{type:entry.mime||'audio/mp4'}));
}
async function playSound(id,button,token,slow=false) {
  if(token!==generation) return false;
  if(!audioCache[unit]) {
    status('音频加载中…');
    try { await loadAudio(unit); }
    catch(e) { if(token===generation)status('音频加载失败，点一下重试');return false; }
    if(token!==generation)return false;
  }
  resetActive(); active=button; button.setAttribute('aria-busy','true'); status();
  return new Promise(resolve=>{
    let done=false;
    const finish=ok=>{
      if(done)return; done=true; clearTimeout(timer);
      if(cancelPending===cancel)cancelPending=null;
      player.onended=null; player.onerror=null; resetActive(); resolve(ok);
    };
    const cancel=()=>finish(false); cancelPending=cancel;
    const fail=()=>{if(done)return;if(token===generation)status('暂时无法播放，请再点一次');finish(false);};
    const timer=setTimeout(()=>{if(done)return;player.pause();fail();},30000);
    player.onended=()=>finish(true); player.onerror=fail;
    try {
      player.src=audioURL(id); slowFactor=slow?.82:1;
      player.playbackRate=Number($('speed').value)*slowFactor;
      const promise=player.play();
      if(promise)promise.then(()=>{
        if(done||token!==generation)return;
        button.removeAttribute('aria-busy');button.classList.add('is-playing');button.setAttribute('aria-pressed','true');
      }).catch(fail);
    } catch(e) { fail(); }
  });
}
function single(id,button,slow=false) { stop();return playSound(id,button,generation,slow); }
function writeHash() { history.replaceState(null,'','#u'+unit+'/'+group+'/'+filtered[position].id); }
function coloredWord(w) {
  $('word').replaceChildren();
  let cursor=0;
  // Abbreviations such as Mrs do not have a letter-by-letter syllable spelling.
  const split=w.syllables.map(s=>s.text).join('')===w.word.replaceAll(' ','');
  if(!split) $('word').textContent=w.word;
  else w.syllables.forEach((s,i)=>{
    if(w.word[cursor]===' '){$('word').append(document.createTextNode(' '));cursor++;}
    const span=document.createElement('span');span.className='c'+i%3;span.textContent=s.text;
    $('word').append(span);cursor+=s.text.length;
  });
  if(w.star){const star=document.createElement('sup');star.textContent='*';star.setAttribute('aria-hidden','true');$('word').prepend(star);}
}
function render() {
  filtered=WORDS.filter(w=>w.unit===unit&&w.bold===(group==='bold'));
  position=Math.max(0,Math.min(position,filtered.length-1));const w=filtered[position];
  document.querySelectorAll('[data-unit]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.unit)===unit)));
  document.querySelectorAll('[data-group]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.group===group)));
  $('bold-count').textContent=WORDS.filter(w=>w.unit===unit&&w.bold).length;
  $('regular-count').textContent=WORDS.filter(w=>w.unit===unit&&!w.bold).length;
  $('group-count').textContent=filtered.length+' 词';
  $('card-unit').textContent='UNIT '+unit+' / '+(group==='bold'?'黑体':'白体');
  $('card-index').textContent=String(position+1).padStart(2,'0')+' / '+String(filtered.length).padStart(2,'0');
  $('word-strip').replaceChildren();
  filtered.forEach((item,i)=>{
    const b=document.createElement('button');b.className='word-tab';b.textContent=item.word;b.setAttribute('aria-current',String(i===position));
    b.onclick=()=>{stop();status();position=i;render();};$('word-strip').append(b);
  });
  const current=$('word-strip').children[position];
  $('word-strip').scrollLeft=current.offsetLeft-$('word-strip').offsetLeft-($('word-strip').clientWidth-current.offsetWidth)/2;
  coloredWord(w);
  $('word').setAttribute('aria-label','朗读单词 '+w.word);$('word').onclick=()=>single(w.audio,$('word'));
  $('ipa').textContent='/'+w.ipa+'/';$('ipa').insertAdjacentHTML('beforeend',speaker);
  $('ipa').setAttribute('aria-label','朗读完整音标 '+w.ipa);$('ipa').onclick=()=>single(w.audio,$('ipa'),true);
  $('meaning').textContent=w.meaning;
  $('syllables').replaceChildren();
  w.syllables.forEach((s,i)=>{
    const b=document.createElement('button');b.className='syllable';
    const label=document.createElement('b');label.textContent=w.word==='Mrs'?(i===0?'mis':'siz'):s.text;
    const ipa=document.createElement('small');ipa.textContent='/'+s.ipa+'/';b.append(label,ipa);
    b.setAttribute('aria-label',`第 ${i+1} 音节 ${s.ipa}`);b.onclick=()=>single(s.audio,b);$('syllables').append(b);
  });
  $('phonics').replaceChildren();
  w.phonics.forEach(p=>{
    const wrap=document.createElement('div');wrap.className='phone-group';
    const label=document.createElement('span');label.className='grapheme';label.textContent=p.text;wrap.append(label);
    const sounds=document.createElement('div');sounds.className='phone-buttons';
    p.sounds.forEach(s=>{
      const b=document.createElement('button');b.className='phoneme';b.textContent='/'+s.ipa+'/';
      b.setAttribute('aria-label',p.text+' 的音素 '+s.ipa);b.onclick=()=>single(s.audio,b);sounds.append(b);
    });
    if(!p.sounds.length){const silent=document.createElement('span');silent.className='silent';silent.textContent='不发音';sounds.append(silent);}
    wrap.append(sounds);$('phonics').append(wrap);
  });
  $('example').textContent=w.example;$('example').insertAdjacentHTML('beforeend',speaker);
  $('example').setAttribute('aria-label','朗读例句 '+w.example);$('example').onclick=()=>single(w.exampleAudio,$('example'));
  $('translation').textContent=w.translation;
  $('previous').disabled=position===0;$('next').disabled=position===filtered.length-1;
  $('position').textContent=`${position+1} / ${filtered.length}`;
  $('progress').style.width=((position+1)/filtered.length*100)+'%';renderAuto();writeHash();
  loadAudio(unit).catch(()=>{if(unit===w.unit)status('音频加载失败，点一下重试');});
}
document.querySelectorAll('[data-unit]').forEach(b=>b.onclick=()=>{stop();status();unit=Number(b.dataset.unit);position=0;render();});
document.querySelectorAll('[data-group]').forEach(b=>b.onclick=()=>{stop();status();group=b.dataset.group;position=0;render();});
function move(step){stop();status();position+=step;render();}
$('previous').onclick=()=>move(-1);$('next').onclick=()=>move(1);
$('speed').onchange=()=>{player.playbackRate=Number($('speed').value)*slowFactor;};
$('mode').onchange=()=>{stop();status();};
$('auto').onclick=async()=>{
  if(auto){stop();return;}stop();auto=true;renderAuto();const token=generation;
  while(token===generation&&auto){
    const w=filtered[position], sequence=[[w.audio,$('word')]];
    if($('mode').value==='full'){
      sequence.push(...w.syllables.map((s,i)=>[s.audio,$('syllables').children[i]]));
      const buttons=Array.from($('phonics').querySelectorAll('button'));
      sequence.push(...w.phonics.flatMap(p=>p.sounds).map((s,i)=>[s.audio,buttons[i]]));
      sequence.push([w.exampleAudio,$('example')]);
    }
    for(const [audio,button] of sequence){
      if(!await playSound(audio,button,token)){if(token===generation){auto=false;renderAuto();}return;}
    }
    if(token!==generation)return;
    if(position===filtered.length-1)break;
    position++;render();
  }
  if(token===generation){auto=false;renderAuto();}
};
function restoreHash(){
  const m=location.hash.match(/^#u([456])\/(bold|regular)\/(\d+)$/);
  if(m){unit=Number(m[1]);group=m[2];const list=WORDS.filter(w=>w.unit===unit&&w.bold===(group==='bold'));position=Math.max(0,list.findIndex(w=>w.id===Number(m[3])));}
  render();
}
window.addEventListener('hashchange',()=>{stop();restoreHash();});
document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
window.addEventListener('pagehide',stop);
restoreHash();
