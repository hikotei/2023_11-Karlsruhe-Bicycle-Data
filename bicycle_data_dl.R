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

# remove quotation marks and backslashes
test <- gsub('["\\]', '', data_text)
# split rows by comma and square brackets
rows <- unlist(strsplit(test, "\\],\\["))

# save in dataframe
data <- data.frame(date = NA, count = NA)
for(i in 1:length(rows)){
    data[i,] <- unlist(strsplit(rows[i], ","))
}

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Plots ####

df <- data.frame(date = as.Date(data$date, format = "%m/%d/%Y"), 
                 count = as.numeric(data$count))
head(df)

plot(df, type = "l")
plot(df, type = "h")
