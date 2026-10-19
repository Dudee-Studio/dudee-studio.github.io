# Dudee Studio

Statische Website: <https://dudee-studio.com/>. GitHub Pages veröffentlicht `main`.

## Deutsch und Englisch

DE / EN im Kopf jeder Seite wechselt auf die entsprechende Seite. Die Sprache bleibt
beim Navigieren erhalten; ein geöffneter Abschnitt bleibt beim Wechsel erhalten.
Keine zusätzlichen Cookies, Analyse-Dienste oder externen Übersetzungsdienste.

Die englischen Seiten liegen unter `en/`. Nach Änderungen an den deutschen
Seiten und den Übersetzungen in `tools/build-language-pages.py` bzw.
`tools/i18n/privacy.en.html`: `python tools/build-language-pages.py`.
Die englische Datenschutzerklärung muss bei inhaltlichen Änderungen ebenfalls
aktualisiert werden; sie wird nicht automatisch maschinell übersetzt.

## Apps und Games

Die Hauptnavigation trennt `/apps.html` und `/games.html`. Unter Apps führt
Abgehakt auf seine Produktseite `/apps/abgehakt.html` mit Beschreibung, Videos und
Hilfe. Die englischen Gegenstücke liegen unter `/en/`. Die Hilfe zeigt die
Navigation Apps → Abgehakt → Hilfe; alte Links auf `projekte.html` und
`en/projects.html` bleiben mit ihren Sprungmarken erreichbar und verweisen per
Canonical auf die Produktseite. Games enthält den aktuellen Leerzustand, bis ein
Spiel vorgestellt wird.

Produkttexte und ihre Übersetzungen: `tools/product_pages.py`. Die gemeinsamen
Kopf- und Fußbereiche werden durch `tools/build-language-pages.py` erzeugt.

## Videos

Die Abgehakt-Seite zeigt fünf sichtbare Vorschaubilder in der gewählten Sprache und einen gemeinsamen Player:
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
Jede Anleitung enthält zwei bis sieben vollständige Appbilder mit passenden
Hervorhebungen, jeweils in der ausgewählten Sprache. Insgesamt sind es 176
Bildverweise pro Sprache und 233 wiederverwendete WebP-Dateien. Ein Tipp öffnet
die vergrößerte Bildfolge mit Vor/Zurück und Tastaturbedienung. Bilder laden erst
bei Bedarf; die App verlinkt auf diese Seiten und enthält keine Hilfefotos. Die kurzen
Textanleitungen bleiben offline in der App verfügbar. Bildverweise und Hervorhebungen
liegen ausschließlich in `assets/abgehakt/help-images.json`.
Mit `python tools/sync-app-help.py --app-repo ../Einkaufsliste` übernehmen und
anschließend `python tools/build-language-pages.py` ausführen.

`python tools/check-help-pages.py http://127.0.0.1:8766` prüft die
Sprachpaare, alle Schritte, Suche, Sprungmarken und den Betrieb ohne JavaScript.
Zusätzlich prüft der Check alle Bilddateien, Sprache, vollständige Proportionen,
Fokusgrenzen, Vergrößerung und die Rückkehr zur ausgewählten Vorschau.
