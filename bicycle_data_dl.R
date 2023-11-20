rm(list = ls())
 v = getwd()

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Load Packages ####
library(httr)
library(dplyr)
library(ggplot2)
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
## Plots ####

plot(bike_df, type = "l")

# Look at 2018, 2019 since there is a large outlier in summer 2018
df_1819 <- subset(bike_df, date >= as.Date("2018-01-01") & date <= as.Date("2019-12-31"))

ggplot(df_1819, aes(x = date, y = bike_count)) +
    geom_line() +
    labs(x = "Date", y = "Count", title = "") +
    theme_minimal() + 
    scale_x_date(date_breaks = "months", date_labels = "%b %g", expand = c(0, 0)) +
    theme(axis.text.x = element_text(angle=60, hjust=1))

hist(bike_df$bike_count, breaks = 30, col = "lightblue", probability=TRUE,
     main = "Histogram with Density Curve", xlab = "Count")
lines(density(bike_df$bike_count), col="red", lw=2)

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
# link <- selectDWD(id=4177, res="hourly", var=vars_hourly, per="recent")
# weather_recent <- dataDWD(link, force=NA, varnames=TRUE, read=TRUE)
# 
# link <- selectDWD(id=4177, res="hourly", var=vars_hourly, per="historical")
# weather_historical <- dataDWD(link, force=NA, varnames=TRUE, read=TRUE)
# - - - - - - - - - 

link <- selectDWD(id=4177, res="daily", var=c("kl"), per=c("historical", "recent"))
weather_data <- dataDWD(link, force=NA, varnames=TRUE, read=TRUE)

historic_last_date <- max(weather_data[[1]]$MESS_DATUM)
bike_df_first_date <- as.POSIXct(min(bike_df$date))

historic_weather_data <- weather_data[[1]][weather_data[[1]]$MESS_DATUM > bike_df_first_date, ]
recent_weather_data <- weather_data[[2]][weather_data[[2]]$MESS_DATUM > historic_last_date, ]

combined_df <- rbind(historic_weather_data, recent_weather_data)
combined_df$MESS_DATUM <- as.Date(combined_df$MESS_DATUM)

# Columns to keep
columns_to_keep <- c("MESS_DATUM", "FX.Windspitze", "FM.Windgeschwindigkeit", 
                     "RSK.Niederschlagshoehe", "RSKF.Niederschlagsform", 
                     "SDK.Sonnenscheindauer", "SHK_TAG.Schneehoehe",
                     "NM.Bedeckungsgrad", "TMK.Lufttemperatur", "UPM.Relative_Feuchte",
                     "TXK.Lufttemperatur_Max", "TNK.Lufttemperatur_Min", 
                     "TGK.Lufttemperatur_5cm_min"
)
combined_df_subset <- combined_df[, columns_to_keep, drop = FALSE]

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Additional Features ####

# - - - - - - - - -
# add weekday ( 1 = Monday, ... , 7 = Sunday )

weekdays_list <- c("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
bike_df$weekday <- match(weekdays(bike_df$date), weekdays_list)

bike_df$is_weekend <- as.integer(bike_df$weekday %in% c(6, 7))

# - - - - - - - - -
# add public holiday

country <- "DE"
years <- unique(format(bike_df$date, "%Y"))

holiday_df_all <- data.frame()

for (year in years) {
    
    url <- paste0("https://date.nager.at/api/v3/PublicHolidays/",year,"/",country)
    
    # Make a GET request to the URL and read the response content
    response <- GET(url)
    data_text <- content(response, "text")
    
    # remove start and end sqr brackets []
    # also remove first and last curly brackets {}
    txt <- substr(data_text, start=3, stop = nchar(data_text)-2)
    
    # remove all quotation marks and backslashes
    txt <- gsub('[\\"]', '', txt)
    
    # separate into rows
    rows <- unlist(strsplit(txt, "\\},\\{"))
    
    holiday_df_yr <- data.frame(date = NA)
    for (row_idx in 1:length(rows)) {
        
        # take only the date which is the relevant info
        date <- unlist(strsplit(unlist(strsplit(rows[row_idx], ","))[1], ":"))[2]
        holiday_df_yr[row_idx,] <- date
    }
    
    holiday_df_all <- rbind(holiday_df_all, holiday_df_yr)
}

holiday_df_all$date <- as.Date(holiday_df_all$date)

# Create a new column "is_holiday" in merged_df
bike_df$is_holiday <- as.integer(bike_df$date %in% holiday_df_all$date)

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Merge Data & Save ####

# Use merge to combine the data frames based on the "MESS_DATUM" and "date" columns
merged_df <- merge(bike_df, combined_df_subset, by.y = "MESS_DATUM", by.x = "date", all.y = TRUE)

date_col_idx <- which(names(merged_df) == "date")
merged_df[, -date_col_idx] <- sapply(merged_df[, -date_col_idx], as.numeric)

first_date <- min(merged_df$date)
last_date <- max(merged_df$date)
fname <- paste0(first_date, "_to_", last_date, "_KA_bike_data.csv")
write.csv(merged_df, fname, row.names = FALSE)

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
## Plots ####

merged_df_nodate <- merged_df[, -which(names(merged_df) == "date")]

# library(corrplot)
# cor_matrix <- cor(merged_df_nodate)
# corrplot(cor_matrix, method = "circle", type = "upper", tl.col = "black", tl.srt = 45)

library(GGally)

corr_plot <- ggcorr(merged_df_nodate, label=TRUE, label_size=3, label_round=2, 
                    max_size=10, min_size=2, size=3, angle=0, hjust=0.6, nbreaks=7) +
    theme(
        legend.position = "bottom",  # Move the legend to the bottom
        legend.direction = "horizontal"  # Set the legend direction to horizontal
    ) +
    guides(fill = guide_legend(nrow = 1, byrow = TRUE, keywidth = unit(1, "cm")))

# param : nbreaks adds discrete colour levels

# Save the plot as a square PNG
ggsave(filename = "bikedata_corr_plot.png",
       plot = corr_plot, width=10, height=10)


