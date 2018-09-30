# Second attempt.
# Using pymongo was really slow. I quit...

from pymongo import MongoClient
from cities.utils import send_batch

client = MongoClient()

def index_cities():
    with open("/home/verene/cities2/allCountries.txt") as fichier:
        batch = []
        next_line = None
        while True:
            if not next_line:
                try:
                    line = fichier.readline().split("\t")
                except:
                    print("End of file")
                    return
            else:
                line = next_line
            city = {
                "country code": line[0],
                "postal codes": [line[1]],
                "name": line[2],
                "latitude": float(line[9]),
                "longitude": float(line[10])
            }

            # Get all postal codes
            while True:
                try:
                    next_line = fichier.readline().split("\t")
                except:
                    print("End of file")
                    return
                if next_line[2] == city["name"]:
                    " It's actually the same city. Aggregate postal codes"
                    city["postal codes"].append(next_line[1])
                else:
                    break

            # Get country
            city["country"] = client["cities"]["countries"].find_one({"ISO": city["country code"]})['name']

            # Get population
            city_equivalent = client["cities"]["population"].find_one({"_id": "{}-{}".format(city["country code"], city["name"])})
            if city_equivalent:
                city["population"] = city_equivalent["population"]

                # Get alternate name
                alternate = client["cities"]["alternate_names"].find_one({"geoname_id": city_equivalent["geoname_id"]})
                if alternate:
                    city["alternate names"] = alternate["alternate names"]
                else:
                    print("No alternate names for city {}".format(city))
            else:
                print("No population for city {}".format(city))



            city.pop("country code")

            batch.append(city)

            if len(batch) > 100:
                send_batch(batch)
                batch = []