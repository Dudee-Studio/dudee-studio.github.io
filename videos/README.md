# Aktuelles Hauptvideo: Abgehakt V10

`einkaufsliste-gerichte.mp4` zeigt die freigegebene 55-Sekunden-Fassung in 1920×1080 bei 30 fps mit deutschem Ton. Die Website nutzt den Export ohne eingebrannte Untertitel und die zuschaltbaren deutschen Untertitel aus `overview-de.vtt`. Auf Start- und Projektseite ist das dazugehörige Vorschaubild eingebunden. Kein Autoplay oder Download-Angebot.

Ablauf:0,5sLogo; Gerichte und Zutatenübernahme vor dem Ergänzen der Milch; Einkauf über70,10€ mit57,12€imWagen und12,98€offen bei23s; kostenloser Rückblick; Handybild42–43s; Markenslogan und Pause; kurzer Nachsatz zur Pro-Version48–55s. Die drei Vorteile erscheinen nacheinander: geteilte Liste, Barcode-Scanner und Ausgaben nach Kategorien. Echte Appansichten bleiben vollständig; feste Bilder ohne Kamerawackeln. KI-Fotografien und App mit Demo-Daten, keine tatsächliche Scan- oder Zwei-Geräte-Sync-Vorführung.

Technischer Produktionsnachweis mit SHA-256: `overview-production.json`. Beide Originalexporte wurden vollständig decodiert und das konkrete Schlussstück erneut aus Gestaltungs- und Produktsicht geprüft. Stimme, Betonung und musikalische Wirkung wurden nicht subjektiv gehört. Neue Aufnahme mit der bereits gewählten Livia-Stimme; vorhandene Musik und gültige Sprachpassagen wiederverwendet. Die vollständige lokale Produktionsmappe liegt unter `/workspace/artifacts/abgehakt-video-v10`; die älteren Renderer unten reproduzieren historische Fassungen.

Wiedergabeprüfung: `python tools/serve-preview.py --port 8765`, danach `python tools/check-project-page.py http://127.0.0.1:8765`. Mobile/Desktop, hell/dunkel, Untertitel und exklusiver Ton werden an der tatsächlich geladenen Datei geprüft.

---

# Archiv früherer Produktionen

## Aktuelle Fotofilme: kostenlose App und Pro getrennt

Die aktuelle Hauptfassung zeigt die kostenlose App in 33 Sekunden. Der zweite Film zeigt Pro in 26 Sekunden. Beide sind Fotosequenzen in 1280 × 720 bei 24 fps: vier verschiedene Handlungsschritte je Szene, kurze Stop-Motion-Wechsel, leichte Kamerabewegung und echte App-Einblendungen. Sie ersetzen die frühere 42-Sekunden-Montage und den 30-Sekunden-Teaser unter denselben öffentlichen Dateinamen.

Die fiktive Familie bleibt visuell konsistent: Frau und Kind auf dem Sofa; Frau allein im Supermarkt; Frau und Mann beim Auspacken und bei der Ausgabenübersicht am Esstisch. Der Pro-Film zeigt zusätzlich den Mann allein zu Hause beim Ergänzen der Liste sowie die Frau beim Barcode-Scan. Es sind keine weiteren Personen dargestellt. Die kostenlosen Ausgaben zeigen ausschließlich den tatsächlich kostenlosen Bereich der App; der Pro-Hinweis im ursprünglichen Screenshot ist außerhalb des gewählten Ausschnitts.

Bildquellen: `assets/einkaufsliste/photo-story/` (OpenAI-Bildgenerierung; je ein 2×2-Bogen mit vier unterschiedlichen Phasen). Keine ElevenLabs-Video-API, da das Creator-Konto dort nicht berechtigt war. Neue deutsche Sprecheraufnahmen mit derselben ElevenLabs-Stimme und `eleven_v3`; vorhandene beauftragte Musik, automatische Absenkung unter der Stimme und dezente App-Klänge. Kein neuer Musikauftrag, keine Preisfolie. Die Untertitel sind kurze, automatisch transkribierte und mit dem Skript verglichene Sprechabschnitte. Sprachtempo beim Schnitt unverändert. Die Stimmemotion wurde nicht durch menschliches Anhören geprüft.

App-Ansichten stammen aus dem realen Compose-Capture. Scan und Gruppen-Synchronisation sind vorbereitete Demonstrationen, keine Aufnahme eines echten Scans oder einer aktiven Zwei-Geräte-Synchronisation. Die Prognose wird im tatsächlichen Einkaufsvorschlag gezeigt; eine nicht belegte `~Anzahl`-Oberfläche wird nicht nachgebaut.

Reproduktion (benötigt FFmpeg, Pillow, NumPy und die bestehenden App-Captures):

```sh
python tools/render-photo-story.py videos/photo-story-production.json
```

Die Quellen liegen im Repository. Der Renderer benötigt keinen API-Schlüssel und löst keine kostenpflichtige Generierung aus. Ergebnis: `build/photo-story/`. Die Projektseite verwendet native Videosteuerung ohne Autoplay oder Download-Link. Beide Filme sind auch mit eingeblendeten Untertiteln verständlich.

