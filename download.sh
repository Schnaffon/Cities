#!/usr/bin/env bash

# Countries
wget -q http://download.geonames.org/export/zip/countryInfo.txt -O ./data/countryInfo.txt

# Population
wget -q http://download.geonames.org/export/dump/allCountries.zip -O ./data/population/allCountries.zip
unzip ./data/population/allCountries.zip -d ./data/population
rm ./data/population/allCountries.zip

wget -q http://download.geonames.org/export/dump/cities1000.zip  -O ./data/population/cities1000.zip
unzip ./data/population/cities1000.zip -d ./data/population
rm ./data/population/cities1000.zip

wget -q http://download.geonames.org/export/dump/cities15000.zip -O ./data/population/cities15000.zip
unzip ./data/population/cities15000.zip -d ./data/population
rm ./data/population/cities15000.zip

wget -q http://download.geonames.org/export/dump/cities5000.zip  -O ./data/population/cities5000.zip
unzip ./data/population/cities5000.zip -d ./data/population
rm ./data/population/cities5000.zip

# Alternate names

wget -q http://download.geonames.org/export/dump/alternateNamesV2.zip  -O ./data/alternateNamesV2.zip
unzip ./data/alternateNamesV2.zip -d ./data
rm ./data/alternateNamesV2.zip


# Postal Codes

wget -q http://download.geonames.org/export/zip/allCountries.zip -O ./data/allCountries.zip
unzip ./data/allCountries.zip -d ./data
rm ./data/allCountries.zip