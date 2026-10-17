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
