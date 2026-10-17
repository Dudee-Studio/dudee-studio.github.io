#!/usr/bin/env python3
"""Render the approved 22s catalogue feature from actual Compose captures and cached audio.
No network/API calls. Captures: tools/capture/CatalogFeatureCapture.kt, remote responses are demo data.
"""
import json, subprocess, sys, wave, math
from pathlib import Path
import numpy as np
from voice_mix import decode, rms_normalize, RATE
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/catalog-v1.1'
ASSETS=ROOT/'assets/einkaufsliste/catalog-v1.1'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
W,H,FPS=1280,720,30

def run(args): subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
def ts(t):
 ms=round(t*1000); return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d}.{ms%1000:03d}'
def captions():
 transcript=json.loads((ROOT/'assets/audio/de/catalog-v1.1/transcript.json').read_text())
 words=[w for w in transcript['words'] if w['type']=='word']
 cues=[];group=[]
 for word in words:
  text=' '.join(x['text'] for x in group+[word])
  if group and (len(text)>43 or word['end']-group[0]['start']>3 or word['start']-group[-1]['end']>.45):
   cues.append((group[0]['start'],group[-1]['end']+.10,' '.join(x['text'] for x in group)));group=[]
  group.append(word)
 if group:cues.append((group[0]['start'],min(22,group[-1]['end']+.12),' '.join(x['text'] for x in group)))
 for i in range(len(cues)-1):
  a,b,text=cues[i];cues[i]=(a,min(b,cues[i+1][0]-.01),text)
 text='WEBVTT\n\n'+'\n\n'.join(f'{ts(a)} --> {ts(b)}\n{s}' for a,b,s in cues)+'\n'
 (ROOT/'videos/artikelkatalog-1.1-de.vtt').write_text(text)
 ass='''[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,36,&H00FFFFFF,&H00FFFFFF,&H20162A1A,&H20162A1A,0,0,0,0,100,100,0,0,3,8,0,2,70,70,25,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
 def at(t):return f'{int(t)//3600}:{int(t)//60%60:02d}:{t%60:05.2f}'
 for a,b,s in cues:ass+=f'Dialogue: 0,{at(a)},{at(b)},Default,,0,0,0,,{s}\n'
 (OUT/'captions.ass').write_text(ass)
 return cues

def audio():
 folder=ROOT/'assets/audio/de/catalog-v1.1';script=json.loads((folder/'script.json').read_text());n=22*RATE
 voice=np.zeros((n,2));duck=np.ones(n)
 trim='silenceremove=start_periods=1:start_duration=0.02:start_threshold=-45dB:start_silence=0.03'
 for row,start in zip(script['segments'],[.15,4.05,9.65,14.30,19.0]):
  a=decode(folder/row['file'],trim+',areverse,'+trim+',areverse,highpass=f=75');a=rms_normalize(a,-19)
  a*=min(1,.85/max(np.max(np.abs(a)),1e-6));at=round(start*RATE);end=at+len(a);assert end<n
  fade=min(480,len(a)//3);a[:fade]*=np.linspace(0,1,fade)[:,None];a[-fade:]*=np.linspace(1,0,fade)[:,None];voice[at:end]+=a
  lo=max(0,at-round(.10*RATE));hi=min(n,end+round(.20*RATE))
  env=np.r_[np.linspace(1,.45,at-lo),np.full(end-at,.45),np.linspace(.45,1,hi-end)];duck[lo:hi]=np.minimum(duck[lo:hi],env)
  row.update(start=round(start,3),end=round(end/RATE,3))
 music=decode(ROOT/'assets/audio/store42-instrumental.mp3');over=round(.5*RATE);first=music[:n-3*RATE+over];ending=music[-3*RATE:];phase=np.linspace(0,np.pi/2,over)[:,None]
 music=np.concatenate([first[:-over],first[-over:]*np.cos(phase)+ending[:over]*np.sin(phase),ending[over:]])[:n];music=rms_normalize(music,-23)
 t=np.arange(n)/RATE;music*=(np.minimum(1,t/.12)*np.minimum(1,(22-t)/.25))[:,None];effects=np.zeros_like(voice)
 for at,name in [(9.4,'add'),(12.9,'tick'),(17.0,'add')]:
  a=rms_normalize(decode(ROOT.parent/'Einkaufsliste/app/src/main/res/raw'/f'snd_{name}.ogg'),-31);pos=round(at*RATE);effects[pos:pos+len(a)]+=a
 mix=voice+music*duck[:,None]+effects;mix*=min(1,.96/max(np.max(np.abs(mix)),1e-8))
 for name,a in [('voice',voice),('mix',mix)]:
  with wave.open(str(OUT/f'{name}.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE);w.writeframes((np.clip(a,-1,1)*32767).astype('<i2').tobytes())
 (folder/'timing.json').write_text(json.dumps(script,ensure_ascii=False,indent=2)+'\n')

def main():
 OUT.mkdir(parents=True,exist_ok=True);audio();captions()
 # All motion comes from successive actions and cuts, never a global pan or zoom.
 shots=json.loads((ROOT/'videos/artikelkatalog-1.1-shots.json').read_text())
 files=[]
 for i,shot in enumerate(shots):
  source=ROOT/shot['image'];vf=[]
  if shot['kind']=='photo':
   x,y=shot['panel'];vf=[f'crop=iw/2:ih/2:iw/2*{x}:ih/2*{y}','scale=1280:720:force_original_aspect_ratio=increase:out_color_matrix=bt709','crop=1280:720','setsar=1']
  else:
   x,y,w,h=shot['crop'];targetw=shot.get('width',1120);targeth=round(h*targetw/w)//2*2
   vf=[f'crop={w}:{h}:{x}:{y}',f'scale={targetw}:{targeth}:out_color_matrix=bt709',f'pad=1280:720:(ow-iw)/2:{shot.get("top",130)}:color=0xf1f6ef','setsar=1']
  filters=','.join(vf)
  if shot.get('label'):
   label=OUT/f'label-{i}.txt';label.write_text(shot['label'])
   if shot['kind']=='photo':filters+=",drawbox=x=0:y=0:w=iw:h=100:color=0x102617@0.60:t=fill"
   filters+=f",drawtext=fontfile={BOLD}:textfile={label}:fontcolor={'white' if shot['kind']=='photo' else '0x183c26'}:fontsize=36:x=52:y=34"
  filters+=f",drawbox=x=974:y=14:w=292:h=46:color=0x183c26@0.94:t=fill,drawtext=fontfile={FONT}:text='Vorschau · Version 1.1':fontcolor=white:fontsize=22:x=988:y=25"
  if shot['kind']!='photo':filters+=f",drawtext=fontfile={FONT}:text='App mit Beispieldaten':fontcolor=0x183c26:fontsize=18:x=w-tw-28:y=94"
  if shot.get('closing'):
   filters+=f",drawbox=x=0:y=464:w=iw:h=112:color=0x102617@0.78:t=fill,drawtext=fontfile={BOLD}:text='Abgehakt':fontcolor=white:fontsize=49:x=52:y=480,drawtext=fontfile={FONT}:text='Mehr Zeit fürs Leben.':fontcolor=white:fontsize=29:x=330:y=496"
  path=OUT/f'shot-{i:02d}.mp4'
  cmd=['ffmpeg','-v','error','-y','-loop','1','-i',str(source)]
  if shot.get('closing'):
   cmd+=['-loop','1','-i',str(ROOT/'assets/abgehakt/mark.png'),'-filter_complex',f'[0:v]{filters}[base];[1:v]scale=72:72[mark];[base][mark]overlay=1136:484:shortest=1']
  else:cmd+=['-vf',filters]
  cmd+=['-t',str(shot['duration']),'-r',str(FPS),'-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv',str(path)]
  try:run(cmd)
  except subprocess.CalledProcessError as e:print(e.stderr.decode(),file=sys.stderr);raise
  files.append(path)
 concat=OUT/'concat.txt';concat.write_text(''.join(f"file '{p}'\n" for p in files))
 silent=OUT/'picture.mp4';run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(silent)])
 for store in [False,True]:
  path=ROOT/'videos'/('artikelkatalog-1.1-store.mp4' if store else 'artikelkatalog-1.1.mp4')
  cmd=['ffmpeg','-v','error','-y','-i',str(silent),'-i',str(OUT/'mix.wav'),'-map','0:v:0','-map','1:a:0']
  if store:cmd+=['-vf',f'ass={OUT}/captions.ass','-c:v','libx264','-crf','18','-preset','fast']
  else:cmd+=['-vf','setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-c:v','libx264','-crf','18','-preset','fast']
  cmd+=['-af','loudnorm=I=-16:TP=-2:LRA=9','-c:a','aac','-b:a','192k','-ar','48000','-t','22','-movflags','+faststart',str(path)]
  run(cmd)
 print('Rendered website and captioned store exports (22 seconds).')
if __name__=='__main__':main()
