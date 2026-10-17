# ElevenLabs: deutsche Sprache und Musik

Diese Audioquellen wurden mit dem vom Nutzer bereitgestellten ElevenLabs-Konto
für Abgehakt generiert. Es wird kein API-Schlüssel im Repository gespeichert.

- Sprecherin: „Emily E. - First-Person Games & Audiobooks“, verfügbare
  professionelle Bibliotheksstimme, als weiblich/jung/deutsch ausgewiesen.
- Sprachmodell: `eleven_v3`. Keine neue Stimmklonierung. Ausdrucksregie über getrennte Performance-Texte mit Audio-Tags; Untertitel enthalten nur den gesprochenen Text.
- `de/overview-script.json` / `de/teaser-script.json`: Texte und Schnittfenster.
- Die MP3-Dateien in `de/overview/` und `de/teaser/` sind die erzeugten Sprachclips.
- `abgehakt-instrumental.mp3`: neu generierte instrumentale Musik (60 Sekunden),
  mit angefordertem 112-BPM-Groove, Bass, organischen Akzenten und Variationen.
- `music-source.json`: tatsächlich verwendeter Musikprompt und Modell.
- `.fingerprint`: Hash der Generierungsparameter, ohne Zugangsdaten; verhindert
  unnötige kostenpflichtige Wiederholungen bei unveränderten Clips.

Erzeugen: `ELEVENLABS_API_KEY` sicher in der Prozessumgebung bereitstellen und
`python tools/generate_elevenlabs.py speech` bzw. `... music` ausführen.
Alternativ `--key-file` mit einer geschützten Datei außerhalb des Repositorys.
Der Generator protokolliert keine Schlüssel. Generierung verbraucht Kontingent.

Mischung: `tools/voice_mix.py` entfernt nur Randstille, erhält Sprechpausen,
platziert Sprache nach Zeitmarken und senkt die Musik unter der Sprecherin ab.
Zu lange Passagen werden neu formuliert; die verbleibende Tempoanpassung ist
auf maximal 10 Prozent begrenzt. Die Kurzfassung verbindet den Anfang der Musik
mit ihrem echten Schluss. Die 90-Sekunden-Fassung verlängert den Mittelteil mit
weichen Überblendungen und behält ebenfalls den musikalischen Abschluss. Die selbst erzeugten Bediengeräusche bleiben dezent.

Beide fertigen Videos: deutsche Sprecherin, ElevenLabs-Musik, AAC Stereo 48 kHz;
Master-Ziel -16 LUFS und -2 dBTP. `videos/*-sound.json` dokumentiert die tatsächlichen
Sprechzeiten. `videos/*-de.vtt` stellt zuschaltbare deutsche Untertitel bereit.
