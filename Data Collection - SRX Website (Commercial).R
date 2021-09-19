# Scrape commercial buildings on SRX

## Libraries 
library(rvest)
library(dplyr)
library(stringr)

##------------------------Extract property type links-------------------------##
# Establish connection
main.url <- "https://www.srx.com.sg"
main.page <- read_html(main.url)
commercial.links <- main.page %>% html_nodes("#property-types-commercial") %>%
  html_nodes("a") %>% html_attr("href")
closeAllConnections()

##----------------------Extract property listing links------------------------##
property.links <- c()

for (commercial.link in commercial.links)
{
  # Establish connection 
  url <- paste0(main.url, commercial.link)
  page <- read_html(url)
  
  # Total number of pages
  page.numbers <- page %>% html_nodes(".disabled+ li a") %>% html_text()
  last.page <- as.numeric(page.numbers[-1]) 
  
  # Iterate through each page
  for (i in 1:last.page)
  {
    commercial.url <- paste0(url, "&page=", i)
    commercial.page <- read_html(commercial.url)
    property.links <- c(property.links, commercial.page %>% html_nodes(".listingPhoto") %>%
                          html_attr("href"))
    closeAllConnections()
  }
}

##---------------------Extract property listing details-----------------------##

df.raw <- data.frame()

# Iterate through each link
for (property.link in property.links)
{
  # Establish connection
  property.url <- paste0(main.url, property.link)
  property.page <- read_html(property.url)
  
  # "About this property"
  keys <- c()
  main.key <- property.page %>% html_nodes(".listing-about-main-key") 
  for (key in main.key) {keys <- c(keys, key %>% html_text())}
  values <- c()
  main.value <- property.page %>% html_nodes(".listing-about-main-value")
  for (value in main.value) {values <- c(values, value %>% html_text())}
  about.property <- t(data.frame(values))
  colnames(about.property) <- keys
  
  # Facility
  facility.listing <- property.page %>% html_nodes(".listing-about-facility-span")
  facility <- length(facility.listing)
  
  # Transport
  train.listing <- property.page %>% html_nodes(".Trains .listing-amenity-name")
  train <- length(train.listing)
  bus.listing <- property.page %>% html_nodes(".listing-amenity-bus")
  bus <- length(unique(bus.listing))
  
  # Schools 
  school.listing <- property.page %>% html_nodes(".Schools .listing-amenity-name")
  school <- length(school.listing)
  
  # Shopping malls 
  shoppingmall.listing <- property.page %>% html_nodes(".Shopping-Malls .listing-amenity-name")
  shopping.mall <- length(shoppingmall.listing)
  
  # Markets
  market.listing <- property.page %>% html_nodes(".Markets .listing-amenity-name")
  market <- length(market.listing)
  
  # Combine all data frames
  df.property <- cbind(about.property, Facility=facility, 
                       Train=train, Buses=bus, Schools=school, Shopping.Mall=shopping.mall, 
                       Markets=market)
  df.raw <- merge(df.raw, df.property, all=TRUE)
  
  # Sleep
  Sys.sleep(sample(1:5, 1, replace=TRUE))
  closeAllConnections()
}

# Export data 
write.csv(df.raw, "./Data/Commercial_Raw.csv")
