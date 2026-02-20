# Installation der Fronius Energiegemeinschaft Integration

## Voraussetzungen

- Home Assistant Core 2023.1.0 oder höher
- Zugang zum Fronius Energiegemeinschafts-Portal (https://energiegemeinschaften.fronius.at)
- Gültige Anmeldedaten für das Portal

## Installationsmethoden

### Methode 1: HACS Installation (empfohlen)

1. Stellen Sie sicher, dass [HACS](https://hacs.xyz/) installiert ist
2. Öffnen Sie HACS in Home Assistant
3. Klicken Sie auf "Integrations"
4. Klicken Sie auf die drei Punkte (⋮) oben rechts
5. Wählen Sie "Custom repositories"
6. Fügen Sie folgende URL hinzu: `https://codeberg.org/lethyro/fronius-energiegemeinde-homeassistant`
7. Wählen Sie als Kategorie: "Integration"
8. Klicken Sie auf "Add"
9. Suchen Sie nun nach "Fronius Energiegemeinschaft"
10. Klicken Sie auf "Download"
11. Starten Sie Home Assistant neu

### Methode 2: Manuelle Installation

1. Laden Sie die neueste Version von [Codeberg Releases](https://codeberg.org/lethyro/fronius-energiegemeinde-homeassistant/releases) herunter
2. Entpacken Sie das Archiv
3. Kopieren Sie den Ordner `custom_components/fronius_energiegemeinschaft` in Ihr Home Assistant Konfigurationsverzeichnis unter `custom_components/`
   - Der Pfad sollte sein: `<config>/custom_components/fronius_energiegemeinschaft/`
4. Starten Sie Home Assistant neu

## Konfiguration

### Schritt 1: Integration hinzufügen

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Klicken Sie auf **+ Integration hinzufügen** (unten rechts)
3. Suchen Sie nach "Fronius Energiegemeinschaft"
4. Klicken Sie auf die Integration

### Schritt 2: Anmeldedaten eingeben

1. Geben Sie Ihre **E-Mail-Adresse** ein, die Sie für das Fronius Portal verwenden
2. Geben Sie Ihr **Passwort** ein
3. Klicken Sie auf **Absenden**

### Schritt 3: Überprüfung

Die Integration wird sich nun mit dem Fronius Portal verbinden und:
- Ihre Energiegemeinschaft(en) abrufen
- Ihre Zählpunkte abrufen
- Sensoren für alle verfügbaren Daten erstellen

Sie sollten nun neue Sensoren in Home Assistant sehen.

## Sensoren

Die Integration erstellt folgende Sensoren für jede Energiegemeinschaft:

- **Community Received** (crec): Von der Community bezogene Energie
- **Grid Consumption** (cgrid): Vom Netz bezogene Energie
- **Total Consumption** (ctotal): Gesamtverbrauch
- **Community Feed-in** (frec): In die Community eingespeiste Energie
- **Grid Feed-in** (fgrid): Ins Netz eingespeiste Energie
- **Total Feed-in** (ftotal): Gesamteinspeisung

Zusätzlich werden für jeden Zählpunkt (Consumer/Producer) eigene Sensoren erstellt.

## Nächste Schritte

Nach der Installation können Sie:
1. Die Sensoren in Dashboards verwenden
2. Automationen basierend auf den Energiedaten erstellen
3. Die Sensoren im Energie-Dashboard einbinden

Siehe [README.md](README.md) für Beispiele und weitere Informationen.

## Fehlerbehebung

### Integration erscheint nicht in der Liste

- Stellen Sie sicher, dass Sie Home Assistant neu gestartet haben
- Überprüfen Sie, ob der Ordner korrekt unter `custom_components/` liegt
- Prüfen Sie die Logs auf Fehlermeldungen

### Anmeldung schlägt fehl

- Überprüfen Sie Ihre Anmeldedaten im Browser: https://energiegemeinschaften.fronius.at
- Stellen Sie sicher, dass Ihr Home Assistant Server Internetzugang hat
- Prüfen Sie die Logs für detaillierte Fehlermeldungen

### Keine Sensoren werden erstellt

- Überprüfen Sie, ob in Ihrem Account Energiegemeinschaften vorhanden sind
- Aktivieren Sie Debug-Logging (siehe README.md)
- Erstellen Sie ein Issue auf Codeberg mit den Log-Informationen

## Support

Bei Problemen oder Fragen:
- Erstellen Sie ein [Issue auf Codeberg](https://codeberg.org/lethyro/fronius-energiegemeinde-homeassistant/issues)
- Aktivieren Sie Debug-Logging und fügen Sie relevante Log-Auszüge hinzu
