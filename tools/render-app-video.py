#!/usr/bin/env python3
"""Render Abgehakt's captioned app overview with reusable motion graphics.
Usage: python tools/render-app-video.py /path/to/Einkaufsliste
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = Path(sys.argv[1])
ART = ROOT / 'assets/abgehakt'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SCENES = [
    ('@intro', 3, 'Abgehakt', 'Dein Einkauf im Griff.', ''),
    ('promo/catalog-before.png', 3, 'Einfach vorbereiten.', 'Artikel von oben nach unten durchgehen.', ''),
    ('promo/catalog-after.png', 3, 'Mit einem Tipp ergänzt.', 'Was du brauchst, kommt auf die Liste.', ''),
    ('promo/dishes.png', 3, 'Was kochen wir?', 'Deine Gerichte helfen beim Planen.', ''),
    ('promo/dish-ingredients.png', 3, 'Zutaten übernehmen.', 'Mengen anpassen. Auf die Liste setzen.', ''),
    ('promo/barcode-before.png', 3, 'Ohne Foto angelegt?', 'Dem Artikel einen Barcode zuordnen.', 'BARCODE · MIT PRO'),
    ('@scan', 3, 'Scannen statt eintippen.', 'Produktdaten und Fotos, sofern verfügbar.', 'BARCODE · MIT PRO · SCAN-DEMO'),
    ('promo/barcode-after.png', 3, 'Für den nächsten Scan.', 'Der Barcode ist am Artikel gespeichert.', 'BARCODE · MIT PRO'),
    ('promo/list-before.png', 4, 'Im Laden abhaken.', 'Deine Liste begleitet den Einkauf.', ''),
    ('promo/spontaneous.png', 5, 'Spontan noch etwas?', 'Per Barcode direkt zur Liste hinzufügen.', 'BARCODE · MIT PRO · DEMO-SCAN'),
    ('@family', 6, 'Gemeinsam einkaufen.', 'Ein Artikel. Auf beiden Listen.', 'GRUPPE MIT PRO · BEITRETEN KOSTENLOS'),
    ('ui-previews/angebote.png', 3, 'Angebote eintragen.', 'Preis und Zeitraum festhalten.', ''),
    ('ui-previews/coupons.png', 3, 'Coupons berücksichtigen.', 'Beim Bezahlen den Rabatt eintragen.', ''),
    ('ui-previews/letzter-angebotskauf-katalog.png', 4, 'Zuletzt im Angebot?', 'Gekauften Angebotspreis und Datum sehen.', ''),
    ('promo/analysis-pro.png', 5, 'Ausgaben verstehen.', 'Monatsverlauf und Abteilungen vergleichen.', 'ERWEITERTE ANALYSE · MIT PRO'),
    ('@end', 6, 'Abgehakt', 'Dein Einkauf im Griff.', ''),
]


def run(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


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
        self.chain(f'fade=t=in:st=0:d=0.12,fade=t=out:st={duration-0.12}:d=0.12,format=yuv420p')
        run(*self.args, '-filter_complex_threads', '1', '-filter_complex', ';'.join(self.filters), '-map', f'[{self.base}]', '-t', str(duration), '-c:v', 'libx264', '-preset', 'fast', '-crf', '24', '-threads', '2', '-an', str(path))


def main():
    output = ROOT / 'videos/einkaufsliste-gerichte.mp4'
    poster = ROOT / 'assets/einkaufsliste/poster.jpg'
    with tempfile.TemporaryDirectory(prefix='abgehakt-motion-') as folder:
        folder = Path(folder)
        icons = {}
        for name in ['scanner', 'family', 'analysis', 'product', 'shared-list', 'scan-line']:
            icons[name] = folder / (name + '.png')
            run('ffmpeg', '-v', 'error', '-y', '-i', str(ART / (name + '.svg')), '-frames:v', '1', str(icons[name]))
        clips = []
        for i, (source, duration, headline, subtitle, badge) in enumerate(SCENES):
            shotdir = folder / str(i)
            shotdir.mkdir()
            s = Shot(shotdir)
            chapter = 0 if i < 8 else (1 if i < 13 else 2)
            if source == '@intro':
                s.image(ART / 'mark.png', 252, 252, 234, 228, effects=',fade=t=in:st=0:d=0.5:alpha=1')
                s.text('DUDEE STUDIO', 20, 83, bold=True)
                s.text(headline, 68, 536, bold=True)
                s.text(subtitle, 32, 636)
                s.text('✓', 78, '780-16*min(t,1)', color='0x246B3D', extra=":alpha='clip((t-0.35)*3,0,1)'")
                s.text('Vorbereiten → Einkaufen → Überblick', 24, 959)
                s.text('Kostenlose Basis · optional Pro', 21, 1040, color='0x526256')
            elif source == '@end':
                s.image(ART / 'mark.png', 160, 160, 280, 145)
                s.text('DUDEE STUDIO', 20, 53, bold=True)
                s.text(headline, 60, 350, bold=True)
                s.text(subtitle, 32, 438)
                s.text('Kostenlose Basis.', 29, 529, bold=True)
                s.text('Mehr mit Pro', 23, 609, bold=True)
                for name, x, label, fontsize in [('scanner', 119, 'Barcode', 20), ('family', 312, 'Familie erstellen', 18), ('analysis', 505, 'Analyse', 20)]:
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
                s.text(headline, 35, 76, bold=True)
                s.text(subtitle, 23, 129)
                s.chapter(chapter)
                s.text(badge or 'LISTE · ARTIKEL · GERICHTE · MEHR', 18, 1195, bold=True)
                s.text('Demo-Daten · Scan und Sync simuliert', 16, 1236, color='0x526256')
            clip = folder / f'{i:02d}.mp4'
            s.finish(clip, duration)
            clips.append(clip)
        manifest = folder / 'concat.txt'
        manifest.write_text(''.join(f"file '{p}'\n" for p in clips))
        run('ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(manifest), '-c', 'copy', '-movflags', '+faststart', str(output))
        run('ffmpeg', '-v', 'error', '-y', '-ss', '1.5', '-i', str(output), '-frames:v', '1', '-q:v', '3', str(poster))
    (ROOT / 'videos/storyboard.json').write_text(json.dumps(SCENES, ensure_ascii=False, indent=2) + '\n')
    print(output)


if __name__ == '__main__':
    main()
