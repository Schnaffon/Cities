from cities import build_alternate_names_dict, add_postal_codes, add_population, clean_data, build_postal_codes_list, \
    build_countries_dictionary, send_to_algolia_index

# Brief note. Only dictionaries are used here. That makes this impossible to apply on large datasets (for RAM is finite)
# I first did this using pymongo instead of dicitonaries. It was really slow so, I settled for dictionaries instead.
# But everything here can be done using database.

if __name__ == "__main__":
    countries = build_countries_dictionary()
    postal_codes = build_postal_codes_list(countries)
    alternate_names = build_alternate_names_dict()
    cities_dictionary = clean_data(add_postal_codes(add_population(alternate_names, countries), postal_codes))
    # send_to_algolia_index(cities_dictionary)
