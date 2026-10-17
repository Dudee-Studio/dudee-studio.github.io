"""Mix cached ElevenLabs narration/music with timeline-aware ducking.

No API access here. Generation and credentials remain separate from rendering.
"""
import json
import subprocess
import tempfile
import wave
from pathlib import Path
import numpy as np
from video_soundtrack import soundtrack

ROOT = Path(__file__).resolve().parents[1]
RATE = 48000


def decode(path, filters=None, channels=2):
    args = ['ffmpeg', '-v', 'error', '-i', str(path)]
    if filters:
        args += ['-af', filters]
    data = subprocess.check_output(args + ['-ar', str(RATE), '-ac', str(channels), '-f', 'f32le', '-'])
    return np.frombuffer(data, dtype='<f4').reshape(-1, channels).astype(np.float64)


def rms_normalize(data, db):
    rms = np.sqrt(np.mean(data ** 2))
    return data * (10 ** (db / 20) / max(rms, 1e-8))


def build_voice_mix(path, scenes, teaser=False):
    seconds = sum(s[1] for s in scenes)
    length = round(seconds * RATE)
    source = decode(ROOT / 'assets/audio/abgehakt-instrumental.mp3')
    if len(source) < 60 * RATE:
        raise RuntimeError('Instrumental bed is shorter than 60 seconds')
    if teaser:
        # Keep the opening groove and the song's actual ending, rather than
        # abruptly cutting the first twenty seconds out of a longer track.
        first = source[:round((seconds - 3.5) * RATE)].copy()
        ending = source[-4 * RATE:].copy()
        overlap = round(.5 * RATE)
        phase = np.linspace(0, np.pi / 2, overlap)[:, None]
        bridge = first[-overlap:] * np.cos(phase) + ending[:overlap] * np.sin(phase)
        music = np.concatenate([first[:-overlap], bridge, ending[overlap:]])[:length]
    elif seconds > 60:
        # Extend the middle of the existing composition with equal-power
        # crossfades; retain its opening and original musical resolution.
        overlap = round(.5 * RATE)
        phase = np.linspace(0, np.pi / 2, overlap)[:, None]
        body = source[:-4 * RATE].copy()
        target = length - 4 * RATE + overlap
        middle = source[16 * RATE:48 * RATE]
        while len(body) < target:
            bridge = body[-overlap:] * np.cos(phase) + middle[:overlap] * np.sin(phase)
            body = np.concatenate([body[:-overlap], bridge, middle[overlap:]])
        body = body[:target]
        ending = source[-4 * RATE:]
        bridge = body[-overlap:] * np.cos(phase) + ending[:overlap] * np.sin(phase)
        music = np.concatenate([body[:-overlap], bridge, ending[overlap:]])
    else:
        music = source[:length].copy()
    music = rms_normalize(music, -24)
    voice = np.zeros((length, 2))
    duck = np.ones(length)
    kind = 'teaser' if teaser else 'overview'
    script = json.loads((ROOT / f'assets/audio/de/{kind}-script.json').read_text())
    timing = []
    silence = 'silenceremove=start_periods=1:start_duration=0.02:start_threshold=-45dB:start_silence=0.04'
    trimming = f'{silence},areverse,{silence},areverse,highpass=f=75'
    for i, segment in enumerate(script['segments']):
        clip_path = ROOT / f'assets/audio/de/{kind}/{i:02d}.mp3'
        clip = decode(clip_path, trimming)
        start = segment['start'] + (.30 if i == 0 else .10)
        available = segment['end'] - start - .10
        original = len(clip) / RATE
        tempo = max(1.0, original / available)
        if tempo > 1.10:
            raise RuntimeError(f'{kind} narration {i} needs shorter text: {original:.2f}s for {available:.2f}s')
        if tempo > 1.001:
            clip = decode(clip_path, f'{trimming},atempo={tempo:.6f}')
        clip = rms_normalize(clip, -20)
        if np.max(np.abs(clip)) > .75:
            clip *= .75 / np.max(np.abs(clip))
        fade = min(round(.015 * RATE), len(clip) // 3)
        clip[:fade] *= np.linspace(0, 1, fade)[:, None]
        clip[-fade:] *= np.linspace(1, 0, fade)[:, None]
        at = round(start * RATE)
        count = min(len(clip), length - at)
        voice[at:at + count] += clip[:count]
        down = max(0, at - round(.16 * RATE))
        up = min(length, at + count + round(.38 * RATE))
        envelope = np.ones(up - down)
        attack = at - down
        envelope[:attack] = np.linspace(1, .28, attack)
        envelope[attack:attack + count] = .28
        release = len(envelope) - attack - count
        if release > 0:
            envelope[-release:] = np.linspace(.28, 1, release)
        duck[down:up] = np.minimum(duck[down:up], envelope)
        timing.append({'segment':i, 'start':round(start, 3), 'end':round((at + count) / RATE, 3),
                       'original_seconds':round(original, 3), 'tempo':round(tempo, 4), 'text':segment['text']})
    t = np.arange(length) / RATE
    music *= (np.minimum(1, t / .6) * np.minimum(1, (seconds - t) / 1.0))[:, None]
    with tempfile.TemporaryDirectory(prefix='abgehakt-cues-') as tmp:
        cues = Path(tmp) / 'cues.wav'
        cue_metadata = soundtrack(cues, scenes, include_music=False)
        effects = decode(cues)[:length] * .32
    mix = music * duck[:, None] + voice + effects
    peak = np.max(np.abs(mix))
    if peak > .90:
        mix *= .90 / peak
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(np.round(np.clip(mix, -1, 1) * 32767).astype('<i2').tobytes())
    return {'duration':seconds, 'narration_provider':'ElevenLabs', 'voice_name':script['profile']['voice_name'],
            'voice_id':script['profile']['voice_id'], 'language':'de-DE', 'music_provider':'ElevenLabs',
            'music_bpm_prompt':112, 'ducking_gain':.28, 'speech':timing, 'effects':cue_metadata['events'],
            'loudness_target_lufs':-16, 'true_peak_target_dbtp':-2}
