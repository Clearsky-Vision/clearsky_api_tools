from datetime import datetime, timedelta

from user import User
from tile_API.search_tile_api import Query, search_data
from tile_API.download_tile_api import download_all

# download all files in search to data_path_out
def example_1():

    credentials = User(api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

    data_path_out = "C:/cs/"
    show_progress = True # progress bar for each download

    from_date = datetime(year=2022, month=7, day=20)
    to_date = datetime(year=2022, month=7, day=22)
    bounding_box = "POLYGON((8.80615204775664 56.57718163398507,9.59716767275664 56.57718163398507,9.59716767275664 56.077701725344184,8.80615204775664 56.077701725344184,8.80615204775664 56.57718163398507))"

    while from_date < to_date:

        query = Query(bounding_box, str(from_date).split(" ")[0] +"T00:00:00Z", str(from_date).split(" ")[0] +"T00:00:00Z")

        search_results = search_data(credentials, query)
        if not isinstance(search_results, list):
            print(str(search_results))
        else:
            download_all(search_results, data_path_out, credentials, show_progress)
            from_date += timedelta(days=1)

    print("done")



if __name__ == '__main__':
    example_1() # Download tiles
