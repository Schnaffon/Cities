from pymongo import MongoClient

def index_countries():

    client = MongoClient()

    coll = client["cities"]["countries"]

    with open("/home/verene/cities/countryInfo.txt") as fichier:
        for line in fichier:
            try:
                splitline = line.split("\t")
                mongoobject = {
                    "name": splitline[4],
                    "ISO": splitline[0]

                }
                coll.insert_one(mongoobject)
            except:
                print("Line {} from file {} could not be parsed".format(line, "/home/verene/cities/countryInfo.txt"))
