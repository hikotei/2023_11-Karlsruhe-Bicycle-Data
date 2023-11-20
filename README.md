# 2023_11-Karlsruhe-Bicycle-Data

---

### Update 2023.11.20

#### Neue Spalten

| Column Name                | Description                 |
|--------------------------- |-----------------------------|
| "date"                     | Date of the record          |
| "count"                    | Count column                |
| "weekday"                  | Day of the week             |
| "is_weekend"               | Indicator for weekend       |
| "is_holiday"               | Indicator for holiday       |
| "FX.Windspitze"            | Windspitze column           |
| "FM.Windgeschwindigkeit"   | Windgeschwindigkeit column  |
| "RSK.Niederschlagshoehe"   | Niederschlagshoehe column   |
| "RSKF.Niederschlagsform"   | Niederschlagsform column    |
| "SDK.Sonnenscheindauer"    | Sonnenscheindauer column    |
| "SHK_TAG.Schneehoehe"      | Schneehoehe column          |
| "NM.Bedeckungsgrad"        | Bedeckungsgrad column       |
| "TMK.Lufttemperatur"       | Lufttemperatur column       |
| "UPM.Relative_Feuchte"     | Relative Feuchte column     |
| "TXK.Lufttemperatur_Max"   | Lufttemperatur_Max column   |
| "TNK.Lufttemperatur_Min"   | Lufttemperatur_Min column   |
| "TGK.Lufttemperatur_5cm_min"| Lufttemperatur_5cm_min column|

#### Corr Plot
![Alt text](path/to/bikedata_corr_plot.png "Title")

#### Fragen zu R DWD
- was bedeutet KL bei den variabeln? scheint eine Zusammenfassung von mehreren Wetterkennzahlen zu sein?
- schien ganz praktisch zu sein alle variabeln in einem Link zu bekommen ... habe ich benutzt

---

### ToDos 2023.11.03
- API: https://github.com/bundesAPI/eco-visio-api
- Liste der Zählstationen: https://github.com/bundesAPI/eco-visio-api/blob/main/eco-visio-api.csv

- Für Wetter-Daten gibt es das rDWD Paket, das im Wesentlichen ein API zu öffentlich verfügbaren Wetter-Datenbanken des DWD ist.
  - https://bookdown.org/brry/rdwd/
  - https://cran.r-project.org/web/packages/rdwd/index.html
 
- Die Wetterstation nahe Karlsruhe ist [Rheinstetten](https://www.dwd.de/DE/wetter/wetterundklima_vorort/baden-wuerttemberg/rheinstetten/_node.html), findest du vermutlich über den Namen.
  - [Alle Stationen für Lufttemperatur zB](https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/air_temperature/recent/TU_Stundenwerte_Beschreibung_Stationen.txt) Identifier sollte 04177 sein

- Die Rohdaten gibt es theoretisch auch über z.B: [LINK](https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/air_temperature/recent/), aber das rDWD Paket ist sicher die einfachere Zugriffsmöglichkeit darauf
- Die Daten sind vermutlich in stündlicher Auflösung und müssten zu tageweisen Daten aggregiert werden (z.B. Summe Niederschlag, Durchschnitts- / Maximum- Temperatur und Windgeschwindigkeit, Sonnenscheindauer,
