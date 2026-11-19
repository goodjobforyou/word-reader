'use strict';

// Small immutable packs for words; individual files for shared phonemes.
// Keep the working set bounded on phones and cancel downloads from old cards.
class ReaderAudio {
  constructor(index, player) {
    this.index=index; this.player=player; this.context=null;
    this.raw=new Map(); this.packs=new Map(); this.buffers=new Map();
    this.decoding=new Map(); this.pending=new Map(); this.urls=new Map();
    this.playToken=0; this.focusToken=0; this.finish=null; this.source=null;
    this.currentIds=new Set(); this.currentPack=null; this.currentFiles=new Set();
  }
  remember(cache,key,value,limit) {
    cache.delete(key); cache.set(key,value);
    while(cache.size>limit) cache.delete(cache.keys().next().value);
    return value;
  }
  unlock() {
    const Context=window.AudioContext||window.webkitAudioContext;
    if(!Context) return Promise.resolve(false);
    try {
      if(!this.context) this.context=new Context({latencyHint:'interactive'});
      if(this.context.state==='running') return Promise.resolve(true);
      // Called synchronously from the tap handler, before any network await.
      return this.context.resume().then(()=>this.context.state==='running').catch(()=>false);
    } catch(e) { return Promise.resolve(false); }
  }
  fileFor(id) {
    const item=this.index[id];
    if(!item) throw Error('missing audio');
    return item.pack&&this.currentIds.has(id)?this.currentPack:(item.pack||item.file);
  }
  request(file,json) {
    if(this.pending.has(file)) return this.pending.get(file).promise;
    const controller=new AbortController(), request={controller};
    const timer=setTimeout(()=>controller.abort(),15000);
    request.promise=fetch(file,{signal:controller.signal,cache:'force-cache'})
      .then(response=>{if(!response.ok) throw Error('network');return json?response.json():response.arrayBuffer();})
      .finally(()=>{
        clearTimeout(timer);
        if(this.pending.get(file)===request) this.pending.delete(file);
      });
    this.pending.set(file,request);
    return request.promise;
  }
  async pack(file) {
    let data=this.packs.get(file);
    if(!data) data=await this.request(file,true);
    this.remember(this.packs,file,data,12);
    for(const [id,entry] of Object.entries(data)) this.remember(this.raw,id,entry,160);
  }
  async bytes(id) {
    let entry=this.raw.get(id);
    if(!entry) {
      const item=this.index[id]; if(!item) throw Error('missing audio');
      if(item.pack) { await this.pack(this.fileFor(id)); entry=this.raw.get(id); }
      else entry=this.remember(this.raw,id,{bytes:await this.request(item.file,false),mime:item.mime},160);
    }
    if(!entry) throw Error('missing recording');
    this.remember(this.raw,id,entry,160);
    if(!entry.bytes) {
      const binary=atob(entry.data), bytes=new Uint8Array(binary.length);
      for(let i=0;i<binary.length;i++) bytes[i]=binary.charCodeAt(i);
      entry.bytes=bytes.buffer;
    }
    return entry;
  }
  async buffer(id) {
    const cached=this.buffers.get(id);
    if(cached) return this.remember(this.buffers,id,cached,48);
    if(this.decoding.has(id)) return this.decoding.get(id);
    const task=(async()=>{
      const entry=await this.bytes(id);
      const buffer=await new Promise((resolve,reject)=>this.context.decodeAudioData(entry.bytes.slice(0),resolve,reject));
      return this.remember(this.buffers,id,buffer,48);
    })().finally(()=>{if(this.decoding.get(id)===task) this.decoding.delete(id);});
    this.decoding.set(id,task); return task;
  }
  focus(word,next) {
    const token=++this.focusToken;
    this.currentPack=word.audioPack;
    this.currentIds=new Set([word.audio,word.exampleAudio,...word.syllables.filter(s=>s.available!==false).map(s=>s.audio)]);
    const phones=[...new Set(word.phonics.flatMap(p=>p.sounds.map(s=>s.audio)))];
    this.currentFiles=new Set([word.audioPack,...phones.map(id=>this.index[id].file)]);
    // Remove aborted entries now so a quick return can start a fresh request.
    for(const [file,request] of this.pending) if(!this.currentFiles.has(file)) {
      request.controller.abort(); this.pending.delete(file);
    }
    this.pack(word.audioPack).then(async()=>{
      if(token!==this.focusToken) return;
      if(this.context) for(const id of this.currentIds) {
        if(token!==this.focusToken) return;
        await this.buffer(id).catch(()=>{});
      }
      // Two small background requests at a time; never download a whole unit.
      const jobs=phones.map(id=>async()=>{
        await this.bytes(id);
        if(this.context&&token===this.focusToken) await this.buffer(id);
      });
      if(next&&next.audioPack!==word.audioPack) jobs.push(()=>this.pack(next.audioPack));
      const worker=async()=>{
        while(token===this.focusToken&&jobs.length) await jobs.shift()().catch(()=>{});
      };
      await Promise.all([worker(),worker()]);
    }).catch(()=>{}); // A later tap retries and reports a real foreground failure.
  }
  stop() {
    this.playToken++;
    const source=this.source;
    if(this.finish) this.finish(false);
    this.player.pause();
    if(source) {
      source.onended=null;
      try { source.stop(); } catch(e) {}
      source.disconnect(); this.source=null;
    }
    this.player.onended=null; this.player.onerror=null;
    this.player.dataset.state='idle';
  }
  setRate(rate) {
    if(this.source) this.source.playbackRate.value=rate;
    this.player.playbackRate=rate;
  }
  async play(id,rate,onStart) {
    const token=++this.playToken, tapped=performance.now();
    // On iOS, the ambient category is silenced by the ringer switch.
    // A tap on a recording is intentional media playback.
    try {
      const session=window.navigator?.audioSession;
      if(session&&session.type!=='playback') session.type='playback';
    } catch {} // Playback still works in browsers without a usable Audio Session API.
    const resumed=this.unlock();
    this.player.dataset.state='loading';
    this.player.dataset.audioId=id;
    const entry=await this.bytes(id);
    if(token!==this.playToken) return false;
    let buffer=null;
    if(await resumed) {
      try { buffer=await this.buffer(id); } catch(e) { /* Native decoder fallback. */ }
    }
    if(token!==this.playToken) return false;
    return new Promise((resolve,reject)=>{
      let ended=false, source=null;
      const finish=(ok,error)=>{
        if(ended) return; ended=true; clearTimeout(timer);
        if(this.finish===finish) this.finish=null;
        if(source) { source.onended=null; source.disconnect(); if(this.source===source)this.source=null; }
        this.player.onended=null; this.player.onerror=null;
        this.player.dataset.state=ok?'ended':'idle';
        if(error) reject(error); else resolve(ok);
      };
      const timer=setTimeout(()=>{this.stop();finish(false,Error('playback timeout'));},30000);
      this.finish=finish;
      const started=()=>{
        if(ended||token!==this.playToken) return;
        this.player.dataset.state='playing';
        this.player.dataset.latencyMs=String(Math.round(performance.now()-tapped));
        onStart();
      };
      try {
        if(buffer) {
          source=this.context.createBufferSource();source.buffer=buffer;
          source.playbackRate.value=rate;source.connect(this.context.destination);
          source.onended=()=>finish(true);this.source=source;
          this.player.dataset.engine='web-audio';source.start();started();
        } else {
          if(!this.urls.has(id)) {
            const url=URL.createObjectURL(new Blob([entry.bytes],{type:entry.mime}));
            this.urls.set(id,url);
            if(this.urls.size>32) {const oldest=this.urls.keys().next().value;URL.revokeObjectURL(this.urls.get(oldest));this.urls.delete(oldest);}
          }
          this.player.dataset.engine='html-audio';this.player.src=this.urls.get(id);
          this.player.playbackRate=rate;this.player.onended=()=>finish(true);
          this.player.onerror=()=>finish(false,Error('media error'));
          const playing=this.player.play();
          if(playing) playing.then(started).catch(error=>finish(false,error));else started();
        }
      } catch(error) {finish(false,error);}
    });
  }
  suspend() {
    this.stop(); this.focusToken++;
    for(const request of this.pending.values()) request.controller.abort();
    this.pending.clear();
  }
}
