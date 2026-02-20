# Manuelle Installation - Fronius Energiegemeinschaft

Da HACS nur GitHub-Repositories unterstützt, hier die Anleitung für die manuelle Installation.

## Methode 1: Mit Installations-Skript (Linux/Docker)

Wenn Sie SSH-Zugriff auf Ihren Home Assistant Server haben:

```bash
# 1. Klonen Sie das Repository
cd /tmp
git clone https://codeberg.org/lethyro/fronius-energiegemeinde-homeassistant.git
cd fronius-energiegemeinde-homeassistant

# 2. Führen Sie das Installations-Skript aus
./install.sh /config

# (Ersetzen Sie /config mit dem Pfad zu Ihrem HA Config-Verzeichnis)
```

## Methode 2: Manuelle Datei-Kopie

### Schritt 1: Repository herunterladen

1. Gehen Sie zu: https://codeberg.org/lethyro/fronius-energiegemeinde-homeassistant
2. Klicken Sie auf **"Code"** → **"Download ZIP"**
3. Entpacken Sie die ZIP-Datei

### Schritt 2: Dateien kopieren

Kopieren Sie den Ordner `custom_components/fronius_energiegemeinschaft` in Ihr Home Assistant Config-Verzeichnis:

```
<HA-Config-Verzeichnis>/
└── custom_components/
    └── fronius_energiegemeinschaft/
        ├── __init__.py
        ├── api_client.py
        ├── config_flow.py
        ├── const.py
        ├── manifest.json
        ├── sensor.py
        ├── strings.json
        └── translations/
            └── de.json
```

**Wichtig:** Der Ordner muss genau `fronius_energiegemeinschaft` heißen!

### Schritt 3: Home Assistant neu starten

Starten Sie Home Assistant neu über:
- **Einstellungen** → **System** → **Neu starten**
- Oder über die Kommandozeile: `ha core restart`

## Methode 3: Über Samba/SMB Share

Wenn Sie Samba eingerichtet haben:

1. Verbinden Sie sich mit Ihrem Home Assistant Server über SMB
2. Navigieren Sie zu `config/custom_components/`
3. Erstellen Sie den Ordner `fronius_energiegemeinschaft`
4. Kopieren Sie alle Dateien aus dem Repository hinein
5. Starten Sie Home Assistant neu

## Methode 4: File Editor Add-on

Wenn Sie das File Editor Add-on installiert haben:

1. Öffnen Sie den File Editor in Home Assistant
2. Erstellen Sie den Ordner `custom_components/fronius_energiegemeinschaft`
3. Erstellen Sie alle erforderlichen Dateien und kopieren Sie den Inhalt
   (aus dem Codeberg Repository)

## Nach der Installation

1. **Neustart:** Starten Sie Home Assistant neu
2. **Integration hinzufügen:**
   - Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
   - Klicken Sie auf **+ Integration hinzufügen**
   - Suchen Sie nach "Fronius Energiegemeinschaft"
3. **Konfiguration:**
   - Geben Sie Ihre E-Mail-Adresse ein
   - Geben Sie Ihr Passwort ein
   - Klicken Sie auf **Absenden**

## Überprüfung

Nach dem Neustart sollten Sie die Integration finden können:
- Suchen Sie in den Integrationen nach "Fronius"
- Prüfen Sie die Logs auf Fehler: **Einstellungen** → **System** → **Protokolle**

## Updates

Um die Integration zu aktualisieren:

1. Laden Sie die neueste Version von Codeberg herunter
2. Ersetzen Sie den Ordner `custom_components/fronius_energiegemeinschaft`
3. Starten Sie Home Assistant neu

## Häufige Probleme

### Integration wird nicht gefunden

- Stellen Sie sicher, dass der Ordnername exakt `fronius_energiegemeinschaft` ist
- Überprüfen Sie, dass alle Dateien vorhanden sind
- Prüfen Sie die Berechtigungen (sollten vom HA-User lesbar sein)
- Starten Sie Home Assistant neu

### Fehler beim Laden

Aktivieren Sie Debug-Logging in `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.fronius_energiegemeinschaft: debug
```

Prüfen Sie dann die Logs unter **Einstellungen** → **System** → **Protokolle**

## Support

Bei Problemen erstellen Sie bitte ein Issue auf Codeberg:
https://codeberg.org/lethyro/fronius-energiegemeinde-homeassistant/issues
