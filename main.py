from dotenv import load_dotenv
from requests import post
import base64
import json
import os

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    # encode client_id and client_secret to base64
    auth_string = client_id + ":" + client_secret
    auth_encoded = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_encoded), "utf-8")

    # setup URL, headers and data for POST request
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }

    # send POST request
    result = post(url, headers=headers, data=data)

    # convert json to python dictionary
    json_result = json.loads(result.content)
    token = json_result["access_token"]

    return token

token = get_token()