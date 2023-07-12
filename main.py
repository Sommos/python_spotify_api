from dotenv import load_dotenv
from requests import post, get
import base64
import urllib
import json
import os
import re

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
    #  convert json to python dictionary
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
    #  convert json to python dictionary
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
    #  convert json to python dictionary
    json_result = json.loads(result.content)["items"]
    # check if albums was found
    if len(json_result) == 0:
        print("No albums found")
        return None
    else: 
        return json_result

def sanitize_filename(filename):
    # remove special characters from filename
    sanitized_filename = re.sub(r"[^\w\s.-]", "_", filename)
    return sanitized_filename

token = get_token()
user_artist = input("Enter an artist: ")
result = search_for_artist(token, user_artist)

# check if artist was found
if result:
    artist_id = result["id"]
    songs = get_songs_by_artist(token, artist_id)
    albums = get_albums_by_artist(token, artist_id)
    # replace spaces with underscores
    artist_folder = user_artist.replace(" ", "_")
    # create folders for images
    os.makedirs(f"images/{artist_folder}/songs/", exist_ok=True)
    os.makedirs(f"images/{artist_folder}/albums/", exist_ok=True)
    # enumerate through top 10 songs and print names
    print("Top 10 songs:")
    for i, song in enumerate(songs):
        print(f"{i+1}. {song['name']}")
        # retrieve the image URL of the song
        image_url = song['album']['images'][0]['url']
        # generate a filename for the image
        filename = sanitize_filename(f"{song['name']}.png")
        # set the filepath
        filepath = os.path.join("images", artist_folder, "songs", filename)
        # save the image
        urllib.request.urlretrieve(image_url, filepath)

    # add a break between songs and albums
    print("\n" + "-"*20 + "\n")

    # enumerate through top 10 albums and print names
    print("Top 10 albums:")
    for x, album in enumerate(albums[:10]):
        print(f"{x+1}. {album['name']}")
        # retrieve the image URL of the album
        image_url = album['images'][0]['url']
        # generate a filename for the image
        filename = sanitize_filename(f"{album['name']}.png")
        # set the filepath
        filepath = os.path.join("images", artist_folder, "albums", filename)
        # save the image
        urllib.request.urlretrieve(image_url, filepath)
else:
    print("Artist not found.")