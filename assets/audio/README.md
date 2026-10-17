# ElevenLabs-Audio für Abgehakt

## Aktuelle 42-Sekunden-Hauptfassung

- `de/store42-script.json`: kurze deutsche Sprechertexte, Zeitfenster und getrennte Performance-Tags.
- `de/store42/*.mp3`: erzeugte junge weibliche deutsche Bibliotheksstimme
  „Emily E. - First-Person Games & Audiobooks“, Modell `eleven_v3`. Keine neue Stimmklonierung.
- `de/store42-generation.json`: tatsächliche Quellen/Cache-Informationen.
- `store42-instrumental.mp3`: eigens erzeugte 42-Sekunden-Instrumentalspur.
- `store42-music-brief.json` / `store42-instrumental-source.json`: Briefing und tatsächlicher Musikprompt.
  Angefordert: 120 BPM, sofortiger Groove, Lift bei 24 s, Preisraum ab 37 s und sauberer Abschluss.
- `.fingerprint`: Hash der Generierungsparameter, ohne Zugangsdaten; vermeidet unnötige Wiederholungen.

`tools/store42_audio.py` mischt Sprache, Musik und Original-App-Geräusche aus
`app/src/main/res/raw/snd_*.ogg`. Ungefähr 8 dB Ducking unter Sprache, kontrollierte
Rückkehr in Pausen. Maximal 10 Prozent Tempoanpassung; Textkürzung hat Vorrang.
Master-Ziel -16 LUFS / -2 dBTP; die codierte Ausgabe wird erneut gemessen.

Generierung mit `python tools/generate_elevenlabs.py speech --kind store42` und
`... music --music-brief assets/audio/store42-music-brief.json`.
Zugangsdaten ausschließlich über `ELEVENLABS_API_KEY` oder `--key-file` mit einer
geschützten Datei außerhalb des Repositories. Keine Zugangsdaten gespeichert.
Generierung verbraucht Kontingent. Der Renderer ruft keine API auf.

Technische Pegelmessungen und Transkription ersetzen keine subjektive Hörprüfung
von Wärme, Timbre, Groove oder Geschmack. BPM und Einsätze im Prompt sind
Gestaltungsziele, keine unabhängig vermessene Partitur.

## Historische Quellen

`de/overview/` und `de/teaser/` sowie `abgehakt-instrumental.mp3` gehören zu den
älteren 90-/30-Sekunden-Fassungen. Der alternative 30-Sekunden-Film bleibt auf der
Website zusätzlich verfügbar. Für die neue Hauptfassung sind ausschließlich die
`store42`-Quellen und `tools/render-store-video.py` maßgeblich.