---

# Abgehakt – kurze Store-Fassung

`einkaufsliste-gerichte.mp4` ist die neue 42-Sekunden-Hauptfassung. Sie ersetzt
die frühere 90-Sekunden-Vorstellung. 720 × 1280, 24 Bilder/s, H.264, AAC Stereo
48 kHz. Keine lange Logoeröffnung; die App-Handlung beginnt sofort.

## Freigegebener Ablauf

- 0–9 s: Artikel, echte Einkaufsvorschau und eine fertig angelegte regelmäßige
  Regel („2× Milch · jede Woche“). Letzter Angebotskauf steht bereits beim Artikel.
- 9–16 s: Gericht und Zutaten übernehmen, dieselbe Liste weiterverwenden.
- 16–24 s: Vier aufeinanderfolgende Abhak-Ergebnisse. Angebote und Coupons werden
  beiläufig erwähnt; kein zusätzlicher Formularrundgang.
- 24–30 s: Pro-Gruppenliste mit einer Ergänzung; für Freunde, WG und Familie.
  Einladen mit Pro, andere treten kostenlos bei.
- 30–34 s: schematischer Barcode-Scan, danach tatsächlich erzeugter Demo-Listeneintrag.
- 34–37 s: Einkauf abgeschlossen, danach eine erweiterte Pro-Auswertung.
- 37–42 s: kostenlose Basis, Pro einmalig 3,99 € (deutscher Basispreis), kein Abo.

Pro-Scanner und persönliche erweiterte Analyse benötigen eigenes Pro.
Kostenlose Basis, Prognose und regelmäßiger Bedarf sind früh als kostenlos
gekennzeichnet. Keine lebenslange Server-Verfügbarkeit versprochen.
Produktdaten beim Scan nur, wenn verfügbar. Kein automatischer Händlervergleich.

## Aufnahmegrundlage und Grenzen

Die Ansichten stammen aus der echten Compose-Oberfläche mit bedienten und
gezielt vorbereiteten Demo-Zuständen im App-Test.
Es handelt sich um eine geschnittene Folge tatsächlicher UI-Zustände mit kurzen
Überblendungen/Vergrößerungen, nicht um eine durchgehende Kameraaufnahme eines
physischen Telefons. Alle Artikel, Einkäufe und Ausgaben sind Demo-Daten.

Die beschriebene Prognoseanzeige „~Anzahl“ lässt sich im zugänglichen App-Stand
nicht nachweisen. Statt eine Oberfläche nachzubauen, zeigt die Produktion die
funktionierende separate Einkaufsvorschau. Die abweichende installierte Fassung
ist noch nicht identifiziert. Keine App-Funktion wurde für den Film verändert.

Die Gruppen-Ergänzung ist eine markierte Sync-Demo mit lokalen Test-Doubles,
kein aufgezeichneter Zwei-Geräte-Abgleich. Der Barcode-Vorgang ist eine ausdrücklich
schematische Animation; Produktauflösung und anschließender Listeneintrag werden
über den FakeScanner/FakeLookup der App getestet. Die Haferdrink-Grafik ist eine
neutrale Illustration, kein Foto eines realen Herstellerprodukts.

Keine versetzten Hervorhebungskreise: der Bildausschnitt, native Auswahl und
sichtbare Bedienergebnisse leiten den Blick. Eigenständige Texttafeln nur im
Preisabschluss. Der letzte Angebotspreis ist ein tatsächlich erfasster Demo-Kauf.

## Ton und Quellen

- Neue 42-Sekunden-ElevenLabs-Musik: `assets/audio/store42-instrumental.mp3`.
- Briefing: `assets/audio/store42-music-brief.json`; angefordert 120 BPM, sofortiger
  Groove, Lift bei 24 s, Platz für den Preis ab 37 s, Ende bei 42 s. BPM und
  musikalische Einsätze sind Promptziele, keine separat gemessene Partitur.
- Neue junge weibliche deutsche Bibliotheksstimme, Modell `eleven_v3`,
  `assets/audio/de/store42-script.json` und `store42/*.mp3`.
- Sprechregie pro Passage, natürliche Pausen bei Aktionsergebnissen.
- Originale Bediengeräusche der App aus `app/src/main/res/raw/snd_*.ogg`.
- Musik wird unter Sprache um ungefähr 8 dB abgesenkt und in Pausen zurückgeholt.
  Ziel für den Master -16 LUFS / -2 dBTP. Codierte Ausgabe erneut messen.
- `overview-sound.json`: tatsächliche Sprech- und Effektzeiten.
- `overview-de.vtt`: native deutsche Untertitel. Für einen Store-/YouTube-Upload
  müssen die Untertitel separat übernommen werden; Website-Tracks erledigen das nicht.

Technische Messungen und automatische Transkription ersetzen keine subjektive
Hörprüfung von Timbre, Wärme und musikalischem Geschmack.

## Wiederherstellen

Python mit NumPy und Pillow, FFmpeg mit libx264/drawtext und DejaVu-Sans sowie
der App-Checkout mit Android-Testumgebung werden benötigt.

