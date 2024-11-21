import models
from api_service import ClearSkyVisionAPI


def main():

    api_key = "###########              REPLACE WITH API KEY              ###########"

    api_service = ClearSkyVisionAPI(api_key)

    # Get information about API key
    apikey_info = api_service.get_api_key_info()

    pass


if __name__ == "__main__":
    main()
