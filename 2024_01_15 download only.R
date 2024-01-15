rm(list = ls())
cwd = getwd()

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Load Packages ####
library(httr)
library(dplyr)
library(rdwd)
 
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Get from URL ####

# Define the URL where your data is located
url <- "https://www.eco-visio.net/api/aladdin/1.0.0/pbl/publicwebpageplus/data/100126474?idOrganisme=4586&idPdc=100126474&interval=4&flowIds=100126474"

# Make a GET request to the URL and read the response content
response <- GET(url)
data_text <- content(response, "text")

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Data Processing ####

# remove first 2 and last 2 square brackets [[ ... ]]
txt <- substr(data_text, start=3, stop = nchar(data_text)-2)
# remove all quotation marks and backslashes
txt <- gsub('[\\"]', '', txt)
# split rows by comma and square brackets
rows <- unlist(strsplit(txt, "\\],\\["))

# save in dataframe
data <- data.frame(date = NA, bike_count = NA)
for(i in 1:length(rows)){
    data[i,] <- unlist(strsplit(rows[i], ","))
}

bike_df <- data.frame(date = as.Date(data$date, format = "%m/%d/%Y"), 
                      bike_count = as.numeric(data$bike_count))

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Get Weather Data ####

# Need Daily Data on ...
    # Summe Niederschlag, 
    # Avg- / Max- Temperatur
    # Avg- / Max- Windgeschwindigkeit
    # Sonnenscheindauer

vars_hourly = c("air_temperature", "sun", "precipitation", "visibility", "wind", "extreme_wind")

# coordinates of ettlinger tor = 49.0064, 8.4029
# nearby_stations_df <- nearbyStations(49.0064, 8.4029, radius=10,
#                                      res=c("hourly"), var= vars,
#                                      mindate=as.Date(min(bike_df$date)))

# dir.create('DWDdata')
# locdir()
# oldopt <- options(rdwdlocdir=paste0(cwd, "/DWDdata"))
# locdir()

# - - - - - - - - - 
## get hourly data ####
# - - - - - - - - -

bike_df_first_date <- as.POSIXct(min(bike_df$date))

link <- selectDWD(id=4177, res="hourly", var=vars_hourly, per="recent")
weather_recent <- dataDWD(link, force=NA, varnames=TRUE, read=TRUE)
weather_recent_df <- Reduce(function(df1, df2) merge(df1, df2), weather_recent)

link <- selectDWD(id=4177, res="hourly", var=vars_hourly, per="historical")
weather_hist <- dataDWD(link, force=NA, varnames=TRUE, read=TRUE)
weather_hist_df <- Reduce(function(df1, df2) merge(df1, df2), weather_hist)

# only need historical data up to first timestamp in bicycle data
weather_hist_df <- weather_hist_df[weather_hist_df$MESS_DATUM > bike_df_first_date, ]

# only need recent data up to last timestamp in weather_hist_df
weather_hist_last_date <- as.POSIXct(max(weather_hist_df$MESS_DATUM))
weather_recent_df <- weather_recent_df[weather_recent_df$MESS_DATUM > weather_hist_last_date, ]

# rbind weather_recent_df and weather_hist_df
weather_df <- rbind(weather_hist_df, weather_recent_df)

# remove irrelevabt cols
columns_to_remove <- c("eor", "^QN", "V_VV_I")  # Remove columns starting with QN
weather_df_clean <- weather_df[, !grepl(paste(columns_to_remove, collapse = "|"), names(weather_df)), drop = FALSE]

write.csv(weather_df_clean, "weather_df_clean.csv", row.names=FALSE)

# - - - - - - - - - 
## aggregate to daily data ####
# - - - - - - - - -

col_to_avg = c("TT_TU.Lufttemperatur", "RF_TU.Relative_Feuchte", 
               "F.Windgeschwindigkeit", "D.Windrichtung", 
               "V_VV.Sichtweite")
col_to_sum = c("R1.Niederschlagshoehe", 
               "SD_SO.Sonnenscheindauer")
col_to_max = c("FX_911.Windspitze_Stunde1")
col_to_median = c("RS_IND.Niederschlagsindikator", "WRTR.Niederschlagsform")

weather_df_daily <- weather_df_clean %>% group_by(date = as.Date(weather_df_clean$MESS_DATUM)) %>%
    summarise(date = as.Date(mean(MESS_DATUM)), 
              temperature = mean(TT_TU.Lufttemperatur), 
              humidity = mean(RF_TU.Relative_Feuchte), 
              windspeed = mean(F.Windgeschwindigkeit), 
              wind_direction = mean(D.Windrichtung), 
              visibility = mean(V_VV.Sichtweite), 
              
              precipitation = sum(R1.Niederschlagshoehe, na.rm=TRUE),
              sun = sum(SD_SO.Sonnenscheindauer),
              
              windspeed_max = max(FX_911.Windspitze_Stunde1),
              
              precip_indic = median(RS_IND.Niederschlagsindikator, na.rm=TRUE),
              precip_type = median(WRTR.Niederschlagsform, na.rm=TRUE))

# - - - - - - - - - 
## check NAs ####
# - - - - - - - - -

# mainly for "precip_indic" and "precip_type" even after na.rm 
# because for some days all values are NA 

# colSums(is.na(weather_df_daily))
# weather_df_daily[rowSums(is.na(weather_df_daily)) > 0, ]

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Merge Data & Save ####

# Use merge to combine the data frames based on the "MESS_DATUM" and "date" columns
merged_df <- merge(bike_df, weather_df_daily)

date_col_idx <- which(names(merged_df) == "date")
merged_df[, -date_col_idx] <- sapply(merged_df[, -date_col_idx], as.numeric)

first_date <- min(merged_df$date)
last_date <- max(merged_df$date)
fname <- paste0(first_date, "_to_", last_date, "_KA_bike_data.csv")
write.csv(merged_df, fname, row.names = FALSE)