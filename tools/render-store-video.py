#!/usr/bin/env python3
"""Render the approved 42s shopping story from real Compose action states.
No API calls. Usage: python tools/render-store-video.py /path/to/Einkaufsliste
"""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image
from store42_audio import build as build_audio

ROOT=Path(__file__).resolve().parents[1]
APP=Path(sys.argv[1]); CAP=APP/'app/build/store42'; ART=ROOT/'assets/abgehakt'
spec=importlib.util.spec_from_file_location('base_renderer', ROOT/'tools/render-app-video.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
Shot=base.Shot
FPS=24; TRANSITION=1/6
# start, end, source, short action heading, background for actual modal windows
SCENES=[
 (0,2,'01-catalog','Was fehlt?',None),
 (2,2.75,'01b-list-forecast','Abgehakt denkt mit.',None),
 (2.75,5,'02-forecast','Vorschläge prüfen.','01b-list-forecast'),
 (5,7,'03-catalog-filled','Mit einem Tipp ergänzt.',None),
 (7,9,'04-recurring','Dein eigener Rhythmus.','03b-list-filled'),
 (9,11.25,'05-dishes','Heute Pasta?',None),
 (11.25,13.75,'06-ingredients','Zutaten übernehmen.','05-dishes'),
 (13.75,16,'07-prepared','Deine Liste steht.',None),
 (16,18,'08-check-one','Einfach abhaken.',None),
 (18,20,'09-check-two','Einfach abhaken.',None),
 (20,22,'10-check-three','Alles im Blick.',None),
 (22,24,'10b-check-four','Angebote & Coupons inklusive.',None),
 (24,27,'11-group-before','Gemeinsam einkaufen.',None),
 (27,30,'12-group-added','Zitronen ergänzt.',None),
 (30,32,'@scan','Spontan entdeckt?',None),
 (32,34,'13-scanned','Gescannt. Auf deiner Liste.',None),
 (34,35,'15-finished','Einkauf erledigt.',None),
 (35,37,'16-analysis','Ausgaben genauer verstehen.',None),
 (37,42,'@end','Abgehakt',None),
]


def run(*args):
    subprocess.run(args,check=True,stdout=subprocess.DEVNULL)


def screen(s,path,zoom=False):
    effects=",zoompan=z='1.015+0.025*min(on/45,1)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=640x1138:fps=24" if zoom else ''
    s.image(path,640,1138,40,72,effects=effects)


def labels(s,start,title):
    s.box(0,0,720,70,'0x103B2D')
    s.text(title,23 if len(title)>25 else 26,24,bold=True,color='0xF6F8F0',x='30')
    is_pro=start>=24
    s.box(538 if is_pro else 528,15,150 if is_pro else 160,40,'0xF7B62B' if is_pro else '0xD9EFE3')
    s.text('MIT PRO' if is_pro else 'KOSTENLOS',17,26,bold=True,color='0x163B2B',x='565' if is_pro else '550')
    demo='Scan-Demo · Produktdaten, wenn verfügbar' if 30<=start<34 else 'Einladen mit Pro · Beitritt kostenlos · Sync-Demo' if 27<=start<30 else 'Für Freunde, WG und Familie · Sync-Demo' if 24<=start<27 else 'App-Ansichten mit Demo-Daten'
    s.text(demo,17,1234,color='0xE3EBE4')


def make_scene(folder,index,row,product):
    start,end,name,title,background=row
    d=end-start
    f=folder/str(index);f.mkdir()
    s=Shot(f)
    s.args=[arg.replace('color=c=0xF6F8F0','color=c=0x103B2D') for arg in s.args]
    if name=='@end':
        s.image(ART/'mark.png',180,180,270,166,effects=',fade=t=in:st=0:d=0.2:alpha=1')
        s.text('Abgehakt',62,397,bold=True,color='0xF6F8F0')
        s.text('Dein Einkauf im Griff.',29,488,color='0xF6F8F0')
        s.text('Kostenlose Basis.',26,596,color='0xD9EFE3')
        s.text('Pro einmalig',30,716,bold=True,color='0xF6F8F0')
        s.text('3,99 €',88,780,bold=True,color='0xF7B62B')
        s.text('Kein Abo.',34,903,bold=True,color='0xF6F8F0')
        s.text('Deutscher Basispreis',17,985,color='0xD9EFE3')
        s.text('Andere treten kostenlos bei.',23,1105,color='0xF6F8F0')
    elif name=='@scan':
        # Explicit schematic, not a fabricated live camera capture.
        s.box(40,72,640,1138,'0xE8F1E6')
        s.image(product,360,540,180,294,effects=",zoompan=z='1.0+0.04*min(on/30,1)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=360x540:fps=24")
        for x,y,w,h in [(124,330,80,5),(124,330,5,80),(516,330,80,5),(591,330,5,80),(124,845,80,5),(124,770,5,80),(516,845,80,5),(591,770,5,80)]:s.box(x,y,w,h,'0x246B3D')
        s.image(folder/'scan-line.png',428,4,146,"'580+110*sin(t*4)'")
        s.text('Barcode erkennen',29,974,bold=True)
        labels(s,start,title)
    else:
        path=CAP/(name+'.png')
        if background:
            screen(s,CAP/(background+'.png'))
            s.box(40,72,640,1138,'0x103B2D@0.30')
            width,height=Image.open(path).size
            h=round(640*height/width)
            s.image(path,640,h,40,round(72+(1138-h)/2))
        else:
            screen(s,path,zoom=name in ['01-catalog','03-catalog-filled','05-dishes','16-analysis'])
        labels(s,start,title)
    clip=folder/f'{index:02d}.mp4'
    pad=TRANSITION/2 if index in (0,len(SCENES)-1) else TRANSITION
    s.finish(clip,d+pad)
    return clip


def main():
    output=ROOT/'videos/einkaufsliste-gerichte.mp4'
    with tempfile.TemporaryDirectory(prefix='abgehakt-store42-') as tmp:
        tmp=Path(tmp)
        product=tmp/'product.png'
        run('ffmpeg','-v','error','-y','-i',str(ART/'store42-product.svg'),'-frames:v','1',str(product))
        run('ffmpeg','-v','error','-y','-i',str(ART/'store42-scan-line.svg'),'-frames:v','1',str(tmp/'scan-line.png'))
        clips=[]
        for i,row in enumerate(SCENES):
            print(f'Rendering {i+1}/{len(SCENES)}: {row[2]}',flush=True)
            clips.append(make_scene(tmp,i,row,product))
        audio=tmp/'mix.wav';meta=build_audio(audio,APP)
        args=['ffmpeg','-v','error','-y']
        for clip in clips:args+=['-threads','1','-i',str(clip)]
        args+=['-i',str(audio)]
        graph=[f'[{i}:v]setpts=PTS-STARTPTS,fps={FPS},format=yuv420p[v{i}]' for i in range(len(clips))]
        last='v0';length=SCENES[0][1]+TRANSITION/2
        transitions=[]
        for i in range(1,len(clips)):
            offset=length-TRANSITION
            mode='smoothleft' if SCENES[i][0] in (9,24,30) else 'fade'
            label=f'x{i}'
            graph.append(f'[{last}][v{i}]xfade=transition={mode}:duration={TRANSITION}:offset={offset},fps={FPS}[{label}]')
            last=label;length+=SCENES[i][1]-SCENES[i][0]+(TRANSITION/2 if i==len(clips)-1 else TRANSITION)-TRANSITION
            transitions.append({'time':round(offset,3),'style':mode,'duration':TRANSITION})
        graph.append(f'[{last}]fade=t=out:st=41.85:d=0.15,format=yuv420p[video]')
        graph.append(f'[{len(clips)}:a]loudnorm=I=-16:TP=-2:LRA=7,aresample=48000[audio]')
        final=tmp/'final.mp4'
        run(*args,'-filter_complex_threads','1','-filter_complex',';'.join(graph),'-map','[video]','-map','[audio]','-t','42','-c:v','libx264','-preset','fast','-crf','22','-threads','2','-c:a','aac','-b:a','160k','-ar','48000','-ac','2','-movflags','+faststart',str(final))
        shutil.copyfile(final,output)
        meta['transitions']=transitions
        (ROOT/'videos/overview-sound.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
        base.write_sound_outputs(meta,False)
        (ROOT/'videos/store42-storyboard.json').write_text(json.dumps(SCENES,ensure_ascii=False,indent=2)+'\n')
        (ROOT/'videos/storyboard.json').write_text(json.dumps(SCENES,ensure_ascii=False,indent=2)+'\n')
        run('ffmpeg','-v','error','-y','-ss','0.75','-i',str(output),'-frames:v','1','-q:v','3',str(ROOT/'assets/einkaufsliste/poster.jpg'))
    print(output)


if __name__=='__main__':main()
