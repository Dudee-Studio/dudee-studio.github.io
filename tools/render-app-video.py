#!/usr/bin/env python3
"""Render the captioned, silent app overview using real UI captures.

Usage: python tools/render-app-video.py /workspace/Einkaufsliste
The Android PromoVideoCapture test supplies barcode and Pro analysis views.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = Path(sys.argv[1])
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SCENES = [
    ('screenshots/1-liste.png', 4, 'Dein Einkauf im Griff.', 'Deine Einkaufsliste. Deine Gerichte.', ''),
    ('promo/catalog-before.png', 3, 'Einfach vorbereiten.', 'Artikel von oben nach unten durchgehen.', ''),
    ('promo/catalog-after.png', 3, 'Mit einem Tipp ergänzt.', 'Was du brauchst, kommt auf die Liste.', ''),
    ('promo/dishes.png', 3, 'Was kochen wir?', 'Deine Gerichte helfen beim Planen.', ''),
    ('promo/dish-ingredients.png', 3, 'Zutaten übernehmen.', 'Mengen anpassen. Auf die Liste setzen.', ''),
    ('promo/barcode-before.png', 4, 'Ohne Foto angelegt?', 'Dem Artikel einen Barcode zuordnen.', 'BARCODE · MIT PRO'),
    ('promo/barcode-after.png', 3, 'Für den nächsten Scan.', 'Der Barcode ist am Artikel gespeichert.', 'BARCODE · MIT PRO'),
    ('promo/list-before.png', 4, 'Im Laden abhaken.', 'Deine Liste begleitet den Einkauf.', ''),
    ('promo/spontaneous.png', 5, 'Spontan noch etwas?', 'Per Barcode direkt zur Liste hinzufügen.', 'BARCODE · MIT PRO · DEMO-SCAN'),
    ('promo/family.png', 6, 'Gemeinsam einkaufen.', 'Eine Familie. Gemeinsame Einkaufslisten.', 'GRUPPE MIT PRO · BEITRETEN KOSTENLOS'),
    ('ui-previews/angebote.png', 3.5, 'Angebote eintragen.', 'Preis und Zeitraum festhalten.', ''),
    ('ui-previews/coupons.png', 3.5, 'Coupons berücksichtigen.', 'Beim Bezahlen den Rabatt eintragen.', ''),
    ('ui-previews/letzter-angebotskauf-katalog.png', 4, 'Zuletzt im Angebot?', 'Gekauften Angebotspreis und Datum sehen.', ''),
    ('promo/analysis-pro.png', 5, 'Ausgaben verstehen.', 'Monatsverlauf und Abteilungen vergleichen.', 'ERWEITERTE ANALYSE · MIT PRO'),
    (None, 6, 'Abgehakt', 'Dein Einkauf im Griff.', ''),
]


def run(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


def main():
    output = ROOT / 'videos/einkaufsliste-gerichte.mp4'
    output.parent.mkdir(parents=True, exist_ok=True)
    poster = ROOT / 'assets/einkaufsliste/poster.jpg'
    poster.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='app-video-') as tmp:
        tmp = Path(tmp)
        def text(label, size, y, bold=False, color='0x163B2B', x='(w-text_w)/2'):
            name = tmp / f'text-{len(list(tmp.glob("text-*")))}.txt'
            name.write_text(label, encoding='utf-8')
            return f"drawtext=fontfile={BOLD if bold else FONT}:textfile={name}:fontsize={size}:fontcolor={color}:x={x}:y={y}"

        clips = []
        for i, (source, duration, headline, subtitle, badge) in enumerate(SCENES):
            clip = tmp / f'{i:02d}.mp4'
            args = ['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=0xF6F8F0:s=720x1280:r=24']
            labels = [text('ABGEHAKT · DUDEE STUDIO', 18, 30, bold=True), text(headline, 36, 79, bold=True), text(subtitle, 23, 133)]
            if source:
                image = APP / 'app/build' / source
                if not image.exists():
                    raise FileNotFoundError(image)
                args += ['-loop', '1', '-i', str(image)]
                graph = '[1:v]scale=540:960:force_original_aspect_ratio=decrease,pad=540:960:(ow-iw)/2:(oh-ih)/2:color=0xF8FAF5[screen];[0:v]drawbox=x=84:y=204:w=552:h=972:color=0xD2DED0:t=fill[bg];[bg][screen]overlay=90:210,'
                labels += [text(badge or 'LISTE · ARTIKEL · GERICHTE · MEHR', 18, 1193, bold=True), text('Demo-Daten · Scan-Ergebnisse simuliert', 16, 1234, color='0x526256')]
            else:
                graph = '[0:v]'
                labels = [text('DUDEE STUDIO', 22, 110, bold=True), text(headline, 56, 320, bold=True), text(subtitle, 34, 414, bold=True), text('Deine Einkaufsliste. Deine Gerichte.', 27, 503), text('Kostenlose Basis.', 33, 671, bold=True), text('Pro einmalig 3,99 € · kein Abo', 29, 732), text('Deutscher Basispreis', 18, 781, color='0x526256'), text('Bald bei Google Play', 27, 952), text('dudee-studio.com', 32, 1026, bold=True)]
            if source == 'promo/catalog-before.png':
                labels.append(text('◯', 90, 703, color='0xF7B62B', x='530') + f":enable='between(t,{duration-0.65},{duration})'")
            if source == 'promo/barcode-before.png':
                labels.append(text('◯', 90, 974, color='0xF7B62B', x='420') + f":enable='between(t,{duration-0.65},{duration})'")
            graph += ','.join(labels) + f',fade=t=in:st=0:d=0.12,fade=t=out:st={duration-0.12}:d=0.12,format=yuv420p[out]' 
            run(*args, '-filter_complex_threads', '1', '-filter_complex', graph, '-map', '[out]', '-t', str(duration), '-c:v', 'libx264', '-preset', 'fast', '-crf', '25', '-threads', '2', '-an', str(clip))
            clips.append(clip)
        manifest = tmp / 'concat.txt'
        manifest.write_text(''.join(f"file '{p}'\n" for p in clips))
        run('ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(manifest), '-c', 'copy', '-movflags', '+faststart', str(output))
        run('ffmpeg', '-v', 'error', '-y', '-ss', '1', '-i', str(output), '-frames:v', '1', '-q:v', '3', str(poster))
    (ROOT / 'videos/storyboard.json').write_text(json.dumps(SCENES, ensure_ascii=False, indent=2) + '\n')
    print(output)


if __name__ == '__main__':
    main()
