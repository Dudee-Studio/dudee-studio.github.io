#!/usr/bin/env python3
"""Original procedural music and UI cues; no recordings or external services.

Loaded by render-app-video.py. Output is 48 kHz stereo PCM for the final mix.
"""
import math
import wave
import numpy as np

RATE = 48000
BPM = 100


def soundtrack(path, scenes, transition=0.5):
    duration = sum(scene[1] for scene in scenes)
    mix = np.zeros((round(duration * RATE), 2), dtype=np.float64)
    rng = np.random.default_rng(6719)

    def add(at, signal, level=1, pan=0):
        first = round(at * RATE)
        if first < 0:
            signal, first = signal[-first:], 0
        length = min(len(signal), len(mix) - first)
        if length <= 0:
            return
        angle = (pan + 1) * math.pi / 4
        mix[first:first + length, 0] += signal[:length] * level * math.cos(angle)
        mix[first:first + length, 1] += signal[:length] * level * math.sin(angle)

    def note(midi, seconds, softness=3):
        t = np.arange(round(seconds * RATE)) / RATE
        hz = 440 * 2 ** ((midi - 69) / 12)
        # Smooth onset and tail avoid discontinuities/clicks.
        envelope = (1 - np.exp(-t * 150)) * np.exp(-t * softness)
        envelope *= np.minimum(1, (seconds - t) / 0.06)
        return (np.sin(2 * math.pi * hz * t) + .16 * np.sin(4 * math.pi * hz * t)) * envelope

    beat = 60 / BPM
    progression = [(48, [60, 64, 67, 74]), (45, [57, 60, 64, 67]),
                   (41, [57, 60, 64, 69]), (43, [59, 62, 64, 67])]
    patterns = [[72, None, 76, 79, None, 76, 74, 72],
                [72, None, 76, 79, 81, None, 79, 76],
                [69, None, 72, 76, None, 74, 72, 69],
                [71, None, 74, 79, None, 76, 74, 71]]
    for bar in range(math.ceil(duration / (4 * beat))):
        start = bar * 4 * beat
        bass, chord = progression[bar % 4]
        # Sparse warm arpeggio; deliberately leaves space for the on-screen story.
        for step, midi in enumerate(chord):
            add(start + step * beat, note(midi, 1.35, 2.4), .032, (-1 if step % 2 else 1) * .35)
        for off in (0, 2 * beat):
            add(start + off, note(bass - 12, .65, 4), .10)
        for step, midi in enumerate(patterns[bar % 4]):
            if midi is not None:
                add(start + step * beat / 2, note(midi, .48, 7), .026, .18 * (-1) ** step)
        for step in range(4):
            at = start + step * beat
            if step % 2 == 0:
                t = np.arange(round(.16 * RATE)) / RATE
                kick = np.sin(2 * math.pi * (50 * t + 5 * (1 - np.exp(-t * 45)))) * np.exp(-t * 30)
                add(at, kick, .075)
            else:
                t = np.arange(round(.09 * RATE)) / RATE
                noise = rng.normal(0, 1, len(t))
                noise = np.convolve(noise, np.ones(9) / 9, mode='same')
                add(at, noise * np.exp(-t * 45), .032, -.2)

    events = []
    elapsed = 0
    for index, (source, seconds, *_rest) in enumerate(scenes):
        start = elapsed - (transition / 2 if index else 0)
        cue = None
        if source == '@intro':
            at, cue = .45, 'brand-confirm'
        elif source in ['promo/catalog-before.png', 'promo/barcode-before.png']:
            at, cue = start + seconds - .55, 'tap'
        elif source == '@family':
            at, cue = start + 2.2, 'sync'
        elif source == '@scan':
            at, cue = start + 1.8, 'scan'
        elif source in ['promo/catalog-after.png', 'promo/spontaneous.png', 'promo/barcode-after.png']:
            at, cue = start + .45, 'confirm'
        elif source in ['@end', '@teaser-end']:
            at, cue = start + .45, 'brand-confirm'
        if cue:
            events.append({'time': round(at, 3), 'cue': cue})
            if cue == 'tap':
                add(at, note(79, .07, 50), .085)
            else:
                pitches = [76, 83] if cue in ['scan', 'sync'] else [72, 79]
                for j, midi in enumerate(pitches):
                    add(at + j * .10, note(midi, .26, 14), .085, -.12 if j == 0 else .12)
        elapsed += seconds
    t = np.arange(len(mix)) / RATE
    fade = np.minimum(1, t / .75) * np.minimum(1, (duration - t) / 1.25)
    mix *= fade[:, None]
    # Conservative master headroom; final loudness/true-peak handled by FFmpeg.
    peak = np.max(np.abs(mix))
    if peak > .8:
        mix *= .8 / peak
    pcm = np.round(np.clip(mix, -1, 1) * 32767).astype('<i2')
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(pcm.tobytes())
    return {'sample_rate': RATE, 'bpm': BPM, 'duration': duration, 'events': events,
            'loudness_target_lufs': -18, 'true_peak_limit_dbtp': -1.5}
