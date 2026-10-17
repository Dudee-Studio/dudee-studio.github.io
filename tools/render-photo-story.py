#!/usr/bin/env python3
"""Render two photographic stories from approved 2x2 sequential image sheets.

No paid API calls. Usage: python tools/render-photo-story.py MANIFEST.json
The manifest points to generated originals, app captures, and cached narration.
"""
import json
import math
import shutil
import subprocess
import sys
import textwrap
import wave
from pathlib import Path

import numpy as np
from PIL import Image
from voice_mix import decode, rms_normalize, RATE

ROOT = Path(__file__).resolve().parents[1]
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FPS = 24
W, H = 1280, 720


def run(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


def audio(folder, kind):
    script = json.loads((folder/f'{kind}-script.json').read_text())
    clips = []
    cursor = .35
    trim = 'silenceremove=start_periods=1:start_duration=0.02:start_threshold=-45dB:start_silence=0.03'
    for i, row in enumerate(script['segments']):
        clip = decode(folder/f'{kind}-{i:02d}.mp3', trim+',areverse,'+trim+',areverse,highpass=f=75')
        clip = rms_normalize(clip, -19)
        peak = np.max(np.abs(clip))
        if peak > .85:
            clip *= .85/peak
        n = min(480, len(clip)//4)
        clip[:n] *= np.linspace(0, 1, n)[:, None]
        clip[-n:] *= np.linspace(1, 0, n)[:, None]
        row.update(start=round(cursor, 3), end=round(cursor+len(clip)/RATE, 3))
        clips.append((cursor, clip))
        cursor += len(clip)/RATE + .18
    seconds = max(script['duration'], math.ceil(cursor+.3))
    length = seconds*RATE
    voice = np.zeros((length, 2))
    duck = np.ones(length)
    for start, clip in clips:
        at = round(start*RATE)
        end = at+len(clip)
        voice[at:end] += clip
        lo = max(0, at-round(.12*RATE))
        hi = min(length, end+round(.28*RATE))
        env = np.concatenate([np.linspace(1, .32, at-lo), np.full(end-at, .32), np.linspace(.32, 1, hi-end)])
        duck[lo:hi] = np.minimum(duck[lo:hi], env)
    source = decode(ROOT/'assets/audio/store42-instrumental.mp3')
    # Retain the existing composition's actual ending, joined with an equal-power crossfade.
    overlap = round(.5*RATE)
    first = source[:length-3*RATE+overlap]
    ending = source[-3*RATE:]
    phase = np.linspace(0, math.pi/2, overlap)[:, None]
    bridge = first[-overlap:]*np.cos(phase)+ending[:overlap]*np.sin(phase)
    music = np.concatenate([first[:-overlap], bridge, ending[overlap:]])[:length]
    music = rms_normalize(music, -23)
    t = np.arange(length)/RATE
    music *= (np.minimum(1, t/.15)*np.minimum(1, (seconds-t)/.45))[:, None]
    effects = np.zeros_like(voice)
    app_audio = ROOT.parent/'Einkaufsliste/app/src/main/res/raw'
    cues = [(script['segments'][2]['start']+1.0, 'tick')] if kind == 'kostenlos' else [(script['segments'][1]['start']+.4, 'add'), (script['segments'][2]['end']-.5, 'add')]
    for at, name in cues:
        clip = rms_normalize(decode(app_audio/f'snd_{name}.ogg'), -32)
        offset = round(at*RATE)
        count = min(len(clip), length-offset)
        effects[offset:offset+count] += clip[:count]
    mix = voice + music*duck[:, None] + effects
    peak = np.max(np.abs(mix))
    if peak > .95:
        mix *= .95/peak
    path = folder/f'{kind}-mix.wav'
    with wave.open(str(path), 'wb') as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(RATE)
        out.writeframes((mix*32767).astype('<i2').tobytes())
    script.update(duration=seconds, music='Existing commissioned ElevenLabs store42 instrumental', tempo_change=1)
    (folder/f'{kind}-timing.json').write_text(json.dumps(script, ensure_ascii=False, indent=2)+'\n')
    return path, script


def stamp(t):
    ms = round(t*1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}'


def captions(folder, kind, script):
    """Short synchronized phrases, rather than a paragraph covering the picture."""
    transcript = folder/f'{kind}-transcript.json'
    if transcript.exists():
        words = [w for w in json.loads(transcript.read_text())['words'] if w['type'] == 'word']
    else:
        words = []
        for row in script['segments']:
            tokens = row['text'].split()
            step = (row['end']-row['start'])/len(tokens)
            words.extend({'text': t, 'start': row['start']+i*step, 'end': row['start']+(i+1)*step} for i, t in enumerate(tokens))
    groups, pending = [], []
    for word in words:
        if pending and (len(' '.join(w['text'] for w in pending+[word])) > 46 or word['end']-pending[0]['start'] > 3):
            groups.append(pending)
            pending = []
        pending.append(word)
        if word['text'].endswith(('.', '?', '!')):
            groups.append(pending)
            pending = []
    if pending:
        groups.append(pending)
    rows = [{'start': g[0]['start'], 'end': g[-1]['end']+.12, 'text': ' '.join(w['text'] for w in g)} for g in groups]
    for row, following in zip(rows, rows[1:]):
        row['end'] = min(row['end'], following['start'])
    vtt, srt = 'WEBVTT\n\n', ''
    for i, row in enumerate(rows, 1):
        text = '\n'.join(textwrap.wrap(row['text'], 46))
        vtt += f'{stamp(row["start"])} --> {stamp(row["end"])}\n{text}\n\n'
        srt += f'{i}\n{stamp(row["start"]).replace(".", ",")} --> {stamp(row["end"]).replace(".", ",")}\n{text}\n\n'
    (folder/f'abgehakt-{kind}.vtt').write_text(vtt.rstrip()+'\n')
    path = folder/f'abgehakt-{kind}.srt'
    path.write_text(srt.rstrip()+'\n')
    return path


def render(manifest, kind):
    folder = Path(manifest['output'])
    folder.mkdir(parents=True, exist_ok=True)
    work = folder/kind
    work.mkdir(exist_ok=True)
    sound, script = audio(folder, kind)
    seg = script['segments']
    end = script['duration']
    if kind == 'kostenlos':
        blocks = [('sofa', 0, seg[2]['start'], 'Zu Hause planen.'),
                  ('market', seg[2]['start'], seg[4]['start'], 'Im Laden abhaken.'),
                  ('table', seg[4]['start'], seg[5]['start'], 'Ausgaben im Blick.'),
                  ('table', seg[5]['start'], end, 'Abgehakt. Dein Einkauf im Griff.')]
        app = [(seg[0]['end']-1, seg[1]['start']+2.6, '01-catalog', 'Deine Artikel'),
               (seg[1]['start']+2.6, seg[1]['start']+4.7, '02-forecast', 'Einkaufsvorschläge'),
               (seg[1]['start']+4.7, seg[2]['start'], '05-dishes', 'Gerichte & Zutaten'),
               (seg[2]['start']+.7, seg[2]['end'], '09-check-two', 'Deine Einkaufsliste'),
               (seg[4]['start']+.4, seg[5]['start'], '@basic', 'Einfache Ausgabenübersicht')]
    else:
        blocks = [('pro', 0, seg[1]['start'], 'Eine Liste. Gemeinsam.'),
                  ('market', seg[1]['start'], seg[2]['start'], 'Zu Hause ergänzt. Im Laden dabei.'),
                  ('scanner', seg[2]['start'], seg[3]['start'], 'Scannen statt abtippen.'),
                  ('table', seg[3]['start'], seg[4]['start'], 'Ausgaben genauer verstehen.'),
                  ('table', seg[4]['start'], end, 'Abgehakt Pro. Ohne Abo.')]
        app = [(seg[1]['start'], seg[2]['start'], '12-group-added', 'Einladen mit Pro · Beitritt kostenlos · Demo'),
               (seg[2]['end']-1.9, seg[3]['start'], '13-scanned', 'Scan-Demo · Daten, wenn verfügbar'),
               (seg[3]['start']+.3, seg[4]['start'], '16-analysis', 'Erweiterte Analysen')]
    # Four genuinely different action states in every scene, with a short stop-motion burst.
    clips = []
    timeline = []
    for b, (name, start, finish, title) in enumerate(blocks):
        duration = finish-start
        if b == len(blocks)-1:
            states = [(3, duration)]
        else:
            middle = min(.5, duration*.15)
            states = [(0, (duration-2*middle)*.5), (1, middle), (2, middle), (3, (duration-2*middle)*.5)]
        split_states = []
        pos = start
        for state, dur in states:
            boundaries = sorted({pos, pos+dur, *[t for row in app for t in row[:2] if pos < t < pos+dur]})
            split_states.extend((state, hi-lo) for lo, hi in zip(boundaries, boundaries[1:]))
            pos += dur
        states = split_states
        cursor = start
        for state, dur in states:
            count = max(1, round(dur*FPS))
            dur = count/FPS
            path = work/f'{len(clips):02d}.mp4'
            sheet = Path(manifest['sheets'][name])
            sw, sh = Image.open(sheet).size
            cw, ch = sw//2, sh//2
            cx, cy = (state%2)*cw, (state//2)*ch
            args = ['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-i', str(sheet)]
            graph = [f'[0:v]crop={cw}:{ch}:{cx}:{cy},scale=1440:810:force_original_aspect_ratio=increase,crop=1440:810:0:0,zoompan=z=1.035:x=\'iw/2-iw/zoom/2+10*sin(on/60)\':y=0:d=1:s={W}x{H}:fps={FPS},setsar=1[v0]']
            current = 'v0'
            # Readable real app insert. Deliberately separate from the photographed blank phone.
            center = cursor+dur/2
            overlay = next((row for row in app if row[0] <= center < row[1]), None)
            if overlay:
                _, _, shot, label = overlay
                screen = Path(manifest['app'])/'app/build/store42'/f'{shot}.png'
                if shot == '@basic':
                    screen = Path(manifest['app'])/'app/build/screenshots/4-analyse.png'
                args += ['-loop', '1', '-i', str(screen)]
                iw, ih = Image.open(screen).size
                crop = ''
                if shot == '@basic':
                    ih = 760
                    crop = 'crop=1080:760:0:0,'
                # Dialog screenshots keep their natural aspect instead of stretching to phone height.
                height = min(466, round(256*ih/iw))
                graph += [f'[{current}]drawbox=x=980:y=88:w=280:h={height+58}:color=0x123B2E@0.94:t=fill[panel]',
                          f'[1:v]{crop}scale=256:{height}:force_original_aspect_ratio=decrease,format=rgba[app]',
                          f'[panel][app]overlay=992:100[insert]']
                current = 'insert'
                label_file = work/f'{len(clips):02d}-app.txt'
                label_file.write_text('\n'.join(textwrap.wrap(label, 31)))
                graph.append(f'[{current}]drawtext=fontfile={FONT}:textfile={label_file}:fontsize=12:fontcolor=white:x=992:y={height+110}[label]')
                current = 'label'
            text_file = work/f'{len(clips):02d}-title.txt'
            text_file.write_text(title)
            graph.append(f'[{current}]drawbox=x=0:y=0:w=1280:h=77:color=black@0.28:t=fill,drawtext=fontfile={BOLD}:textfile={text_file}:fontsize=30:fontcolor=white:x=36:y=25,format=yuv420p[out]')
            args += ['-filter_complex_threads', '1', '-filter_complex', ';'.join(graph), '-map', '[out]', '-frames:v', str(count), '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '21', '-threads', '2', str(path)]
            run(args)
            clips.append(path)
            timeline.append({'scene': name, 'state': state, 'start': round(cursor, 3), 'duration': dur, 'app_insert': overlay[2] if overlay else None})
            cursor += dur
            print(f'{kind}: frame-state {len(clips)} rendered', flush=True)
    listing = work/'concat.txt'
    listing.write_text(''.join(f"file '{path}'\n" for path in clips))
    subtitles = captions(folder, kind, script)
    output = folder/f'abgehakt-{kind}.mp4'
    vf = f"subtitles={subtitles}:force_style='FontName=DejaVu Sans,FontSize=15,PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,BorderStyle=3,Outline=2,Shadow=0,MarginV=12',fade=t=out:st={end-.3}:d=0.3"
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(listing), '-i', str(sound), '-vf', vf, '-af', 'loudnorm=I=-16:TP=-2:LRA=7,aresample=48000', '-t', str(end), '-c:v', 'libx264', '-preset', 'fast', '-crf', '21', '-threads', '2', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(output)])
    (folder/f'{kind}-timeline.json').write_text(json.dumps(timeline, ensure_ascii=False, indent=2)+'\n')
    run(['ffmpeg', '-v', 'error', '-y', '-ss', '1', '-i', str(output), '-frames:v', '1', str(folder/f'{kind}-poster.jpg')])
    print(f'Finished {output}', flush=True)


if __name__ == '__main__':
    data = json.loads(Path(sys.argv[1]).read_text())
    for field in ['output', 'app']:
        if not Path(data[field]).is_absolute():
            data[field] = str((ROOT/data[field]).resolve())
    for name, path in data['sheets'].items():
        if not Path(path).is_absolute():
            data['sheets'][name] = str((ROOT/path).resolve())
    if data.get('audio_source'):
        target = Path(data['output'])
        target.mkdir(parents=True, exist_ok=True)
        for source in (ROOT/data['audio_source']).iterdir():
            if source.name.endswith(('-script.json', '-transcript.json', '.mp3')):
                shutil.copyfile(source, target/source.name)
    for variant in ['kostenlos', 'pro']:
        render(data, variant)