1. `tools/capture/PromoVideoCapture.kt` vorübergehend nach
   `app/src/test/java/io/github/captawesome89/einkaufsliste/ui/` im App-Repo kopieren.
2. Im App-Repo:
   `SCREENSHOTS=true ./gradlew testDebugUnitTest --tests '*PromoVideoCapture.captureStore42'`.
   Ansichten entstehen unter `app/build/store42`.
3. In diesem Repo:
   `python tools/render-store-video.py /pfad/zur/Einkaufsliste`.
4. Temporäre Capture-Klasse im App-Repo entfernen.

Der Renderer ruft keine API auf. Neue Generierung erfolgt ausdrücklich mit
`tools/generate_elevenlabs.py speech --kind store42` bzw.
`... music --music-brief assets/audio/store42-music-brief.json`.
Zugangsdaten ausschließlich aus Prozessumgebung oder geschützter externer Datei.

`abgehakt-kurz.mp4` bleibt die bereits veröffentlichte alternative 30-Sekunden-
Ansicht. Alte Generatoren/Skripte sind deren historische Produktionsquellen;
für die neue Hauptfassung ist `render-store-video.py` maßgeblich.
Kein Autoplay und keine Download-Angebote auf der Website. Noch kein Upload in
Google Play/YouTube erfolgt. Store-Verfügbarkeit bleibt separat ausgewiesen.

## Separates Feature-Video: Artikelkatalog, Version 1.1

Der vom Nutzer freigegebene Schnitt ist als eigener 22-Sekunden-Film unter den aktuellen Projekten eingebunden.
Die zwei bisherigen Hauptfilme bleiben ohne Versionsnummer. Bis Backend-Freischaltung und echte Geräteprüfung
abgeschlossen sind, steht im neuen Film „Vorschau · Version 1.1“. Die aktuelle Oberfläche und vorbereitete
Serverantworten werden ausdrücklich als Demo gezeigt; es wird kein Live-Serverabgleich behauptet.

- Website: `artikelkatalog-1.1.mp4` mit optionalen nativen Untertiteln `artikelkatalog-1.1-de.vtt`.
- Store-Fassung: `artikelkatalog-1.1-store.mp4` mit eingebrannten deutschen Untertiteln.
- Schnitt und Quellen: `artikelkatalog-1.1-shots.json`; freigegebener Plan: `artikelkatalog-v1.1-plan.md`.
- Produktionsnachweis und Messwerte: `artikelkatalog-1.1-production.json`.

Der Film beginnt mit Mutter und Kind zu Hause, zeigt die tatsächlichen App-Schritte für Suche, Übernahme,
persönliche Kategorie und freiwillige Freigabe und endet mit gemeinsamem Puzzeln. App-Ausschnitte werden
fest vergrößert gezeigt; keine künstlichen Kameraschwenks oder wackelnden Zooms. Keine Preiskarte.

### Reproduktion ohne weitere API-Aufrufe

`python tools/render-catalog-feature.py` verwendet die eingecheckten App-Aufnahmen, Bildsequenzen und Audiodateien.
Benötigt FFmpeg, NumPy und die vorhandenen Audiowerkzeuge unter `tools/`. Die Zwischendateien unter
`build/catalog-v1.1/` bleiben lokal. Das Instrumental stammt aus der bestehenden ElevenLabs-Produktion
`assets/audio/store42-instrumental.mp3`. Nur die fünf deutschen Sprachpassagen wurden neu erzeugt.
Die Wortzeiten der Untertitel stammen aus der Transkription genau dieser Aufnahme.

Neue App-Aufnahmen: `tools/capture/CatalogFeatureCapture.kt` vorübergehend nach
`../Einkaufsliste/app/src/test/java/io/github/captawesome89/einkaufsliste/catalog/` kopieren,
`testDebugUnitTest --tests '*CatalogFeatureCapture.captureFeature'` mit der vorhandenen Android-Umgebung ausführen,
PNG-Dateien aus `app/build/catalog-feature-captures/` übernehmen und die temporäre Testdatei wieder entfernen.
Die Aufnahme nutzt die echte Compose-Oberfläche von App-Commit `83cfe1e`; nur Katalogantworten und Fotos sind
vorbereitete Demo-Daten. Das Veröffentlichungsfoto gehört zu einem eigenen Artikel, nicht zu einer fremden Kopie.

Lokale Medienprüfung: `python tools/serve-preview.py --port 8765`, dann
`python tools/check-project-page.py http://127.0.0.1:8765`. Der Vorschau-Server unterstützt HTTP-Byte-Ranges
für echte Sprung-/Wiedergabetests. Geprüft wurden drei Videos, Untertitel, exklusiver Ton und Darstellung bei
390 und 1440 Pixeln in hell und dunkel. Kein Autoplay und kein Download-Angebot.

Bildkontrolle, Wortlaut, Timing und Pegel sind geprüft. Eine tatsächliche Hörprüfung von emotionaler Wirkung,
Stimmfarbe, Groove und Verständlichkeit auf Lautsprechern/Kopfhörern wurde nicht durchgeführt.
