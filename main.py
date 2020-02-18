def read_users_input_of_coordinate(coordinate: str) -> bool or str:
    """
    Returns True if he input of coordinate is correct and
    returns "Error" if the input of coordinate is uncorrect.
    If in users input is only lat or long it returns "Missing lat or long"

    >>> read_users_input_of_coordinate("49.83826, 24.02324")
    True
    >>> read_users_input_of_coordinate("49.83826")
    'Missing lat or long'
    >>> read_users_input_of_coordinate("34t")
    'Error'
    """
    if (len(coordinate) >= 16) and (("," in coordinate) and
                                    (coordinate.count(".") == 2)):
        return True
    if "." not in coordinate:
        return "Error"
    if len(coordinate) == 8:
        return "Missing lat or long"
    return "Error"


def give_lat_of_coordinate(coordinate: str) -> str:
    """
    Returns lat from whole coordinate.

    >>> give_lat_of_coordinate("49.83826, 24.02324")
    '49.83826'
    """
    index = coordinate.find(",")
    return coordinate[:index].strip()


def give_long_of_coordinate(coordinate: str) -> str:
    """
    Returns long from whole coordinate.

    >>> give_long_of_coordinate("49.83826, 24.02324")
    '24.02324'
    """
    index = coordinate.find(",")
    return coordinate[index+1:].strip()


def read_location_list(path: str, year: int) -> str:
    """
    Takes from file with location all location, that are
    connected with given year.

    >>> read_location_list("locations.list", 2017).head(2)
                    0           1     2
    12      Nashville   Tennessee   USA
    23  New York City    New York   USA
    """
    import pandas as pd
    data = pd.read_fwf(path)
    n = 'CRC: 0xCF86E85D  File: locations.list  Date: Fri Dec 22 00:00:00 2017'
    new = data[n].str.split("(", n=1, expand=True)
    new = new.drop(new.index[0:7])
    years = new[1].str.split(")", n=1, expand=True)
    places = years[1].str.split("}", n=1, expand=True)
    frame = {"year": years[0], "place": places[0]}
    frame1 = {"year": years[0], "place": places[1]}
    result = pd.DataFrame(frame)
    result["place"] = result["place"].str.strip()
    result = result[result["place"].str.contains("{") == False]
    result1 = pd.DataFrame(frame1)
    result1["place"] = result1["place"].str.strip()
    final = result.append(result1).dropna(axis=0, subset=["place"])
    final["place"] = final["place"].str.replace("}", "")
    final["place"] = final["place"].str.replace("(on location)", "")
    final["place"] = final["place"].str.replace("\t()", "")
    final["place"] = final["place"].str.strip()
    return (final[final["year"] == str(year)].dropna())["place"].str.split(",",
                                                            n=2, expand=True)


def sort_data(data: str) -> str:
    """
    Returns sorted data

    """
    data[2] = data[2].str.replace("()", "")
    return data.sort_values(2).dropna()


def read_coodinate_list(path: str) -> str:
    """
    Reads the file with places and coordinates.

    """
    import pandas as pd
    data = pd.read_csv(path)
    n = "country\tcity_ascii\tlat\tlng"
    new = data[n].str.split("\t", n=2, expand=True)
    new[2] = new[2].str.replace("\t", ", ")
    return new


def create_list_with_coordinates(data: str) -> list:
    """
    Creates list with coordinates
    """
    lst = []
    for i in data[2]:
        lst.append(i)
    return lst


def place_from_coordinate(coordinate: str, data: str) -> str:
    """
    Returns place of users coordinate.

    >>> data = read_coodinate_list("city_coordinates.tsv")
    >>> place_from_coordinate("19.4424, -99.1310", data)
    'Mexico'
    """
    s = str(data[data[2] == coordinate][0])
    index = s.find("  ")
    index1 = s.find("\n")
    return s[index:index1].strip()


def fixed_list(data: str, city: str) -> str:
    """
    Sort dataframe by cities from user.

    """
    return data[data[2].str.contains(city) == True].head(10)


def generate_coordinate(data: str) -> dict:
    """
    Adds new column with coordinates of cities.
    """
    key = "16944410e94240bfab0c9270ef4a3b3a"
    from opencage.geocoder import OpenCageGeocode
    geocoder = OpenCageGeocode(key)
    lst = []
    for index, row in data.iterrows():
        query = row[2]
        result = geocoder.geocode(query)
        lat = str(result[0]['geometry']['lat'])
        lng = str(result[0]['geometry']['lng'])
        lst.append(lat + ", " + lng)
    data["coordination"] = lst
    return data


def counties_read(path: str) -> str:
    """
    Reads file with information about countries.
    """
    import pandas as pd
    data = pd.read_fwf(path)
    new = data["0"].str.split("|", n=2, expand=True)
    return new


def generate_map(coordinate: list, zoom: int, data: str, data1: str):
    """
    Creates the HTML file with map.

    """
    import folium
    new_coordinate = []
    for i in coordinate:
        new_coordinate.append(float(i))
    map = folium.Map(location=new_coordinate, default_zoom_start=zoom)
    your_location = folium.FeatureGroup(name="Your place")
    your_location.add_child(folium.Marker(
        location=coordinate,
        popup="Your location: {}.\nWelcome to a beautiful place".format(
            ",".join(coordinate)), icon=folium.Icon()))
    fg = folium.FeatureGroup(name='Films')
    for i in range(len(data)):
        x = data.iloc[i]["coordination"].split(",")
        new_x = []
        for k in x:
            new_x.append(float(k))
        fg.add_child(folium.Marker(location=new_x,
                       popup="Here the film was directed"))
    ft = folium.FeatureGroup(name="Countries")
    for i in range(len(data1)):
        x = data1.iloc[i][1].split(",")
        new_x = []
        for t in x:
            new_x.append(float(t))
        ft.add_child(folium.CircleMarker(location=new_x, radius=20,
                            popup="One of the biggest countries in Europa",
                            line_color="#3186cc",
                            fill_color='#3186cc'))
    map.add_child(your_location)
    map.add_child(fg)
    map.add_child(ft)
    map.add_child(folium.LayerControl())
    map.save("Map_2.html")
    return ""


if __name__ == "__main__":
    # import doctest
    # doctest.testmod()
    import random
    year = int(input("Please enter a year you would like to have a map: "))
    coordinate = input("Please enter your location (format: lat, long): ")
    if read_users_input_of_coordinate(coordinate) == True:
        print("Map is generating...\nPlease wait...")
        lst = create_list_with_coordinates(read_coodinate_list("city_coordinates.tsv"))
        if coordinate not in lst:
            coordinate = lst[random.randint(1, len(lst))]
        data = sort_data(read_location_list("locations.list", year))
        coordinates_list = read_coodinate_list("city_coordinates.tsv")
        country = place_from_coordinate(coordinate, coordinates_list)
        list_of_coordinate = []
        list_of_coordinate.append(give_lat_of_coordinate(coordinate))
        list_of_coordinate.append(give_long_of_coordinate(coordinate))
        data = generate_coordinate(fixed_list(data, country))
        data1 = counties_read("Europa")
        generate_map(list_of_coordinate, 100, data, data1)
    else:
        print(read_users_input_of_coordinate(coordinate))

