# Fronius Energiegemeinschaft - Home Assistant Integration

Diese Custom Integration ermöglicht die Anbindung des Fronius Energiegemeinschafts-Portals an Home Assistant.

## Features

- Abruf der Energiedaten für Ihre Energiegemeinschaft
- Abruf der Energiedaten für Ihre Zählpunkte (Messpunkte)
- Automatische Aktualisierung alle 5 Minuten
- Sensoren für:
  - Community Bezug (Community Received)
  - Netzbezug (Grid Consumption)
  - Gesamtverbrauch (Total Consumption)
  - Community Einspeisung (Community Feed-in)
  - Netzeinspeisung (Grid Feed-in)
  - Gesamteinspeisung (Total Feed-in)

## Installation

### HACS (empfohlen)

1. Öffnen Sie HACS in Home Assistant
2. Klicken Sie auf "Integrations"
3. Klicken Sie auf die drei Punkte oben rechts und wählen Sie "Custom repositories"
4. Fügen Sie diese Repository-URL hinzu: `https://codeberg.org/lethyro/fronius-energiegemeinde-homeassistant`
5. Wählen Sie als Kategorie "Integration"
6. Klicken Sie auf "Add"
7. Suchen Sie nach "Fronius Energiegemeinschaft" und installieren Sie die Integration
8. Starten Sie Home Assistant neu

### Manuelle Installation

1. Kopieren Sie den Ordner `custom_components/fronius_energiegemeinschaft` in Ihr Home Assistant `custom_components` Verzeichnis
2. Starten Sie Home Assistant neu

## Konfiguration

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Klicken Sie auf **+ Integration hinzufügen**
3. Suchen Sie nach "Fronius Energiegemeinschaft"
4. Geben Sie Ihre Anmeldedaten für das Fronius Energiegemeinschafts-Portal ein
5. Klicken Sie auf **Absenden**

Die Integration wird sich dann mit dem Portal verbinden und die verfügbaren Sensoren erstellen.

## Verwendung

Nach der Konfiguration werden automatisch Sensoren für Ihre Energiegemeinschaft und Zählpunkte erstellt. Diese können Sie dann in Dashboards, Automationen und Skripten verwenden.

### Beispiel Lovelace-Karte

```yaml
type: entities
title: Fronius Energiegemeinschaft
entities:
  - entity: sensor.fronius_energiegemeinschaft_total_consumption
  - entity: sensor.fronius_energiegemeinschaft_community_received
  - entity: sensor.fronius_energiegemeinschaft_grid_consumption
  - entity: sensor.fronius_energiegemeinschaft_total_feed_in
  - entity: sensor.fronius_energiegemeinschaft_community_feed_in
  - entity: sensor.fronius_energiegemeinschaft_grid_feed_in
```

### Beispiel Energie-Dashboard

Die Sensoren können auch im Home Assistant Energie-Dashboard verwendet werden:

1. Gehen Sie zu **Einstellungen** → **Dashboards** → **Energie**
2. Fügen Sie die gewünschten Sensoren hinzu

## API-Endpunkte

Die Integration nutzt folgende API-Endpunkte:

- `/vis/community` - Community-Liste
- `/vis/community/{id}/energy_data` - Energiedaten für Community
- `/vis/counter_point` - Zählpunkte-Liste
- `/vis/counter_point/{id}/energy_data` - Energiedaten für Zählpunkt

## Fehlerbehebung

### Anmeldung schlägt fehl

Überprüfen Sie, ob Ihre Anmeldedaten korrekt sind und Sie sich im Fronius Energiegemeinschafts-Portal anmelden können.

### Keine Sensoren werden erstellt

Stellen Sie sicher, dass:
- Die Integration korrekt konfiguriert ist
- Home Assistant Internetzugang hat
- Ihre Anmeldedaten korrekt sind

### Debug-Logging aktivieren

Fügen Sie folgendes zu Ihrer `configuration.yaml` hinzu:

```yaml
logger:
  default: info
  logs:
    custom_components.fronius_energiegemeinschaft: debug
```

## Lizenz

MIT License

## Support

Bei Problemen oder Fragen erstellen Sie bitte ein Issue auf Codeberg: https://codeberg.org/lethyro/fronius-energiegemeinde-homeassistant/issues
