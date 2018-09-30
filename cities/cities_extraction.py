import os
from tqdm import tqdm

from algoliasearch import algoliasearch, helpers

from .utils import hasNumbers, location_identification, fusion, city_identification

# For obvious reasons,  the config file won't be pushed
from .config import ALGOLIA_APP_ID


# Brief note. Only dictionaries are used here. That makes this impossible to apply on large datasets (for RAM is finite)
# I first did this using pymongo instead of dicitonaries. It was really slow so, I settled for dictionaries instead.
# But everything here can be done using database.

def build_alternate_names_dict(alternate_names_file):
    """This should build the first dictionary. It shall contain a series of names associated to a geoname_id key"""
    alternate_names_dict = {}
    with open(alternate_names_file) as alternate_names_file:
        for i, line in enumerate(alternate_names_file.readlines()):

            # Let's parse each line
            parse_line = line.split("\t")

            geocode = parse_line[1]
            name_type = parse_line[2]
            name = parse_line[3]

            # I decided not to use unlc. As for links... well, that was not usefull
            if name_type in ["link", "unlc"]:
                continue

            # This here is meant to aggregate cities with the same geoname_id.
            if geocode in alternate_names_dict:
                alternate_names_dict[geocode].add(name)
            else:
                alternate_names_dict[geocode] = set([name])

    return alternate_names_dict


def add_population(alternate_name_dict, countries, population_dir):
    """Once the alternate names dictioary is built, let's iterate on the files containing population information
    The jointure is made on geoname_id that should be unique
    This dictionary has a couple (country, city_name) for key
    To each key is associated a list of cities with the same name and same country"""

    with_population = {}
    # I used tqdm here but really it isn't necessary as I only had like 4 files. But anyway...
    for file in tqdm(os.listdir(population_dir)):
        with open(population_dir + file, 'r') as population_file:
            for line in population_file:

                # Building the City Object

                splitline = line.split("\t")

                # Some cities are not parsable and lack some fields. I just dropped them...
                if len(splitline) < 19:
                    continue

                city = {
                    "geoname_id": splitline[0],
                    # We could have kept these too to have more alternate names,
                    # but I figured that the alternatenames table was more reliable
                    # "alternatenames": splitline[3].split(','),

                    # As for this name2 I figured this name was more reliable than the rest and decided to keep it somewhere.
                    "name2": splitline[1],
                    "latitude": float(splitline[4]),
                    "longitude": float(splitline[5]),
                    'country code': splitline[8],
                    "population": int(splitline[14]),
                    "timezone": splitline[17],
                    "postal codes": set()
                }

                # Some cities didn't have any population indication. That was also not usefull here as I needed the population.
                if city["population"] == 0:
                    continue

                # Find country
                # print(city["country code"])
                try:
                    city["country"] = countries[city["country code"]]
                except KeyError as e:
                    print("Faulty city {}".format(city))
                    continue

                # Associate cities with their alternate_names counterpart
                # The common key here was geoname_id
                if city["geoname_id"] in alternate_name_dict:
                    city["alternate names"] = alternate_name_dict[city["geoname_id"]]

                    # Here we build the new dictionary structure
                    # (country, city_name): [{city}]
                    # I add an entry for each alternate name
                    for name in city["alternate names"]:
                        city["name"] = name

                        if (city["country"], name) not in with_population:
                            with_population[(city["country"], name)] = [city]
                        else:
                            # If the list already exists, I also check that the exact same city with the same name doesn't exists here
                            # There are a bunch of duplicates in there
                            # If it already exists I merge them
                            found = False
                            for same_name_city in with_population[(city["country"], name)]:
                                if location_identification((same_name_city['latitude'], same_name_city['longitude']),
                                                           (city['latitude'], city['longitude'])):
                                    fusion(same_name_city, city)
                                    found = True
                                    break
                            if not found:
                                with_population[(city["country"], name)].append(city)

    return with_population


