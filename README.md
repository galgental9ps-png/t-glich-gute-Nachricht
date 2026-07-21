# Daily Good News Monitor

Ein automatisch erzeugter, statischer Nachrichtenmonitor mit einem lustigen
Ziegen-Header. Das Projekt liest ausschließlich öffentliche RSS-/Atom-Feeds
aus einer transparenten Quellenliste und veröffentlicht die Ausgabe über
GitHub Pages.

## Sicherheitsmodell

- keine Benutzerkonten
- keine Cookies
- kein Tracking
- keine Datenbank
- keine Formulare
- keine API-Schlüssel
- keine KI-API
- externe Links werden mit `noopener noreferrer` geöffnet
- erlaubte Domains werden vor der Ausgabe geprüft
- GitHub Actions erhält nur die erforderlichen Berechtigungen
- die Website besteht ausschließlich aus statischen Dateien

## Lokaler Start

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/generate.py
python -m http.server 8000
```

Danach `http://localhost:8000/docs/` öffnen.

## Veröffentlichung auf GitHub Pages

1. Neues öffentliches Repository erstellen.
2. Alle Dateien dieses Projekts hochladen.
3. Unter **Settings → Pages → Build and deployment** als Quelle
   **GitHub Actions** auswählen.
4. Unter **Actions** den Workflow **Update Good News Monitor** einmal manuell starten.
5. Danach läuft er täglich automatisch.

## Quellen bearbeiten

Die Datei `sources.json` enthält alle zugelassenen Feeds, Domains und
Schlüsselwörter. Nur vertrauenswürdige offizielle Quellen eintragen.

## Wichtiger redaktioneller Hinweis

Die Auswahl erfolgt automatisch über Schlüsselwörter. Das Skript versteht
Nachrichten nicht wie ein Mensch. Deshalb können unpassende oder unvollständige
Meldungen erscheinen. Für eine öffentliche redaktionelle Publikation sollte
zusätzlich eine manuelle Freigabe oder eine Positivliste einzelner Meldungen
eingebaut werden.

## Lizenz

Der Programmcode steht unter der MIT-Lizenz. Das Ziegenbild ist nur für dieses
Projekt vorgesehen. Prüfe vor einer weiteren kommerziellen Nutzung die
gewünschten Bildrechte und ersetze es bei Bedarf durch ein eigenes Bild.
