# First attempt at indexing the cities
# This was meant to fail as I had not seen the file containing postal codes
# I  used mongodb thinking the dataset may be too heavy to work with dictionaries

from pymongo import MongoClient, errors
from tqdm import tqdm
import os

from cities.utils import location_identification


def index_cities():
    client = MongoClient()

    coll = client["cities"]["cities"]

    for file in tqdm(os.listdir("/home/verene/cities/unzipped")):
        with open("/home/verene/cities/unzipped/" + file, 'r') as fichier:
            for line in tqdm(fichier):
                city = {}
                try:
                    # Building the City Object
                    splitline = line.split("\t")
                    country = client["cities"]["countries"].find_one({"ISO": splitline[8]})['name']
                    city = {
                        "geoname_id": splitline[0],
                        "name": splitline[1],
                        # "asciiname": splitline[2],
                        "alternatenames": splitline[3].split(','),
                        "latitude": float(splitline[4]),
                        "longitude": float(splitline[5]),
                        # "feature class": splitline[6],
                        # "feature code": splitline[7],
                        'country code': splitline[8],
                        # "cc2": splitline[9],
                        # "admin1-code": splitline[10],
                        # "admin2 code": splitline[11],
                        # "admin3 code": splitline[12],
                        # "admin4 code": splitline[13],
                        "population": int(splitline[14]),
                        # "elevation": splitline[15],
                        # "dem": splitline[16],
                        "timezone": splitline[17],
                        # "modification date": splitline[18],

                    }
                except:
                    print("Could not parse line {} in file {}".format(line, file))
                    continue

                # If the population is null, drop the city (it seems that most cities that don't have a population are..well.. not cities
                if not city["population"]:
                    continue

                # If the name of the city is too long, it may also not be a city ( the city with the longest name is called
                # Llanfair­pwll­gwyn­gyll­go­gery­chwyrn­drobwll­llan­tysilio­gogo­goch and that makes 58 chars
                if len(city["name"]) > 60:
                    continue

                # Match with a country (to have the country name)
                try:
                    city["country"] = client["cities"]["countries"].find_one({"ISO": city["country code"]})['name']
                    city.pop("country code")
                except:
                    print("no country")

                # Add a correct postcode
                # TODO : Find postcodes (I can't find any)
                city["postcode"] = ""

                # Check that the city does not already exist
                # A city will be defined by two elements : its name and its location.
                # If two cities are too much alike, it's assumed they are the same city
                # Check for similar names
                for name in city["name"].split(" "):
                    if len(name) > 3:
                        regex = ".*{}.*".format(name)
                        for other_city in coll.find({"name": {"$regex": regex}}):
                            if location_identification(other_city["population"], (other_city["latitude"], other_city["longitude"]), (city["latitude"], city["longitude"])):
                                # If these two cities are actually one, we'll assume population is always growing, so the highest population should be the most recent record
                                if city["population"] >= other_city["population"]:
                                    continue
                                else:
                                    try:
                                        coll.delete_one({"_id": other_city["_id"]})
                                        break
                                    except errors.DuplicateKeyError as e:
                                        print(regex)
                                        print(city)
                                        print(other_city)
                                        raise errors.DuplicateKeyError(e)

                else:
                    try:
                        coll.insert_one(city)
                    except errors.DuplicateKeyError as e:
                        print(city)
                        raise errors.DuplicateKeyError(e)

