# Fronius Energiegemeinschaft - Home Assistant Integration

[![Version](https://img.shields.io/github/v/release/lethyro85/fronius-energiegemeinde-homeassistant)](https://github.com/lethyro85/fronius-energiegemeinde-homeassistant/releases)
[![License](https://img.shields.io/github/license/lethyro85/fronius-energiegemeinde-homeassistant)](LICENSE)

Diese Custom Integration ermöglicht die Anbindung des Fronius Energiegemeinschafts-Portals an Home Assistant.

**Aktuelle Version:** 0.1.0 ([Changelog](CHANGELOG.md))

## Features

- 📊 **Energiedaten für Ihre Energiegemeinschaft**
  - Gesamtverbrauch und -erzeugung der Community
  - Aufschlüsselung nach Netz und Community-Anteil

- 📈 **Persönliche Zählpunkt-Daten**
  - Ihr individueller Verbrauch und Erzeugung
  - Tägliche Aufschlüsselung der letzten 30 Tage

- 🔄 **Automatische Aktualisierung** alle 5 Minuten
- ⏱️ **Datenhistorie:** Tägliche Werte für die letzten 30 Tage
- 📅 **Hinweis:** Daten sind ca. 2 Tage verzögert (Smart Meter Übermittlung)

### Sensoren

**Community-Sensoren:**
- Community Bezug (Community Received)
- Netzbezug (Grid Consumption)
- Gesamtverbrauch (Total Consumption)
- Community Einspeisung (Community Feed-in)
- Netzeinspeisung (Grid Feed-in)
- Gesamteinspeisung (Total Feed-in)

**Counter Point Sensoren (persönliche Zählpunkte):**
- Verbrauch (Consumer): Ihr täglicher Stromverbrauch
- Erzeugung (Producer): Ihre tägliche Stromproduktion

### Sensor-Attribute

Alle Sensoren bieten zusätzliche Attribute mit täglichen Daten:
- `daily_data_crec`: Täglicher Community-Bezug (Dict: Datum → kWh)
- `daily_data_cgrid`: Täglicher Netzbezug (Dict: Datum → kWh)
- `daily_data_ctotal`: Täglicher Gesamtverbrauch (Dict: Datum → kWh)
- `daily_data_frec`: Tägliche Community-Einspeisung (Dict: Datum → kWh)
- `daily_data_fgrid`: Tägliche Netzeinspeisung (Dict: Datum → kWh)
- `daily_data_ftotal`: Tägliche Gesamteinspeisung (Dict: Datum → kWh)
- `last_30_days_*`: Listen mit den letzten 30 Tageswerten

## Installation

### HACS (empfohlen)

1. Öffnen Sie HACS in Home Assistant
2. Klicken Sie auf "Integrations"
3. Klicken Sie auf die drei Punkte oben rechts und wählen Sie "Custom repositories"
4. Fügen Sie diese Repository-URL hinzu: `https://github.com/lethyro85/fronius-energiegemeinde-homeassistant`
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

### Dashboard-Beispiele

Wir bieten fertige Dashboard-Konfigurationen an:

**📊 [dashboard_personal_data.yaml](dashboard_personal_data.yaml)**
- Ihr täglicher Verbrauch (Gemeinschaft + Netz)
- Ihre tägliche Einspeisung (Gemeinschaft + Netz)
- Gemeinschafts-Übersicht
- Verwendet Ihre persönlichen Counter Point Sensoren

**📈 [dashboard_with_percentage.yaml](dashboard_with_percentage.yaml)**
- Wie oben, zusätzlich mit **Prozentanzeige**
- Zeigt Balken für absolute Werte (kWh)
- Zeigt Linie für Prozentsatz aus der Gemeinschaft
- Dual Y-Achsen (kWh + %)

**Voraussetzung:** [ApexCharts Card](https://github.com/RomRider/apexcharts-card) muss über HACS installiert sein.

### Einfache Übersicht-Karte

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
  - entity: sensor.counter_point_1_consumer
  - entity: sensor.counter_point_2_producer
```

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
