# 2023_11-Karlsruhe-Bicycle-Data

- API: https://github.com/bundesAPI/eco-visio-api
- Liste der Zählstationen: https://github.com/bundesAPI/eco-visio-api/blob/main/eco-visio-api.csv

- Für Wetter-Daten gibt es das rDWD Paket, das im Wesentlichen ein API zu öffentlich verfügbaren Wetter-Datenbanken des DWD ist.
  - https://bookdown.org/brry/rdwd/
  - https://cran.r-project.org/web/packages/rdwd/index.html
- Die Wetterstation nahe Karlsruhe ist Rheinstetten, https://www.dwd.de/DE/wetter/wetterundklima_vorort/baden-wuerttemberg/rheinstetten/_node.html, findest du vermutlich über den Namen.
  - [https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/[…]temperature/recent/TU_Stundenwerte_Beschreibung_Stationen.txt](LINK)
  - Identifier sollte 04177 sein
- Die Rohdaten gibt es theoretisch auch über z.B: https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/air_temperature/recent/, aber das rDWD Paket ist sicher die einfachere Zugriffsmöglichkeit darauf
- Die Daten sind vermutlich in stündlicher Auflösung und müssten zu tageweisen Daten aggregiert werden (z.B. Summe Niederschlag, Durchschnitts- / Maximum- Temperatur und Windgeschwindigkeit, Sonnenscheindauer,
