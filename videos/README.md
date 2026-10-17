# Abgehakt – Dein Einkauf im Griff.

`einkaufsliste-gerichte.mp4`: Hochformat 720 × 1280, H.264, 24 Bilder/s,
mit eingeblendeten Texten, ohne Ton. Der Player startet erst auf Wunsch.
Die Mediendateinamen bleiben für bestehende Links stabil.
Das Poster liegt unter `assets/einkaufsliste/poster.jpg`.

Das Video besteht aus echten Android-Compose-Ansichten, die automatisiert
mit Robolectric gerendert wurden. Es ist eine geschnittene Funktionsübersicht,
keine durchgehende Aufnahme eines physischen Telefons. Barcode- und
Produktsuchergebnisse stammen aus Test-Doubles; keine Kamerabilder werden
vorgetäuscht. Die Familien-Szene zeigt den Einstieg zur gemeinsamen Liste,
keinen aufgenommenen Abgleich zwischen zwei Geräten. Alle Einkäufe und
Ausgaben sind Beispieldaten. Keine fremden Produktfotos oder Musik verwendet.

## Wiederherstellen

Benötigt: Python 3, FFmpeg mit libx264/drawtext und DejaVu-Sans-Schriften sowie
Checkout von `CaptAwesome89/Einkaufsliste` (Stand 06ceac9) mit Android-Testumgebung.

1. `tools/capture/PromoVideoCapture.kt` vorübergehend nach
   `app/src/test/java/io/github/captawesome89/einkaufsliste/ui/` im App-Repo kopieren.
2. Dort `SCREENSHOTS=true ./gradlew testDebugUnitTest --tests '*StoreScreenshots*'
   --tests '*ShoppingPreparationUiTest*' --tests '*PromoVideoCapture*'` ausführen.
   Die Tests erzeugen `app/build/screenshots`, `app/build/ui-previews` und
   `app/build/promo`. Netzwerk-/Proxy-Konfiguration der Testumgebung beachten.
3. Hier `python tools/render-app-video.py /pfad/zur/Einkaufsliste` ausführen.
4. Die vorübergehende Capture-Datei im App-Checkout wieder entfernen.

`storyboard.json` enthält Reihenfolge, Laufzeiten, Quellansichten und Einblendungen.
Der deutsche Pro-Basispreis ist 3,99 € einmalig. Scanner und erweiterte Analyse
benötigen Pro. Familien erstellen/einladen benötigt Pro, Beitreten ist kostenlos.
Es gibt noch keinen Store-Link: bis zur Veröffentlichung „Bald bei Google Play“.
