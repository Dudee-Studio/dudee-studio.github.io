"""Mix the approved 42-second story. Uses cached sources, never accesses an API."""
import json
import wave
from pathlib import Path
import numpy as np
from voice_mix import decode, rms_normalize, RATE

ROOT = Path(__file__).resolve().parents[1]
DURATION = 42
EVENTS = [(5.15, 'add'), (14.0, 'add'), (16.15, 'tick'), (18.15, 'tick'), (20.15, 'tick'), (22.15, 'tick'), (27.0, 'add'), (32.15, 'add'), (34.3, 'complete')]


def build(path, app):
    length = DURATION * RATE
    music = decode(ROOT/'assets/audio/store42-instrumental.mp3')
    if len(music) < length - RATE // 2:
        raise ValueError('The commissioned music is shorter than the approved cut')
    music = np.pad(music[:length], ((0, max(0, length-len(music))), (0, 0)))
    music = rms_normalize(music, -22)
    voice = np.zeros((length, 2))
    effects = np.zeros_like(voice)
    duck = np.ones(length)
    script = json.loads((ROOT/'assets/audio/de/store42-script.json').read_text())
    silence = 'silenceremove=start_periods=1:start_duration=0.02:start_threshold=-45dB:start_silence=0.025'
    trimming = f'{silence},areverse,{silence},areverse,highpass=f=75'
    timing = []
    previous_end = 0
    for i, row in enumerate(script['segments']):
        source = ROOT/f'assets/audio/de/store42/{i:02d}.mp3'
        clip = decode(source, trimming)
        start = row['start'] + (.12 if i == 0 else .06)
        available = row['end'] - start - .06
        original = len(clip)/RATE
        tempo = max(1, original/available)
        if tempo > 1.10:
            raise ValueError(f'Clip {i} needs a shorter line: {original:.2f}s for {available:.2f}s')
        if tempo > 1.001:
            clip = decode(source, trimming+f',atempo={tempo:.6f}')
        clip = rms_normalize(clip, -19)
        peak = np.max(np.abs(clip))
        if peak > .8: clip *= .8/peak
        n = min(720, len(clip)//4)
        clip[:n] *= np.linspace(0, 1, n)[:, None]
        clip[-n:] *= np.linspace(1, 0, n)[:, None]
        at = round(start*RATE)
        end = at+len(clip)
        if at < previous_end or end > length:
            raise ValueError('Narration overlaps or is truncated')
        voice[at:end] += clip
        previous_end = end
        lo = max(0, at-round(.10*RATE)); hi = min(length, end+round(.28*RATE))
        envelope = np.concatenate([np.linspace(1, .40, at-lo), np.full(end-at, .40), np.linspace(.40, 1, hi-end)])
        duck[lo:hi] = np.minimum(duck[lo:hi], envelope)
        timing.append({'segment':i,'start':round(start,3),'end':round(end/RATE,3),'tempo':round(tempo,4),'original_seconds':round(original,3),'text':row['text']})
    for at, name in EVENTS:
        clip = decode(app/f'app/src/main/res/raw/snd_{name}.ogg')
        clip = rms_normalize(clip, -31)
        pos=round(at*RATE); n=min(len(clip), length-pos)
        effects[pos:pos+n] += clip[:n]
    t=np.arange(length)/RATE
    # Very short opening fade retains immediate groove; keep the composed ending.
    music *= (np.minimum(1,t/.10)*np.minimum(1,(DURATION-t)/.18))[:,None]
    mix = voice + music*duck[:,None] + effects
    peak=np.max(np.abs(mix))
    if peak>.94:mix*=.94/peak
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE)
        w.writeframes(np.round(np.clip(mix,-1,1)*32767).astype('<i2').tobytes())
    return {'duration':DURATION,'narration_provider':'ElevenLabs','narration_model':script['profile']['model'],'voice_name':script['profile']['voice_name'],'voice_id':script['profile']['voice_id'],'music_provider':'ElevenLabs','music_bpm_prompt':120,'ducking_gain':.4,'speech':timing,'effects':[{'time':t,'cue':n} for t,n in EVENTS],'loudness_target_lufs':-16,'true_peak_target_dbtp':-2}