def add_postal_codes(incomplete_dictionary, postal_codes_list):
    """Here we build the final dictionary
    Goal is to assemblate our cities with their postal codes
    Problem is : the postal codes file doesn't contain any geoname_id.
    I decided to join the two datasets based on the couple (country, city_name)
    It's not enough.
    To be sure I don't assemblate two totally different cities, I also check that's the same city based on location.
    The returned dictionary contains all cities with all the necessary information. Each is identified with a geoname_id as a key."""

    complete_dictionary = {}
    for postal in postal_codes_list:
        postal_id = (postal["country"], postal["name"])
        if postal_id in incomplete_dictionary:
            cities = incomplete_dictionary[postal_id]
            for i, city in enumerate(cities):
                if location_identification((postal["latitude"], postal["longitude"]),
                                           (city["latitude"], city["longitude"])):
                    city["postal codes"].update(set(postal["postal codes"]))
                    complete_dictionary[city["geoname_id"]] = city

    return complete_dictionary


def clean_data(cities_dictionary):
    """This function is meant to clean the resulting dictionary"""

    for city in cities_dictionary.values():
        new_alternate = []
        for alternate in city["alternate names"]:
            if not hasNumbers(alternate):
                new_alternate.append(alternate)
        if not hasNumbers(city["name2"]):
            city["name"] = city["name2"]
        else:
            try:
                city["name"] = new_alternate[0]
            except IndexError:
                continue
        city["alternate names"] = new_alternate

        city.pop("name2")

    print("Total : {}".format(len(cities_dictionary)))


def send_to_algolia_index(cities_dictionary, ALGOLIA_API_KEY):
    """This function has a self explatory title
    As for sending, it could have been done in batches to go faster, but the dataset here was
    small enough to allow me to do as I wished.
    As some cities where too big to be indexed, I decided to send them one by one to identify the ones that could not
    be inserted in the index and give them a second chance, hand made."""

    algolia_client = algoliasearch.Client(ALGOLIA_APP_ID, ALGOLIA_API_KEY)

    index = algolia_client.init_index('Cities3')

    for element in cities_dictionary.values():
        # I put the geoname_id as objectID. Not sur of this choice...
        geoname_id = element.pop('geoname_id')
        element["objectID"] = geoname_id
        element["alternate names"] = list(element["alternate names"])
        try:
            index.add_object(element)
        except helpers.AlgoliaException:
            print("Too big of an entry : {}".format(element))
            continue


def build_postal_codes_list(countries, postal_codes_file):
    """ This builds a dictionary ith the postal codes dataset.
    I first used pymongo to index everything (because I didn't want to this every time. And wanted to be able to search through the data.
    That's why this function is not as clean as the others.
    :return:
    """

    postal_codes_list = []
    with open(postal_codes_file) as postal_codes_file:
        next_line = [""]
        while True:
            if next_line == [""]:
                try:
                    line = postal_codes_file.readline().split("\t")
                except:
                    print("End of file")
                    return postal_codes_list
                if line == [""]:
                    return postal_codes_list
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
                    next_line = postal_codes_file.readline().split("\t")
                except:
                    print("End of file")
                    return postal_codes_list
                if next_line == [""]:
                    print("End of file")
                    return postal_codes_list
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
                    # It's actually the same city. Aggregate postal codes
                    city["postal codes"].append(next_line[1])
                else:
                    break

            # Get country
            city["country"] = countries[city["country code"]]
            city.pop("country code")

            # save
            postal_codes_list.append(city)


def build_countries_dictionary(countries_file):
    countries = {}

    with open(countries_file) as countries_file:
        for line in countries_file:
            try:
                splitline = line.split("\t")
                country = {
                    "name": splitline[4],
                    "ISO": splitline[0]

                }
                countries[country["ISO"]] = country["name"]
            except:
                print("Line {} could not be parsed".format(line))
    return countries
