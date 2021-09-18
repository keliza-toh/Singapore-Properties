# # SRX Property Listings
# This script aims to extract the details of property listings for residential properties on SRX. 

# Packages
import pandas as pd
import numpy as np
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver

#######################################################################################
#----------------------- Establish Connections with Home Page ------------------------#
#######################################################################################

main_url = "https://www.srx.com.sg"
main_page = requests.get(main_url)
main_soup = BeautifulSoup(main_page.content, "html.parser")
main_page.close()

#######################################################################################
#----------------------------- Obtain Housing Type Links -----------------------------#
#######################################################################################

residential_links = []
residential_main = main_soup.find("div", {"id":"property-types-residential"})
residential_hrefs = residential_main.find_all("a", href=True)
for href in residential_hrefs: 
    residential_links.append(href["href"])

#######################################################################################
#------------------------- Obtain Individual Property Links --------------------------#
#######################################################################################

# Looping through each property category
property_links = []
for residential_link in residential_links[0:3]: # Not including new launches (duplicated properties)
    
    # Establish connection
    page = requests.get(main_url + residential_link)
    soup = BeautifulSoup(page.content, "html.parser")
    page.close()
    page_numbers = soup.find(id="listingResultPagination").find_all("a")
    last_page = int(page_numbers[-2].text)
    
    # Iterating through pages
    for i in range(1, last_page + 1, 1): 
        # Establish connection with page
        residential_url = main_url + residential_link + "?page=" + str(i)
        residential_page = requests.get(residential_url)
        residential_soup = BeautifulSoup(residential_page.content, "html.parser")
        residential_page.close()
        # Extract url for property listing
        property_href = residential_soup.find_all("a", class_="listingPhoto", href=True)
        for href in property_href: 
            property_links.append(href["href"])
        # Sleep
        time.sleep(np.random.randint(1, 5))

# Remove duplicates 
property_links_unique = list(set(property_links))
# Create empty dataframe 
df_raw = pd.DataFrame()

#######################################################################################
#------------------------- Extract Property Listing Details --------------------------#
#######################################################################################

for proeprty_link in property_links_unique: 
    
    # Establish connection
    property_url = main_url + property_link
    property_page = requests.get(property_url)
    property_soup = BeautifulSoup(property_page.content, "html.parser")
    # Sleep
    time.sleep(np.random.randint(1, 5))
    property_page.close()
    # Create empty dictionary
    property_details = {}
    
    # "About this property"
    main_keys = property_soup.select(".listing-about-main-key")
    main_values = property_soup.select(".listing-about-main-value")
    keys = [key.text for key in main_keys]
    values = [value.text for value in main_keys]
    for i in range(0, len(keys)): 
        property_details[keys[i]] = values[i]
    
    # Facilities 
    facility_listings = property_soup.select(".listing-about-facility-span")
    property_details["Facility"] = len(facility_listings)
    
    # Transport
    train_listings = property_soup.select(".Trains .listing-amenity-name")
    property_details["Trains"] = len(train_listings)
    bus_listings = set(property_soup.select(".listing-amenity-bus"))
    property_details["Buses"] = len(bus_listings)
    
    # Schools 
    school_listings = property_soup.select(".Schools .listing-amenity-name")
    property_details["Schools"] = len(school_listings)
    
    # Shopping Malls 
    shoppingmall_listings = property_soup.select(".Shopping-Malls .listing-amenity-name")
    property_details["Shopping Malls"] = len(shoppingmall_listings)
    
    # Markets
    market_listings = property_soup.select(".Markets .listing-amenity-name")
    property_details["Markets"] = len(market_listings)
    
    # Convert details into dataframe and combine with final dataframe
    df_property = pd.DataFrame(property_details, index=[0])
    df_raw = pd.concat([df_raw, df_property], axis=0)
    
# Export results   
df_raw.to_csv("./Data/Residential_Raw.csv")