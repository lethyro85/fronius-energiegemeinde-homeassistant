# Fronius Energiegemeinschaft - Home Assistant Integration

[![Version](https://img.shields.io/github/v/release/lethyro85/fronius-energiegemeinde-homeassistant)](https://github.com/lethyro85/fronius-energiegemeinde-homeassistant/releases)
[![License](https://img.shields.io/github/license/lethyro85/fronius-energiegemeinde-homeassistant)](LICENSE)

Diese Custom Integration ermöglicht die Anbindung des Fronius Energiegemeinschafts-Portals an Home Assistant.

**Aktuelle Version:** 0.2.7 ([Changelog](CHANGELOG.md))

## Features

- 📊 **Energiedaten für Ihre Energiegemeinschaft**
  - Gesamtverbrauch und -erzeugung der Community
  - Aufschlüsselung nach Netz und Community-Anteil

- 📈 **Persönliche Zählpunkt-Daten**
  - Ihr individueller Verbrauch und Erzeugung
  - Tägliche Aufschlüsselung der letzten 30 Tage

- 💰 **Kosten-Tracking**
  - Konfigurierbare Strompreise (Netz & Gemeinde, Verbrauch & Einspeisung)
  - Tägliche, monatliche und jährliche Kostenberechnung
  - Automatische Berechnung der Nettokosten (Verbrauch - Einspeisevergütung)
  - Detaillierte Kostenaufschlüsselung nach Quelle

- 📉 **Langzeit-Statistiken** (ab v0.2.6)
  - Monatliche Kosten werden automatisch in den HA Recorder geschrieben
  - Rückwirkend 13 Monate beim ersten Start befüllt
  - Sichtbar unter *Developer Tools → Statistiken* und in ApexCharts nutzbar

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

**Kosten-Sensoren:**
- **Daily Cost**: Tageskosten mit detaillierter Aufschlüsselung
- **Monthly Cost**: Monatliche Gesamtkosten
- **Yearly Cost**: Jährliche Gesamtkosten

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
4. **Schritt 1:** Geben Sie Ihre Anmeldedaten für das Fronius Energiegemeinschafts-Portal ein
5. **Schritt 2:** Konfigurieren Sie Ihre Strompreise
   - Netzanbieter Verbrauchspreis (€/kWh)
   - Gemeinde Verbrauchspreis (€/kWh)
   - Netzanbieter Einspeisepreis (€/kWh)
   - Gemeinde Einspeisepreis (€/kWh)
6. Klicken Sie auf **Absenden**

Die Integration wird sich dann mit dem Portal verbinden und die verfügbaren Sensoren erstellen.

### Strompreise ändern

Sie können Ihre Strompreise jederzeit ändern:

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Suchen Sie die "Fronius Energiegemeinschaft" Integration
3. Klicken Sie auf **Konfigurieren**
4. Aktualisieren Sie die Preise und klicken Sie auf **Absenden**

Die Integration wird automatisch neu geladen und die Kostenberechnungen aktualisiert.

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

**💰 [dashboard_costs_monthly.yaml](dashboard_costs_monthly.yaml)**
- Monatliche Kostenübersicht
- Gestapelte Balken (Netz + Gemeinde)
- Gesamtkosten als Linie
- Zeigt letzte 12 Monate

**📊 [dashboard_costs_daily_detail.yaml](dashboard_costs_daily_detail.yaml)**
- Tägliche Kostendetails der letzten 30 Tage
- Aufschlüsselung: Netz-Verbrauch, Gemeinde-Verbrauch, Einspeisung
- Nettokosten als Linie

**📅 [dashboard_costs_monthly_selector.yaml](dashboard_costs_monthly_selector.yaml)**
- Monatsvergleich der letzten 12 Monate
- Detaillierte Aufschlüsselung pro Monat
- Jahresübersicht

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
  - entity: sensor.counter_point_1_consumer_daily_cost
    name: Tageskosten
  - entity: sensor.counter_point_1_consumer_monthly_cost
    name: Monatskosten
  - entity: sensor.counter_point_1_consumer_yearly_cost
    name: Jahreskosten
```
### Komplexe Dashboard-Karte

```yaml
type: custom:vertical-stack-in-card
cards:
  - type: custom:apexcharts-card
    header:
      show: true
      title: Mein täglicher Verbrauch (letzte 30 Tage)
      show_states: true
      colorize_states: true
    graph_span: 30d
    span:
      end: day
      offset: "-2d"
    now:
      show: true
      label: Heute
    series:
      - entity: sensor.counter_point_1_consumer
        name: Gemeinschaft
        type: column
        color: "#4CAF50"
        data_generator: |
          return entity.attributes.daily_data_crec ?
            Object.entries(entity.attributes.daily_data_crec).map(([date, value]) => {
              return [new Date(date).getTime(), value];
            }).slice(-30) : [];
        show:
          in_header: true
          legend_value: true
      - entity: sensor.counter_point_1_consumer
        name: Netz
        type: column
        color: "#FF9800"
        data_generator: |
          return entity.attributes.daily_data_cgrid ?
            Object.entries(entity.attributes.daily_data_cgrid).map(([date, value]) => {
              return [new Date(date).getTime(), value];
            }).slice(-30) : [];
        show:
          in_header: true
          legend_value: true
    apex_config:
      chart:
        height: 300px
      plotOptions:
        bar:
          columnWidth: 80%
      dataLabels:
        enabled: false
      yaxis:
        title:
          text: Energie (kWh)
      xaxis:
        type: datetime
      tooltip:
        x:
          format: dd.MM.yyyy
      legend:
        show: true
        position: top
  - type: custom:apexcharts-card
    header:
      show: true
      title: Meine tägliche Einspeisung (letzte 30 Tage)
      show_states: true
      colorize_states: true
    graph_span: 30d
    span:
      end: day
      offset: "-2d"
    now:
      show: true
      label: Heute
    series:
      - entity: sensor.counter_point_2_producer
        name: Gemeinschaft
        type: column
        color: "#2196F3"
        data_generator: |
          return entity.attributes.daily_data_frec ?
            Object.entries(entity.attributes.daily_data_frec).map(([date, value]) => {
              return [new Date(date).getTime(), value];
            }).slice(-30) : [];
        show:
          in_header: true
          legend_value: true
      - entity: sensor.counter_point_2_producer
        name: Netz
        type: column
        color: "#9C27B0"
        data_generator: |
          return entity.attributes.daily_data_fgrid ?
            Object.entries(entity.attributes.daily_data_fgrid).map(([date, value]) => {
              return [new Date(date).getTime(), value];
            }).slice(-30) : [];
        show:
          in_header: true
          legend_value: true
    apex_config:
      chart:
        height: 300px
      plotOptions:
        bar:
          columnWidth: 80%
      dataLabels:
        enabled: false
      yaxis:
        title:
          text: Energie (kWh)
      xaxis:
        type: datetime
      tooltip:
        x:
          format: dd.MM.yyyy
      legend:
        show: true
        position: top
  - type: custom:apexcharts-card
    header:
      show: true
      title: Energiegemeinschaft Gesamt (letzte 30 Tage)
      show_states: true
      colorize_states: true
    graph_span: 30d
    span:
      end: day
      offset: "-2d"
    now:
      show: true
      label: Heute
    series:
      - entity: sensor.fronius_energiegemeinschaft_total_feed_in
        name: Erzeugung
        type: column
        color: "#4CAF50"
        data_generator: |
          return entity.attributes.daily_data ?
            Object.entries(entity.attributes.daily_data).map(([date, value]) => {
              return [new Date(date).getTime(), value];
            }).slice(-30) : [];
        show:
          in_header: true
          legend_value: true
      - entity: sensor.fronius_energiegemeinschaft_total_consumption
        name: Verbrauch
        type: column
        color: "#FF5722"
        data_generator: |
          return entity.attributes.daily_data ?
            Object.entries(entity.attributes.daily_data).map(([date, value]) => {
              return [new Date(date).getTime(), value];
            }).slice(-30) : [];
        show:
          in_header: true
          legend_value: true
    apex_config:
      chart:
        height: 300px
      plotOptions:
        bar:
          columnWidth: 80%
      dataLabels:
        enabled: false
      yaxis:
        title:
          text: Energie (kWh)
      xaxis:
        type: datetime
      tooltip:
        x:
          format: dd.MM.yyyy
      legend:
        show: true
        position: top
  - type: custom:apexcharts-card
    header:
      show: true
      title: Tägliche Stromkosten (letzte 30 Tage)
      show_states: true
      colorize_states: true
    graph_span: 30d
    span:
      end: day
      offset: "-2d"
    now:
      show: true
      label: Heute
    series:
      - entity: sensor.counter_point_1_daily_cost
        name: Netz Verbrauch
        type: column
        color: "#FF5722"
        data_generator: |
          const breakdown = entity.attributes.daily_costs_breakdown;
          if (!breakdown) return [];
          return Object.entries(breakdown).map(([date, data]) => {
            return [new Date(date).getTime(), data.grid_consumption_cost];
          }).slice(-30);
        show:
          in_header: true
          legend_value: true
      - entity: sensor.counter_point_1_daily_cost
        name: Gemeinde Verbrauch
        type: column
        color: "#4CAF50"
        data_generator: |
          const breakdown = entity.attributes.daily_costs_breakdown;
          if (!breakdown) return [];
          return Object.entries(breakdown).map(([date, data]) => {
            return [new Date(date).getTime(), data.community_consumption_cost];
          }).slice(-30);
        show:
          in_header: true
          legend_value: true
      - entity: sensor.counter_point_2_daily_cost
        name: Einspeisung
        type: column
        color: "#9C27B0"
        data_generator: |
          const breakdown = entity.attributes.daily_costs_breakdown;
          if (!breakdown) return [];
          return Object.entries(breakdown).map(([date, data]) => {
            const revenue = data.grid_feed_in_revenue + data.community_feed_in_revenue;
            return [new Date(date).getTime(), -revenue];
          }).slice(-30);
        show:
          in_header: true
          legend_value: true
      - entity: sensor.counter_point_1_daily_cost
        name: Netto
        type: line
        color: "#2196F3"
        stroke_width: 3
        data_generator: |
          const costs = entity.attributes.daily_costs;
          if (!costs) return [];
          return Object.entries(costs).map(([date, cost]) => {
            return [new Date(date).getTime(), cost];
          }).slice(-30);
        show:
          in_header: true
          legend_value: true
    apex_config:
      chart:
        height: 400px
        stacked: false
      plotOptions:
        bar:
          columnWidth: 80%
      dataLabels:
        enabled: false
      yaxis:
        - title:
            text: Kosten (€)
          labels:
            formatter: |
              EVAL:function(value) {
                return '€ ' + value.toFixed(2);
              }
      xaxis:
        type: datetime
      tooltip:
        x:
          format: dd.MM.yyyy
        "y":
          formatter: |
            EVAL:function(value, opts) {
              if (value < 0) {
                return '€ ' + Math.abs(value).toFixed(2) + ' (Gutschrift)';
              }
              return '€ ' + value.toFixed(2);
            }
      legend:
        show: true
        position: top
      annotations:
        yaxis:
          - "y": 0
            borderColor: "#999"
            strokeDashArray: 3
  - type: custom:apexcharts-card
    header:
      show: true
      title: Monatliche Stromkosten
      show_states: true
      colorize_states: true
    graph_span: 12months
    span:
      end: month
    now:
      show: true
      label: Aktueller Monat
    series:
      - entity: sensor.counter_point_1_monthly_cost
        name: Netzanbieter
        type: column
        color: "#FF5722"
        data_generator: |
          const breakdown = entity.attributes.monthly_costs_breakdown;
          if (!breakdown) return [];
          return Object.entries(breakdown).map(([month, data]) => {
            const cost = data.grid_consumption_cost - data.grid_feed_in_revenue;
            return [new Date(month + '-01').getTime(), cost.toFixed(2)];
          });
        show:
          in_header: true
          legend_value: true
      - entity: sensor.counter_point_1_monthly_cost
        name: Gemeinde
        type: column
        color: "#4CAF50"
        data_generator: |
          const breakdown = entity.attributes.monthly_costs_breakdown;
          if (!breakdown) return [];
          return Object.entries(breakdown).map(([month, data]) => {
            const cost = data.community_consumption_cost - data.community_feed_in_revenue;
            return [new Date(month + '-01').getTime(), cost.toFixed(2)];
          });
        show:
          in_header: true
          legend_value: true
      - entity: sensor.counter_point_1_monthly_cost
        name: Gesamt
        type: line
        color: "#2196F3"
        stroke_width: 3
        data_generator: |
          const costs = entity.attributes.monthly_costs;
          if (!costs) return [];
          return Object.entries(costs).map(([month, cost]) => {
            return [new Date(month + '-01').getTime(), cost.toFixed(2)];
          });
        show:
          in_header: true
          legend_value: true
  - type: vertical-stack
    cards:
      - type: entities
        title: Monatsübersicht
        entities:
          - entity: sensor.counter_point_1_monthly_cost
            name: Aktuelle Monatskosten
          - type: attribute
            entity: sensor.counter_point_1_monthly_cost
            attribute: monthly_costs_breakdown
            name: Detailaufschlüsselung
      - type: custom:apexcharts-card
        header:
          show: true
          title: Monatsvergleich (letzte 12 Monate)
          show_states: true
        graph_span: 12months
        span:
          end: month
        series:
          - entity: sensor.counter_point_1_monthly_cost
            name: Verbrauch
            type: column
            color: "#FF9800"
            data_generator: |
              const breakdown = entity.attributes.monthly_costs_breakdown;
              if (!breakdown) return [];
              return Object.entries(breakdown).map(([month, data]) => {
                const cost = data.grid_consumption_cost + data.community_consumption_cost;
                return [new Date(month + '-01').getTime(), cost.toFixed(2)];
              });
          - entity: sensor.counter_point_2_monthly_cost
            name: Gutschrift
            type: column
            color: "#4CAF50"
            data_generator: |
              const breakdown = entity.attributes.monthly_costs_breakdown;
              if (!breakdown) return [];
              return Object.entries(breakdown).map(([month, data]) => {
                const revenue = data.grid_feed_in_revenue + data.community_feed_in_revenue;
                return [new Date(month + '-01').getTime(), -revenue.toFixed(2)];
              });
          - entity: sensor.counter_point_1_monthly_cost
            name: Netto
            type: line
            color: "#2196F3"
            stroke_width: 3
            data_generator: |
              const costs = entity.attributes.monthly_costs;
              if (!costs) return [];
              return Object.entries(costs).map(([month, cost]) => {
                return [new Date(month + '-01').getTime(), cost.toFixed(2)];
              });
        apex_config:
          chart:
            height: 350px
          plotOptions:
            bar:
              columnWidth: 70%
          dataLabels:
            enabled: true
            formatter: |
              EVAL:function(value) {
                if (value === 0) return '';
                return '€ ' + Math.abs(value).toFixed(0);
              }
          yaxis:
            - title:
                text: Kosten (€)
              labels:
                formatter: |
                  EVAL:function(value) {
                    return '€ ' + value.toFixed(0);
                  }
          xaxis:
            type: datetime
            labels:
              format: MMM yy
          tooltip:
            x:
              format: MMMM yyyy
            "y":
              formatter: |
                EVAL:function(value) {
                  if (value < 0) {
                    return '€ ' + Math.abs(value).toFixed(2) + ' Gutschrift';
                  }
                  return '€ ' + value.toFixed(2);
                }
          legend:
            show: true
            position: top
      - type: entities
        title: Jahresübersicht
        entities:
          - entity: sensor.counter_point_1_yearly_cost
            name: Aktuelle Jahreskosten
          - type: attribute
            entity: sensor.counter_point_1_yearly_cost
            attribute: yearly_cost_breakdown
            name: Jahresaufschlüsselung
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

Bei Problemen oder Fragen erstellen Sie bitte ein Issue auf GitHub: https://github.com/lethyros85/fronius-energiegemeinde-homeassistant/issues
