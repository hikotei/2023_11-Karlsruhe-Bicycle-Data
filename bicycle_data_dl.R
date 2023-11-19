# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Load necessary packages
library(httr)
library(dplyr)

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Get from URL ####

# Define the URL where your data is located
url <- "https://www.eco-visio.net/api/aladdin/1.0.0/pbl/publicwebpageplus/data/100126474?idOrganisme=4586&idPdc=100126474&interval=4&flowIds=100126474"

# Make a GET request to the URL and read the response content
response <- GET(url)
data_text <- content(response, "text")

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Data Processing ####

# remove first and last square brackets [ ... ]
txt <- substr(data_text, start=3, stop = nchar(data_text)-2)
# split rows by comma and square brackets
rows <- unlist(strsplit(txt, "\\],\\["))

# save in dataframe
data <- data.frame(date = NA, count = NA)
for(i in 1:length(rows)){
    
    # split each row into timestamp and value
    this_row_raw <- unlist(strsplit(rows[i], ","))
    
    # extract data from format ... "\"05/03/2012\"" 
    # by removing backslashes and quotation marks
    this_row <- c(gsub("\"", "", this_row_raw[1]),
                  gsub("\"", "", this_row_raw[2]))
    
    # save to dataframe
    data[i,] <- this_row
}

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Plots ####

df <- data.frame(date = as.Date(data$date, format = "%m/%d/%Y"), 
                 count = as.numeric(data$count))
head(df)

plot(df, type = "l")
plot(df, type = "h")
