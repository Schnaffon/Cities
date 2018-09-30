from pymongo import MongoClient
from cities.utils import city_identification

client = MongoClient()
coll = client["cities"]["postal3"]


def index_postal():
    with open("/home/verene/cities2/allCountries.txt") as fichier:
        next_line = [""]
        line_number = 0
        while True:
            if next_line == [""]:
                try:
                    line = fichier.readline().split("\t")
                    line_number += 1
                except:
                    print("End of file")
                    return
                if line == [""]:
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
                    line_number += 1
                    if not line_number % 1000:
                        print("Reached line {}".format(line_number))
                except:
                    print("End of file")
                    return
                if next_line == [""]:
                    print("End of file")
                    return
                if len(next_line) < 3:
                    continue
                # if next_line[2] == city["name"]:
                city2 = {
                    "country code": next_line[0],
                    "postal codes": [next_line[1]],
                    "name": next_line[2],
                    "latitude": float(next_line[9]),
                    "longitude": float(next_line[10])
                }
                if city_identification(city, city2):
                    " It's actually the same city. Aggregate postal codes"
                    city["postal codes"].append(next_line[1])
                else:
                    break

            # Get country
            city["country"] = client["cities"]["countries"].find_one({"ISO": city["country code"]})['name']
            city.pop("country code")

            # save
            coll.insert_one(city)


if __name__ == "__main__":
    index_cities()
