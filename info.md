# Fronius Energiegemeinschaft Integration

Integration für Home Assistant zur Anbindung des Fronius Energiegemeinschafts-Portals.

## Features

✅ Automatischer Abruf der Energiedaten
✅ Unterstützung für mehrere Energiegemeinschaften
✅ Unterstützung für mehrere Zählpunkte
✅ Automatische Aktualisierung alle 5 Minuten
✅ Einfache Konfiguration über die UI
✅ Deutsche Übersetzung

## Sensoren

Die Integration erstellt automatisch Sensoren für:

### Community-Daten
- **Community Received** - Von der Community bezogene Energie
- **Grid Consumption** - Vom Netz bezogene Energie
- **Total Consumption** - Gesamtverbrauch
- **Community Feed-in** - In die Community eingespeiste Energie
- **Grid Feed-in** - Ins Netz eingespeiste Energie
- **Total Feed-in** - Gesamteinspeisung

### Zählpunkt-Daten
Für jeden Zählpunkt (Consumer/Producer) werden individuelle Sensoren erstellt.

## Installation

Nach der Installation über HACS:

1. Starten Sie Home Assistant neu
2. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
3. Klicken Sie auf **+ Integration hinzufügen**
4. Suchen Sie nach "Fronius Energiegemeinschaft"
5. Geben Sie Ihre Anmeldedaten ein

## Konfiguration

Die Integration wird über die Benutzeroberfläche konfiguriert. Sie benötigen:

- E-Mail-Adresse für das Fronius Energiegemeinschafts-Portal
- Passwort für das Portal

## Support

Bei Problemen oder Fragen erstellen Sie bitte ein Issue auf Codeberg.
