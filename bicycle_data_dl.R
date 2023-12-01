rm(list = ls())
 v = getwd()

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Load Packages ####
library(httr)
library(dplyr)
library(rdwd)

library(ggplot2)
library(GGally)
library(corrplot)
 
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

# - - - - - - - - - 
# plot all years since 2012

plot(bike_df, type="l")

# - - - - - - - - - 
# Look at 2018, 2019 since there is a large outlier in summer 2018

year <- 2020
df_yearly <- subset(bike_df, date >= as.Date(paste0(year, "-01-01")) & date <= as.Date(paste0(year+1, "-01-01")))

marg <- 20
ggplot(df_yearly, aes(x = date, y = bike_count)) +
    geom_line() +
    labs(x = "Date", y = "Count", title = "") +
    theme_minimal() + 
    scale_x_date(date_breaks = "months", date_labels = "%b %g", expand = c(0, 0)) +
    theme(axis.text.x = element_text(angle=60, hjust=1), 
          plot.margin = margin(marg, marg, marg, marg, "pt"))

# - - - - - - - - - 
## model fitting [JUST FOR FUN] ####

df_yearly$week <- as.numeric(format(df_yearly$date, "%U"))

weekdays_list <- c("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
df_yearly$weekday <- match(weekdays(df_yearly$date), weekdays_list)
df_yearly$is_weekend <- as.integer(df_yearly$weekday %in% c(6, 7))

cutoff <- 14
plot(df_yearly$date[1:cutoff], df_yearly$bike_count[1:cutoff], type = "l")

weekly_data <- df_yearly %>% group_by(week) %>%
    summarise(weekly_max = max(bike_count),
              weekly_min = min(bike_count),
              weekly_amp = weekly_max-weekly_min) 

amplitude_pattern <- rep(weekly_data$weekly_amp, each=7)[1:length(df_yearly$date)]
shift_pattern <- rep(weekly_data$weekly_min, each=7)[1:length(df_yearly$date)]

x_range <- seq(0,(length(df_yearly$date)-1))
phase <- df_yearly$weekday[1] # number of days past monday of first day of year
period <- 14
freq <- 1 / period
y_vals <- abs(sin((x_range+phase)*2*pi*freq)) * amplitude_pattern + shift_pattern

cutoff <- 366
# Plot the original time series and the fitted values
plot(df_yearly$date[1:cutoff], df_yearly$bike_count[1:cutoff], type = "l", col='blue',
     lwd = 2, ylab = "Bike Count", xlab = "Timestamp", 
     main = "Original (blue) vs. Fitted (red) Time Series")
lines(df_yearly$date[1:cutoff], y_vals[1:cutoff], col = "red", lwd = 2)

# - - - - - - - - - 
# Histogram Plot

png("histogram_plot.png", width = 800, height = 600)

hist(bike_df$bike_count, breaks = 30, col = "lightblue", probability=TRUE,
     main = "Histogram with Density Curve", xlab = "Count")
lines(density(bike_df$bike_count), col="red", lw=2)

dev.off()

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
# Additional Features ####

# - - - - - - - - -
# add weekday ( 1 = Monday, ... , 7 = Sunday )

# create new df to keep old one untouched
bike_and_holiday <- data.frame(bike_df)

weekdays_list <- c("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
bike_and_holiday$weekday <- match(weekdays(bike_and_holiday$date), weekdays_list)
bike_and_holiday$is_weekend <- as.integer(bike_and_holiday$weekday %in% c(6, 7))

# - - - - - - - - -
# add public holiday

country <- "DE"
years <- unique(format(bike_and_holiday$date, "%Y"))

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

# save all holidays as date format in df
holiday_df_all$date <- as.Date(holiday_df_all$date)

# Create a new column "is_holiday" in bike_and_holiday df
bike_and_holiday$is_holiday <- as.integer(bike_df$date %in% holiday_df_all$date)

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Merge Data & Save ####

# Use merge to combine the data frames based on the "MESS_DATUM" and "date" columns
merged_df <- merge(bike_and_holiday, weather_df_daily)

date_col_idx <- which(names(merged_df) == "date")
merged_df[, -date_col_idx] <- sapply(merged_df[, -date_col_idx], as.numeric)

first_date <- min(merged_df$date)
last_date <- max(merged_df$date)
fname <- paste0(first_date, "_to_", last_date, "_KA_bike_data.csv")
write.csv(merged_df, fname, row.names = FALSE)

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
## Plots ####

merged_df_nodate <- merged_df[, -which(names(merged_df) == "date")]

# - - - - - - - - -

cor_matrix <- cor(merged_df_nodate)
corrplot(cor_matrix, method = "circle", type = "upper", tl.col = "black", tl.srt = 45)

# - - - - - - - - -

# param : nbreaks adds discrete colour levels
corr_plot <- ggcorr(merged_df_nodate, label=TRUE, label_size=3, label_round=2, 
                    max_size=10, min_size=2, size=3, angle=0, hjust=0.6, nbreaks=10) +
    theme(
        legend.position = "bottom",  # Move the legend to the bottom
        legend.direction = "horizontal"  # Set the legend direction to horizontal
    ) +
    guides(fill = guide_legend(nrow = 1, byrow = TRUE, keywidth = unit(1, "cm"))); corr_plot

# Save the plot as a square PNG
ggsave(filename = "bikedata_corr_plot.png",
       plot = corr_plot, width=10, height=10)

# - - - - - - - - -

# Extract correlation values for bike_count
bike_corr <- cor(merged_df_nodate)[,"bike_count"]

# Ignore correlation with itself
bike_corr <- bike_corr[-1]

# Create a data frame for ggplot
cor_data <- data.frame(variable = names(bike_corr), correlation = bike_corr)

marg <- 20

# Create a horizontal bar chart with ggplot2
ggplot(cor_data, aes(y = reorder(variable, correlation), x = correlation, fill = abs(correlation))) +
    geom_bar(stat = "identity", position = "identity") +
    scale_fill_gradient(low = "grey80", high = "lightblue", guide = "none") +  # Remove the colorbar legend
    labs(title = "Correlation of variables with bike_count",
         x = "Correlation Coefficient",
         y = NULL) +  # Remove y-axis label
    theme_minimal() +
    theme(axis.text.y = element_text(angle = 0, vjust = 0.5, hjust = 0.5),
          plot.margin = margin(marg, marg, marg, marg, "pt"))  # Adjust the values to add padding

# # Create a vertical bar (column) chart with ggplot2
# ggplot(cor_data, aes(x = reorder(variable, correlation), y = correlation, fill = abs(correlation))) +
#     geom_bar(stat = "identity", position = "identity") +
#     scale_fill_gradient(low = "grey80", high = "lightblue", guide = "none") +  # Remove the colorbar legend
#     labs(title = "Correlation of variables with bike_count",
#          y = "Correlation Coefficient",
#          x = NULL) +  # Remove x-axis label
#     theme_minimal() +
#     theme(axis.text.x = element_text(angle=90, vjust=0.5, hjust=0.5),
#           plot.margin = margin(marg, marg, marg, marg, "pt"))  # Adjust the values to add padding


