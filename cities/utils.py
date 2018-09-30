def location_identification( loc1: tuple, loc2: tuple):
    """Checks if two cities are close enough to assume they're one"""

    return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1]) < 0.5


def city_identification(city1, city2):
    if city1["name"] in city2["name"]:
        return location_identification((city1["latitude"], city1["longitude"]), (city2["latitude"], city2["longitude"]))
    if city2["name"] in city1["name"]:
        return location_identification((city1["latitude"], city1["longitude"]), (city2["latitude"], city2["longitude"]))

    return False


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


def fusion(staying_city, additional_city):
    if staying_city["population"] < additional_city["population"]:
        staying_city["population"] = additional_city["population"]
        staying_city["geoname_id"] = additional_city["geoname_id"]
    staying_city["alternate names"].update(additional_city["alternate names"])

