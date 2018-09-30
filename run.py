import argparse

from cities import build_alternate_names_dict, add_postal_codes, add_population, clean_data, build_postal_codes_list, \
    build_countries_dictionary, send_to_algolia_index
from cities.config import ALTERNATE_NAMES_FILE, POPULATION_DIR, POSTAL_CODES_FILE, COUNTRIES_FILE

# Brief note. Only dictionaries are used here. That makes this impossible to apply on large datasets (for RAM is finite)
# I first did this using pymongo instead of dicitonaries. It was really slow so, I settled for dictionaries instead.
# But everything here can be done using database.

# There's a bash script to download all required files. Please felle free to use it

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--algolia_index', metavar='N', type=str, help = 'the algolia index')
    args = parser.parse_args()

    countries = build_countries_dictionary(COUNTRIES_FILE)
    postal_codes = build_postal_codes_list(countries, POSTAL_CODES_FILE)
    alternate_names = build_alternate_names_dict(ALTERNATE_NAMES_FILE)
    cities_dictionary = clean_data(add_postal_codes(add_population(alternate_names, countries, POPULATION_DIR), postal_codes))

    if args.algolia_index:
        send_to_algolia_index(cities_dictionary, args.algolia_index)
