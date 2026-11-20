function currentLesson(){return LESSONS.find(l=>l.unit===unit&&l.part===lessonPart);}
function stopLessonsUI(){lessonPlaying=false;$('lesson-auto').textContent='整篇朗读';$('lesson-auto').setAttribute('aria-pressed','false');}
function focusSentence(line,next){audio.focus({audio:line.audio,exampleAudio:line.audio,audioPack:line.audioPack,syllables:[],phonics:[]},next?{audioPack:next.audioPack}:null);}
function renderLessonWords(container, sentence) {
 const words=sentence.match(/[A-Za-z]+(?:['’\-][A-Za-z]+)*/g)||[];
 for(const word of words){
  const key=word.replaceAll('’', "'").toLowerCase();
  const id=LESSON_WORD_AUDIO[key];
  const button=document.createElement('button');
  button.type='button';
  button.className='lesson-word';
  button.textContent=word;
  button.setAttribute('aria-pressed','false');
  button.onclick=()=>{
   stop();
   focusSentence({audio:id,audioPack:AUDIO_INDEX[id].pack});
   return playSound(id,button,generation,false,true);
  };
  container.append(button);
 }
}
function renderLessons(){
 $('words-panel').hidden=view!=='words';$('lessons-panel').hidden=view!=='texts';
 document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));
 document.querySelectorAll('[data-part]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.part===lessonPart)));
 const lesson=currentLesson();if(!lesson)return;
 $('lesson-title').textContent=lesson.title;$('lesson-page').textContent='UNIT '+unit+' · Part '+lessonPart.toUpperCase()+' · p. '+lesson.page;
 $('lesson-lines').replaceChildren();
 lesson.lines.forEach((line,i)=>{
  const row=document.createElement('article');
  row.className='sentence '+line.gender;
  const top=document.createElement('span');
  top.className='sentence-top';
  top.lang='en-GB';
  const role=document.createElement('span');
  role.className='role';
  role.textContent=line.speaker;
  top.append(role);
  const text=document.createElement('span');
  text.className='sentence-text';
  text.lang='en-GB';
  text.textContent=line.text;
  const translation=document.createElement('span');
  translation.className='sentence-translation';
  translation.lang='zh-CN';
  translation.id=lesson.id+'-translation-'+(i+1);
  translation.textContent=line.translation;
  const button=document.createElement('button');
  button.type='button';
  button.className='sentence-play';
  const copy=document.createElement('span');
  copy.className='sentence-copy';
  copy.append(top,text,translation);
  const icon=document.createElement('span');
  icon.className='sentence-play-icon';
  icon.innerHTML=speaker;
  button.append(copy,icon);
  button.setAttribute('aria-label','朗读整句：'+line.text);
  button.setAttribute('aria-describedby',translation.id);
  button.setAttribute('aria-pressed','false');
  button.onclick=()=>{
   stop();
   focusSentence(line,lesson.lines[i+1]);
   return playSound(line.audio,button,generation,false,true);
  };
  const wordsPanel=document.createElement('div');
  wordsPanel.className='sentence-word-panel';
  wordsPanel.setAttribute('role','group');
  wordsPanel.setAttribute('aria-label','单词点读');
  const label=document.createElement('div');
  label.className='sentence-word-label';
  label.textContent='单词点读';
  label.setAttribute('aria-hidden','true');
  const wordList=document.createElement('div');
  wordList.className='sentence-words';
  wordList.lang='en-GB';
  renderLessonWords(wordList,line.text);
  wordsPanel.append(label,wordList);
  row.append(button,wordsPanel);
  $('lesson-lines').append(row);
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
   const line=lesson.lines[i],button=$('lesson-lines').children[i].querySelector('.sentence-play');focusSentence(line,lesson.lines[i+1]);
   // Sentence recordings are already synthesized at 0.8x, with natural pitch.
   const ok=await playSound(line.audio,button,token,false,true);
   if(!ok){if(token===generation)stopLessonsUI();return;}
  }
  if(token===generation)stopLessonsUI();
 };
 renderLessons();
}
