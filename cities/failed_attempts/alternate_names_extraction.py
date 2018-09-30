from pymongo import MongoClient
from pymongo import errors as e

coll = MongoClient()["cities"]["alternate_names"]

def index_alternate_names():
    with open("/home/verene/cities2/alternateNamesV2/alternateNamesV2.txt") as fichier:
        next_line = None
        line_number = 0
        while True:
            if not next_line:
                try:
                    line_number +=1
                    line = fichier.readline().split("\t")
                    if len(line)<3:
                        continue
                except:
                    print("End of file")
                    return

            else:
                line = next_line
            city = {
                "_id": line[1],
                "alternate names": [line[3]]
            }

            while True:
                next_line = fichier.readline().split("\t")
                if not next_line:
                    print("End of file")
                    return
                line_number +=1
                if not line_number%10000:
                    print("Reached line {}".format(line_number))
                if len(next_line)<3:
                    continue
                if next_line[1] == city["_id"]:
                    # It's the same city, with another name
                    if next_line[3] not in city["alternate names"] and "wiki" not in next_line[3]:
                        city["alternate names"].append(next_line[3])

                else:
                    try:
                        coll.insert_one(city)
                    except e.DuplicateKeyError as err:
                        print("Error in alterate names. City {} can't be inserted because {}".format(city,  err))
                    else:
                        break






if __name__=="__main__":
    index_alternate_names()