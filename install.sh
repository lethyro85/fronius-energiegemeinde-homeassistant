#!/bin/bash

# Fronius Energiegemeinschaft Installation Script
# Dieses Skript installiert die Integration in Home Assistant

set -e

echo "=========================================="
echo "Fronius Energiegemeinschaft Installation"
echo "=========================================="
echo ""

# Prüfe ob HA Config Verzeichnis existiert
if [ -z "$1" ]; then
    echo "Bitte geben Sie den Pfad zu Ihrem Home Assistant Config-Verzeichnis an:"
    echo "Beispiel: ./install.sh /config"
    echo "Oder:     ./install.sh /home/homeassistant/.homeassistant"
    exit 1
fi

CONFIG_DIR="$1"

if [ ! -d "$CONFIG_DIR" ]; then
    echo "Fehler: Verzeichnis $CONFIG_DIR existiert nicht!"
    exit 1
fi

echo "Home Assistant Config: $CONFIG_DIR"
echo ""

# Erstelle custom_components Verzeichnis falls nicht vorhanden
CUSTOM_COMPONENTS="$CONFIG_DIR/custom_components"
if [ ! -d "$CUSTOM_COMPONENTS" ]; then
    echo "Erstelle custom_components Verzeichnis..."
    mkdir -p "$CUSTOM_COMPONENTS"
fi

# Kopiere Integration
INTEGRATION_DIR="$CUSTOM_COMPONENTS/fronius_energiegemeinschaft"
echo "Installiere Integration nach $INTEGRATION_DIR..."

if [ -d "$INTEGRATION_DIR" ]; then
    echo "Warnung: Integration existiert bereits. Wird überschrieben..."
    rm -rf "$INTEGRATION_DIR"
fi

# Kopiere Dateien
cp -r custom_components/fronius_energiegemeinschaft "$CUSTOM_COMPONENTS/"

echo ""
echo "✅ Installation erfolgreich!"
echo ""
echo "Nächste Schritte:"
echo "1. Starten Sie Home Assistant neu"
echo "2. Gehen Sie zu Einstellungen → Geräte & Dienste"
echo "3. Klicken Sie auf '+ Integration hinzufügen'"
echo "4. Suchen Sie nach 'Fronius Energiegemeinschaft'"
echo "5. Geben Sie Ihre Anmeldedaten ein"
echo ""
echo "=========================================="
