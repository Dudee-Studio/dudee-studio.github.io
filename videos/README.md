# Abgehakt – Store-Videos

Die Videos erklären zuerst die kostenlose App und anschließend die optionalen
Pro-Funktionen. Keine Anzeigenkampagne, keine externen Werbe-CTAs.

- `einkaufsliste-gerichte.mp4`: 90 Sekunden. 0–48 s: Artikel, Gerichte,
  Einkaufsliste, selbst eingetragene Angebote, Coupons, letzter tatsächlich
  gekaufter Angebotspreis mit Datum und Basis-Ausgabenübersicht. 48–53 s:
  Übergang zu Pro. 53–82 s: gemeinsame Einkaufsliste, Barcode-Scanner für neue
  und bestehende Artikel sowie erweiterte Auswertung. 82–90 s: Einmalkauf.
- `abgehakt-kurz.mp4`: 30 Sekunden. Kostenloser Grundnutzen zuerst,
  anschließend gemeinsame Liste und Scanner mit Pro; Einmalkauf zum Schluss.
- Beide: 720 × 1280, H.264, 24 Bilder/s, AAC Stereo 48 kHz, 0,5 Sekunden
  lange Überblendungen, keine Schwarzpausen zwischen Szenen.
- `storyboard.json` / `teaser-storyboard.json`: tatsächliche Szenenfolge.
- `overview-sound.json` / `teaser-sound.json`: Sprechzeiten, Tempo und Tonregie.
- `overview-de.vtt` / `teaser-de.vtt`: zuschaltbare deutsche Untertitel.

## Aussagen zu Pro

Deutscher Basispreis: **einmalig 3,99 €, kein Abo**. Preis kann je nach Land
abweichen. Pro benötigt, wer die Gruppe erstellt/einlädt; Eingeladene können
kostenlos beitreten und gemeinsam einkaufen. Eigener Scanner und erweiterte
Auswertung benötigen jeweils eigenes Pro. Die Gruppe ist für Paare, WGs,
Freunde, Familien und andere gemeinsame Einkäufe gedacht.

Kein Versprechen eines lebenslangen Serverbetriebs. „Einmal kaufen“ beschreibt
das Kaufmodell. Keine automatische Händler-Angebotssuche oder Preisgarantie.
Produktdaten beim Scan werden nur geladen, wenn verfügbar.

## Bild und Ton

Echte Android-Compose-Ansichten mit Demo-Daten, automatisiert gerendert mit
Robolectric. Kein durchgehendes Video eines physischen Telefons. Scan und
Gruppen-Sync sind ausdrücklich als schematische/simulierte Demos markiert;
kein vorgetäuschter Kamera-Scan oder aufgezeichneter Zwei-Geräte-Abgleich.
Alle Ausgaben sind Beispieldaten.

Das ausgewählte Logo C ist die korrigierte Fassung ohne schwarze Flecken.
Grafiken: `assets/abgehakt/`. Poster: `assets/einkaufsliste/*poster.jpg`.

Deutsche junge weibliche Bibliotheksstimme von ElevenLabs, jetzt Modell
`eleven_v3` mit ausdrucksvollerer Regie: neugierige Fragen, freundlich lebendige
Erklärung und positiv betonter Pro-Übergang. Keine Stimmklonierung. Performance-
Tags sind von sichtbarem Text und Untertiteln getrennt. Generierte Musik:
`assets/audio/abgehakt-instrumental.mp3`. Der Mittelteil wird für 90 Sekunden
weich verlängert, der musikalische Schluss bleibt erhalten. Musik wird unter
Sprache abgesenkt, Bediengeräusche bleiben dezent. Master-Ziel -16 LUFS / -2 dBTP.
Weitere Quellen und Generierung: `assets/audio/README.md`.

## Wiederherstellen

Python 3 mit NumPy, FFmpeg mit libx264/drawtext und DejaVu-Schriften sowie ein
Checkout von `CaptAwesome89/Einkaufsliste` mit erzeugten Testansichten erforderlich.

1. `tools/capture/PromoVideoCapture.kt` vorübergehend nach
   `app/src/test/java/io/github/captawesome89/einkaufsliste/ui/` im App-Repo kopieren.
2. Dort mit geeigneter Android-Testumgebung:
   `SCREENSHOTS=true ./gradlew testDebugUnitTest --tests '*StoreScreenshots*' --tests '*ShoppingPreparationUiTest*' --tests '*PromoVideoCapture*'`.
   Quellen liegen unter `app/build/screenshots`, `app/build/ui-previews` und `app/build/promo`.
3. Hier `python tools/render-app-video.py /pfad/zur/Einkaufsliste` und für die
   Kurzfassung zusätzlich `--teaser` ausführen. Die Renderer rufen keine API auf.
4. Temporäre Capture-Datei im App-Checkout entfernen.

Nur den Ton neu mischen: zusätzlich `--audio-only`. Neue Sprache explizit mit
`tools/generate_elevenlabs.py speech` erzeugen; Zugangsdaten ausschließlich aus
sicherer Prozessumgebung oder geschützter Datei außerhalb des Repositories.

Website: kein Autoplay, keine Download-Angebote; Start des zweiten Videos
pausiert das erste. Die Website nennt bis zur Store-Veröffentlichung „Bald bei
Google Play“. Die Videos selbst verzichten auf diese zeitabhängige Einblendung.
Ein Upload in Google Play/YouTube ist mit dieser Website-Veröffentlichung nicht erfolgt.
