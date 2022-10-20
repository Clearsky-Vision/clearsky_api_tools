from datetime import datetime, timedelta

from user import User
from tile_API.search_tile_api import Query, search_data
from tile_API.download_tile_api import download_all

# download all files in search to data_path_out
def example_1():

    credentials = User(api_key="XXXXXXXXXXX")

    data_path_out = "C:/test/"
    show_progress = True # progress bar for each download

    from_date = datetime(year=2019, month=3, day=1)
    to_date = datetime(year=2022, month=1, day=1)
    bounding_box = "POLYGON ((-57.183317017598405 -12.989665339677789, -56.71119347827542 -12.98956953775976, -56.71064817250214 -13.452542761230577, -57.18366314843131 -13.452642099473834, -57.183317017598405 -12.989665339677789))"

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
