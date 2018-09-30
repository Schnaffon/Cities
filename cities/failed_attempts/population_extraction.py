import os
from tqdm import tqdm
from pymongo import MongoClient
from pymongo import errors as e


def index_cities():
    client = MongoClient()

    coll = client["cities"]["population"]

    for file in tqdm(os.listdir("/home/verene/cities2/population")):
        print(file)
        line_number = 0
        with open("/home/verene/cities2/population/" + file, 'r') as fichier:
            for line in fichier:
                line_number +=1
                if not line_number%1000:
                    print("Reached line {}".format(line_number))
                city = {}
                try:
                    # Building the City Object
                    splitline = line.split("\t")
                    if len(splitline)<19:
                        continue
                    city = {
                        "geoname_id": splitline[0],
                        "name": splitline[1],
                        # We could have kept these too to have more alternate names, but I figured that the alternatenames table was more reliable
                        #"alternatenames": splitline[3].split(','),
                        "latitude": float(splitline[4]),
                        "longitude": float(splitline[5]),
                        'country code': splitline[8],
                        "population": int(splitline[14]),
                        "timezone": splitline[17],
                    }
                except:
                    print("Could not parse line {} in file {}".format(line, file))
                    continue

                city["_id"] = "{}-{}".format(city["country code"], city["name"])
                try:
                    coll.insert_one(city)
                except e.DuplicateKeyError:
                    existing_city = coll.find_one({"_id": city["_id"]})
                    if existing_city["population"] < city["population"]:
                        coll.delete_one({"_id": city["_id"]})
                        coll.insert_one(city)




if __name__=="__main__":
    index_cities()