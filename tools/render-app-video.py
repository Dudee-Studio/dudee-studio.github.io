#!/usr/bin/env python3
"""Render Abgehakt's captioned app overview with reusable motion graphics.
Usage: python tools/render-app-video.py /path/to/Einkaufsliste
"""
import json
import subprocess
import shutil
import sys
import tempfile
from pathlib import Path
from video_soundtrack import soundtrack
from voice_mix import build_voice_mix

TRANSITION = 0.5

ROOT = Path(__file__).resolve().parents[1]
APP = Path(sys.argv[1])
ART = ROOT / 'assets/abgehakt'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SCENES = [
    ('@intro', 3, 'Schon wieder', 'etwas vergessen?', ''),
    ('promo/catalog-before.png', 4, 'Was fehlt zu Hause?', 'Artikel durchgehen. Mit einem Tipp ergänzen.', ''),
    ('promo/catalog-after.png', 3, 'Deine Liste steht.', 'Vorher planen. Entspannter einkaufen.', ''),
    ('promo/dishes.png', 3, 'Was kochen wir?', 'Deine Gerichte helfen beim Planen.', ''),
    ('promo/dish-ingredients.png', 4, 'Zutaten direkt auf die Liste.', 'Für dein nächstes Essen vormerken.', ''),
    ('promo/list-before.png', 4, 'Im Laden einfach abhaken.', 'Alles Geplante auf deiner Liste.', ''),
    ('@family', 6, 'Eine Liste. Alle wissen Bescheid.', 'Gemeinsam planen statt Nachrichten hin und her.', 'GRUPPE MIT PRO · BEITRETEN KOSTENLOS'),
    ('@scan', 4, 'Spontan etwas entdeckt?', 'Mit Pro scannen statt abtippen.', 'BARCODE · MIT PRO · DATEN, WENN VERFÜGBAR'),
    ('promo/spontaneous.png', 4, 'Direkt auf deiner Liste.', 'Spontanen Einkauf per Barcode ergänzen.', 'BARCODE · MIT PRO · DEMO-SCAN'),
    ('promo/barcode-before.png', 2, 'Schon als Artikel angelegt?', 'Barcode ergänzen – auch ohne Foto.', 'BARCODE · MIT PRO'),
    ('promo/barcode-after.png', 3, 'Beim nächsten Scan wiederfinden.', 'Den gespeicherten Artikel direkt erkennen.', 'BARCODE · MIT PRO'),
    ('ui-previews/angebote.png', 3, 'Ein gutes Angebot?', 'Angebotspreis und Zeitraum festhalten.', ''),
    ('ui-previews/coupons.png', 3, 'Coupon dabei?', 'Rabatt beim Bezahlen berücksichtigen.', ''),
    ('ui-previews/letzter-angebotskauf-katalog.png', 4, 'War es zuletzt günstiger?', 'Letzten gekauften Angebotspreis mit Datum sehen.', ''),
    ('promo/analysis-pro.png', 4, 'Wo bleibt dein Einkaufsbudget?', 'Mit Pro Monatsverlauf und Abteilungen ansehen.', 'ERWEITERTE ANALYSE · MIT PRO'),
    ('@end', 6, 'Abgehakt', 'Dein Einkauf im Griff.', ''),
]
TEASER = [
    ('@intro', 3, 'Schon wieder', 'etwas vergessen?', ''),
    ('promo/catalog-after.png', 4, 'Entspannter einkaufen.', 'Vorher planen. Mit Artikeln und Gerichten.', 'KOSTENLOSE BASIS'),
    ('@family', 5, 'Eine Liste. Alle wissen Bescheid.', 'Gemeinsam planen statt Nachrichten hin und her.', 'GRUPPE MIT PRO · BEITRETEN KOSTENLOS'),
    ('promo/spontaneous.png', 4, 'Scannen statt eintippen.', 'Spontane Einkäufe direkt auf die Liste.', 'BARCODE · MIT PRO · DEMO-SCAN'),
    ('@teaser-end', 4, 'Abgehakt', 'Dein Einkauf im Griff.', ''),
]


