from dotenv import load_dotenv
from requests import post, get
import base64
import json
import os

# load environment variables
load_dotenv()
# get environment variables and assign to variables
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

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    # setup URL and headers for GET request
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    # encode artist_name to url format
    query = f"?q={artist_name}&type=artist&limit=1"
    # combine url and query
    query_url = url + query
    # send GET request
    result = get(query_url, headers=headers)
    # convert json to python dictionary
    json_result = json.loads(result.content)["artists"]["items"]
    # check if artist was found
    if len(json_result) == 0:
        print("No artist found")
        return None
    else: 
        return json_result[0]

def get_songs_by_artist(token, artist_id):
    # setup URL and headers for GET request
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US" 
    headers = get_auth_header(token)
    # send GET request
    result = get(url, headers=headers)
    # convert json to python dictionary
    json_result = json.loads(result.content)["tracks"]
    # check if tracks was found
    if len(json_result) == 0:
        print("No tracks found")
        return None
    else: 
        return json_result

def get_albums_by_artist(token, artist_id):
    # setup URL and headers for GET request
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?country=US" 
    headers = get_auth_header(token)
    # send GET request
    result = get(url, headers=headers)
    # convert json to python dictionary
    json_result = json.loads(result.content)["items"]
    # check if albums was found
    if len(json_result) == 0:
        print("No albums found")
        return None
    else: 
        return json_result
    
def get_song_info(token, song_id):
    # setup URL and headers for GET request
    url = f"https://api.spotify.com/v1/tracks/{song_id}" 
    headers = get_auth_header(token)
    # send GET request
    result = get(url, headers=headers)
    # convert json to python dictionary
    json_result = json.loads(result.content)
    return json_result

def get_album_info(token, album_id):
    # setup URL and headers for GET request
    url = f"https://api.spotify.com/v1/albums/{album_id}" 
    headers = get_auth_header(token)
    # send GET request
    result = get(url, headers=headers)
    # convert json to python dictionary
    json_result = json.loads(result.content)
    return json_result