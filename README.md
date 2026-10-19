# Dudee Studio

Statische Website: <https://dudee-studio.com/>. GitHub Pages veröffentlicht `main`.

## Deutsch und Englisch

DE / EN im Kopf jeder Seite wechselt auf die entsprechende Seite. Die Sprache bleibt
beim Navigieren erhalten; ein geöffneter Abschnitt bleibt beim Wechsel erhalten.
Keine zusätzlichen Cookies, Analyse-Dienste oder externen Übersetzungsdienste.

Die sechs englischen Seiten liegen unter `en/`. Nach Änderungen an den deutschen
Seiten und den Übersetzungen in `tools/build-language-pages.py` bzw.
`tools/i18n/privacy.en.html`: `python tools/build-language-pages.py`.
Die englische Datenschutzerklärung muss bei inhaltlichen Änderungen ebenfalls
aktualisiert werden; sie wird nicht automatisch maschinell übersetzt.

## Videos

Die Projektseite zeigt fünf sichtbare Vorschaubilder in der gewählten Sprache und einen gemeinsamen Player:
Hauptfilm Deutsch/Englisch, kostenlose Funktionen, Pro-Version, Analyse und
Community-Katalog. Alle fünf Filme gibt es auf Deutsch und Englisch; die Galerie zeigt ausschließlich die gewählte Sprache.
Der Katalogfilm ist eine Vorschau auf Version 1.1; die Live-Freigabe steht noch aus.

`videos/library.json` dokumentiert die veröffentlichten Querformatfilme mit
Prüfsummen, Quellen und Untertiteln. `tools/prepare-video-library.py` übernimmt die
freigegebenen Dateien aus dem Produktionsarbeitsbereich und baut Vorschaubilder.
Ältere Teaser bleiben als Produktionsarchiv erhalten und sind nicht mehr eingebunden.

**Hochformatfilme liegen ausschließlich im Branch
[`media/abgehakt-portrait-20261019`](https://github.com/Dudee-Studio/dudee-studio.github.io/tree/media/abgehakt-portrait-20261019/videos/portrait)**,
nicht in der von GitHub Pages veröffentlichten Website. Dort sind alle zehn
Filme mit randlosen Fotos, vollständigen Appansichten und Untertiteln abgelegt.

## Prüfen

`python tools/serve-preview.py --port 8766`

Danach: `python tools/check-project-page.py http://127.0.0.1:8766`.
Der Browsercheck prüft beide Sprachen, alle Seitenpaare, Handy/Desktop, Hell/Dunkel,
alle tatsächlichen Videowiedergaben, Untertitel, Tastaturwahl und den Betrieb
ohne JavaScript. Playwright und Chromium werden nur für den Check benötigt.

Die Datenschutzhinweise der Android-App stammen aus
`docs/play-store/datenschutz.md` im App-Repository. Mit
`python tools/sync-app-privacy.py --app-repo ../Einkaufsliste` aktualisieren;
die Hosting-Hinweise bleiben erhalten. Danach die englische Fassung nachführen
und die Sprachseiten neu bauen.

## Klickanleitungen

`hilfe.html` und `en/help.html` bieten dieselben 42 durchsuchbaren Anwendungsfälle
wie die Offline-Hilfe in der App. Die JSON-Quelle stammt aus
`app/src/main/assets/help-usecases.json` im App-Repository.
Mit `python tools/sync-app-help.py --app-repo ../Einkaufsliste` übernehmen und
anschließend `python tools/build-language-pages.py` ausführen.

`python tools/check-help-pages.py http://127.0.0.1:8766` prüft die
Sprachpaare, alle Schritte, Suche, Sprungmarken und den Betrieb ohne JavaScript.