def run(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


def write_sound_outputs(metadata, teaser):
    prefix = 'teaser' if teaser else 'overview'
    (ROOT / f'videos/{prefix}-sound.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    if 'speech' in metadata:
        def stamp(seconds):
            ms = round(seconds * 1000)
            return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d}.{ms%1000:03d}'
        cues = ['WEBVTT', '']
        for row in metadata['speech']:
            cues += [f'{stamp(row["start"])} --> {stamp(row["end"])}', row['text'], '']
        (ROOT / f'videos/{prefix}-de.vtt').write_text('\n'.join(cues))


class Shot:
    def __init__(self, folder):
        self.folder = folder
        self.args = ['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=0xF6F8F0:s=720x1280:r=24']
        self.filters = []
        self.base = '0:v'
        self.inputs = 0
        self.serial = 0

    def chain(self, effect):
        self.serial += 1
        label = f'b{self.serial}'
        self.filters.append(f'[{self.base}]{effect}[{label}]')
        self.base = label

    def text(self, label, size, y, bold=False, color='0x163B2B', x='(w-text_w)/2', extra=''):
        path = self.folder / f'text-{self.serial}.txt'
        path.write_text(label, encoding='utf-8')
        self.chain(f"drawtext=fontfile={BOLD if bold else FONT}:textfile={path}:fontsize={size}:fontcolor={color}:x='{x}':y='{y}'{extra}")

    def image(self, path, width, height, x, y, enable=None, effects=''):
        self.inputs += 1
        self.args += ['-loop', '1', '-i', str(path)]
        image = f'img{self.inputs}'
        self.filters.append(f'[{self.inputs}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=0xF6F8F0,format=rgba{effects}[{image}]')
        self.serial += 1
        label = f'b{self.serial}'
        condition = f":enable='{enable}'" if enable else ''
        self.filters.append(f'[{self.base}][{image}]overlay=x={x}:y={y}{condition}[{label}]')
        self.base = label

    def box(self, x, y, w, h, color, thickness='fill', enable=None):
        condition = f":enable='{enable}'" if enable else ''
        self.chain(f'drawbox=x={x}:y={y}:w={w}:h={h}:color={color}:t={thickness}{condition}')

    def chapter(self, current):
        for i, (label, x) in enumerate([('VORBEREITEN', 76), ('EINKAUFEN', 315), ('ÜBERBLICK', 537)]):
            self.text(label, 16, 176, bold=i == current, color='0x246B3D' if i == current else '0x788579', x=str(x))
            if i == current:
                self.box(x, 199, 116, 3, '0xF7B62B')

    def finish(self, path, duration):
        self.chain('format=yuv420p')
        run(*self.args, '-filter_complex_threads', '1', '-filter_complex', ';'.join(self.filters), '-map', f'[{self.base}]', '-t', str(duration), '-c:v', 'libx264', '-preset', 'fast', '-crf', '24', '-threads', '2', '-an', str(path))


def main():
    teaser = '--teaser' in sys.argv[2:]
    scenes = TEASER if teaser else SCENES
    output = ROOT / ('videos/abgehakt-kurz.mp4' if teaser else 'videos/einkaufsliste-gerichte.mp4')
    poster = ROOT / ('assets/einkaufsliste/teaser-poster.jpg' if teaser else 'assets/einkaufsliste/poster.jpg')
    if '--audio-only' in sys.argv[2:]:
        with tempfile.TemporaryDirectory(prefix='abgehakt-narration-') as tmp:
            tmp = Path(tmp)
            audio = tmp / 'mix.wav'
            metadata = build_voice_mix(audio, scenes, teaser)
            rendered = tmp / 'narrated.mp4'
            run('ffmpeg', '-v', 'error', '-y', '-i', str(output), '-i', str(audio),
                '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-af', 'loudnorm=I=-16:TP=-2:LRA=7,aresample=48000',
                '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-ac', '2', '-t', str(sum(s[1] for s in scenes)),
                '-movflags', '+faststart', str(rendered))
            shutil.copyfile(rendered, output)
            write_sound_outputs(metadata, teaser)
        print(output)
        return
    with tempfile.TemporaryDirectory(prefix='abgehakt-motion-') as folder:
        folder = Path(folder)
        icons = {}
        for name in ['scanner', 'family', 'analysis', 'product', 'shared-list', 'scan-line']:
            icons[name] = folder / (name + '.png')
            run('ffmpeg', '-v', 'error', '-y', '-i', str(ART / (name + '.svg')), '-frames:v', '1', str(icons[name]))
        clips = []
        for i, (source, duration, headline, subtitle, badge) in enumerate(scenes):
            shotdir = folder / str(i)
            shotdir.mkdir()
            s = Shot(shotdir)
            chapter = (0 if i < 5 else (1 if i < 13 else 2)) if not teaser else (0 if i < 2 else 1)
            if source == '@intro':
                s.image(ART / 'mark.png', 160, 160, 280, 140, effects=',fade=t=in:st=0:d=0.5:alpha=1')
                s.text('DUDEE STUDIO', 20, 83, bold=True)
                s.text('Abgehakt', 36, 331, bold=True)
                s.text(headline, 52, 461, bold=True)
                s.text(subtitle, 52, 536, bold=True)
                s.text('Dein Einkauf im Griff.', 29, 659)
                s.text('✓', 78, '780-16*min(t,1)', color='0x246B3D', extra=":alpha='clip((t-0.35)*3,0,1)'")
                s.text('Weniger im Kopf. Mehr auf deiner Liste.', 25, 959)
                s.text('Kostenlose Basis · optional Pro', 21, 1040, color='0x526256')
            elif source == '@teaser-end':
                s.image(ART / 'mark.png', 180, 180, 270, 157)
                s.text(headline, 61, 397, bold=True)
                s.text(subtitle, 31, 487)
                s.text('Kostenlose Basis.', 33, 629, bold=True)
                s.text('Pro einmalig 3,99 € · kein Abo', 29, 708)
                s.text('Deutscher Basispreis', 18, 760, color='0x526256')
                s.text('Bald bei Google Play', 29, 929, bold=True)
                s.text('dudee-studio.com', 33, 1013, bold=True)
            elif source == '@end':
                s.image(ART / 'mark.png', 160, 160, 280, 145)
                s.text('DUDEE STUDIO', 20, 53, bold=True)
                s.text(headline, 60, 350, bold=True)
                s.text(subtitle, 32, 438)
                s.text('Kostenlose Basis.', 29, 529, bold=True)
                s.text('Mehr mit Pro', 23, 609, bold=True)
                for name, x, label, fontsize in [('scanner', 119, 'Barcode', 20), ('family', 312, 'Familie erstellen', 18), ('analysis', 505, 'Mehr Auswertungen', 17)]:
                    s.image(icons[name], 96, 96, x, 672)
                    s.text(label, fontsize, 790, x=f'{x+48}-text_w/2')
                s.text('Einmalig 3,99 € · kein Abo', 30, 873, bold=True)
                s.text('Deutscher Basispreis', 18, 925, color='0x526256')
                s.text('Bald bei Google Play', 27, 1022)
                s.text('dudee-studio.com', 30, 1082, bold=True)
                s.text('Familie: Erstellen mit Pro · kostenlos beitreten', 18, 1198)
            else:
                if source == '@scan':
                    s.image(icons['product'], 240, 360, 79, 365)
                    s.image(icons['scanner'], 160, 160, 432, 466)
                    s.text('→', 70, 492, x='337', color='0xF7B62B')
                    s.image(icons['scan-line'], 180, 4, 108, "'620+30*sin(t*3)'", enable='lt(t,2)')
                    s.box(399, 738, 257, 69, '0xD9EFE3', enable='gte(t,1.8)')
                    s.text('✓ Artikel erkannt', 24, 758, bold=True, x='422', extra=":enable='gte(t,1.8)'")
                    s.text('Produkt → Barcode → Artikel', 27, 955, bold=True)
                    s.text('Schematische Scan-Demo', 20, 1014, color='0x526256')
                elif source == '@family':
                    s.image(icons['shared-list'], 680, 775, 20, 248)
                    s.text('→', 70, 595, x='325', color='0xF7B62B', extra=":enable='between(t,0.7,2.8)'")
                    s.box(430, 604, 213, 70, '0xD9EFE3', enable='gte(t,2.2)')
                    s.text('+ Haferdrink', 24, 626, bold=True, x='449', extra=":enable='gte(t,2.2)'")
                    s.text('✓ Gemeinsam auf dem gleichen Stand', 25, 1040, bold=True, extra=":enable='gte(t,2.7)'")
                    s.text('Sync-Prinzip · schematische Demo', 20, 1095, color='0x526256')
                else:
                    path = APP / 'app/build' / source
                    if not path.exists():
                        raise FileNotFoundError(path)
                    s.box(84, 210, 552, 972, '0xD2DED0')
                    zoom = ",zoompan=z='min(zoom+0.00012,1.008)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=540x960:fps=24" if source in ['promo/catalog-after.png', 'promo/analysis-pro.png'] else ''
                    s.image(path, 540, 960, 90, 216, effects=zoom)
                    if source == 'promo/catalog-before.png':
                        s.text('◯', 90, 709, x='530', color='0xF7B62B', extra=f":enable='between(t,{duration-0.65},{duration})'")
                    if source == 'promo/barcode-before.png':
                        s.text('◯', 90, 980, x='420', color='0xF7B62B', extra=f":enable='between(t,{duration-0.65},{duration})'")
                s.text('ABGEHAKT · DUDEE STUDIO', 18, 28, bold=True)
                s.text(headline, 32 if len(headline) > 32 else 35, 76, bold=True)
                s.text(subtitle, 23, 129)
                s.chapter(chapter)
                s.text(badge or 'LISTE · ARTIKEL · GERICHTE · MEHR', 18, 1195, bold=True)
                s.text('Demo-Daten · Scan und Sync simuliert', 16, 1236, color='0x526256')
            clip = folder / f'{i:02d}.mp4'
            padding = TRANSITION / 2 if i in [0, len(scenes) - 1] else TRANSITION
            s.finish(clip, duration + padding)
            clips.append(clip)
        # Half a transition hold at the ends and one in the middle preserve
        # the nominal 20/60 second duration while overlapping every cut.
        audio = folder / 'soundtrack.wav'
        narrated = (ROOT / 'assets/audio/abgehakt-instrumental.mp3').exists() and (ROOT / 'assets/audio/de/overview/00.mp3').exists()
        audio_metadata = build_voice_mix(audio, scenes, teaser) if narrated else soundtrack(audio, scenes, TRANSITION)
        args = ['ffmpeg', '-v', 'error', '-y']
        for clip in clips:
            args += ['-threads', '1', '-i', str(clip)]
        args += ['-i', str(audio)]
        graph = [f'[{j}:v]setpts=PTS-STARTPTS,fps=24,format=yuv420p[v{j}]' for j in range(len(clips))]
        current = 'v0'
        length = scenes[0][1] + TRANSITION / 2
        transitions = []
        for j in range(1, len(clips)):
            mode = 'smoothleft' if j in ([1, 2] if teaser else [1, 5, 13]) else 'fade'
            offset = length - TRANSITION
            label = f'xf{j}'
            graph.append(f'[{current}][v{j}]xfade=transition={mode}:duration={TRANSITION}:offset={offset},fps=24[{label}]')
            transitions.append({'start': offset, 'duration': TRANSITION, 'style': mode})
            current = label
            length += scenes[j][1] + (TRANSITION / 2 if j == len(clips) - 1 else TRANSITION) - TRANSITION
        duration = sum(scene[1] for scene in scenes)
        graph.append(f'[{current}]fade=t=out:st={duration-.35}:d=0.35,format=yuv420p[video]')
        target, peak = (-16, -2) if narrated else (-18, -1.5)
        graph.append(f'[{len(clips)}:a]loudnorm=I={target}:TP={peak}:LRA=7,aresample=48000[audio]')
        rendered = folder / 'final.mp4'
        run(*args, '-filter_complex_threads', '1', '-filter_complex', ';'.join(graph),
            '-map', '[video]', '-map', '[audio]', '-t', str(duration),
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-threads', '2',
            '-c:a', 'aac', '-b:a', '128k', '-ar', '48000', '-ac', '2', '-movflags', '+faststart', str(rendered))
        shutil.copyfile(rendered, output)
        audio_metadata['transitions'] = transitions
        write_sound_outputs(audio_metadata, teaser)
        run('ffmpeg', '-v', 'error', '-y', '-ss', '1.5', '-i', str(output), '-frames:v', '1', '-q:v', '3', str(poster))
    (ROOT / ('videos/teaser-storyboard.json' if teaser else 'videos/storyboard.json')).write_text(json.dumps(scenes, ensure_ascii=False, indent=2) + '\n')
    print(output)


if __name__ == '__main__':
    main()
