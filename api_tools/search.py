import requests

class Query():
    def __init__(self, bounding_box, start_date, end_date):
        self.bounding_box = bounding_box
        self.start_date = start_date
        self.end_date = end_date


def search_data(credentials, query):

    try:
        data_str = {"BoundingBoxWkt": query.bounding_box, "From": query.start_date, "Until": query.end_date}

        req = requests.post("https://api.clearsky.vision/api/satelliteimages/boundingbox/", json=data_str, timeout=200,headers={"X-API-KEY":credentials.api_key})
        print(f"Status Code: {req.status_code})#, Response: {req.json()}")
        if req.status_code == 200:
            return req.json()['Data']
        else:
            return req

    except Exception as E:
        return str(E)
