from imgurpython import ImgurClient
from dotenv import dotenv_values


def authenticate():
    # Get client ID and secret from auth.ini
    config = dotenv_values(".env")
    client_id = config['CLIENT_ID']
    client_secret = config['CLIENT_SECRET']

    client = ImgurClient(client_id, client_secret)
    client.set_user_auth(config['access_token'], config['refresh_token'])
    print("Authentication successful!")

    return client