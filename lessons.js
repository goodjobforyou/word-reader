function currentLesson(){return LESSONS.find(l=>l.unit===unit&&l.part===lessonPart);}
function stopLessonsUI(){lessonPlaying=false;$('lesson-auto').textContent='整篇朗读';$('lesson-auto').setAttribute('aria-pressed','false');}
function focusSentence(line,next){audio.focus({audio:line.audio,exampleAudio:line.audio,audioPack:line.audioPack,syllables:[],phonics:[]},next?{audioPack:next.audioPack}:null);}
function renderLessons(){
 $('words-panel').hidden=view!=='words';$('lessons-panel').hidden=view!=='texts';
 document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));
 document.querySelectorAll('[data-part]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.part===lessonPart)));
 const lesson=currentLesson();if(!lesson)return;
 $('lesson-title').textContent=lesson.title;$('lesson-page').textContent='UNIT '+unit+' · Part '+lessonPart.toUpperCase()+' · p. '+lesson.page;
 $('lesson-lines').replaceChildren();
 lesson.lines.forEach((line,i)=>{
  const button=document.createElement('button');button.className='sentence '+line.gender;button.lang='en-GB';button.setAttribute('aria-label','朗读 '+line.speaker+'：'+line.text);
  const top=document.createElement('span');top.className='sentence-top';
  const role=document.createElement('span');role.className='role';role.textContent=line.speaker;
  top.append(role);
  const text=document.createElement('span');text.className='sentence-text';text.textContent=line.text;
  button.append(top,text);button.insertAdjacentHTML('beforeend',speaker);
  button.onclick=()=>{stop();focusSentence(line,lesson.lines[i+1]);playSound(line.audio,button,generation,false,true);};$('lesson-lines').append(button);
 });
 stopLessonsUI();
 if(view==='texts'){history.replaceState(null,'','#u'+unit+'/text/'+lessonPart);focusSentence(lesson.lines[0],lesson.lines[1]);}
}
function initLessons(){
 document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{stop();view=b.dataset.view;render();});
 document.querySelectorAll('[data-part]').forEach(b=>b.onclick=()=>{stop();lessonPart=b.dataset.part;renderLessons();});
 $('lesson-auto').onclick=async()=>{
  if(lessonPlaying){stop();return;}stop();lessonPlaying=true;$('lesson-auto').textContent='停止朗读';$('lesson-auto').setAttribute('aria-pressed','true');
  const token=generation,lesson=currentLesson();
  for(let i=0;i<lesson.lines.length;i++){
   if(token!==generation)return;
   const line=lesson.lines[i],button=$('lesson-lines').children[i];focusSentence(line,lesson.lines[i+1]);
   // Sentence recordings are already synthesized at 0.8x, with natural pitch.
   const ok=await playSound(line.audio,button,token,false,true);
   if(!ok){if(token===generation)stopLessonsUI();return;}
  }
  if(token===generation)stopLessonsUI();
 };
 renderLessons();
}
