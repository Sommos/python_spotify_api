import sys
from requests import RequestException
from dotenv import load_dotenv
from requests import post, get
import base64
import urllib
import time
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

def sanitize_filename(filename):
    # remove special characters from filename
    sanitized_filename = re.sub(r"[^\w\s.-]", "_", filename)
    return sanitized_filename

def display_loading_spinner():
    while True:
        for cursor in "|/-\\":
            print(f"\rLoading... {cursor}", end="")
            sys.stdout.flush()
            time.sleep(0.1)
            # clear the line
            print("\r\033[K", end="")
        break

token = get_token()

# get user input, check if input is empty
while True:
    user_artist = input("Enter an artist: ")
    if user_artist.strip():
        break
    print("Invalid artist name. Please try again.")

try:
    result = search_for_artist(token, user_artist)
    # check if artist was found
    if result:
        artist_id = result["id"]
        songs = get_songs_by_artist(token, artist_id)
        albums = get_albums_by_artist(token, artist_id)
        # replace spaces with underscores
        artist_folder = user_artist.replace(" ", "_")
        # create folders for information
        os.makedirs(f"info/{artist_folder}/songs/info", exist_ok=True)
        os.makedirs(f"info/{artist_folder}/albums/info", exist_ok=True)
        os.makedirs(f"info/{artist_folder}/songs/images", exist_ok=True)
        os.makedirs(f"info/{artist_folder}/albums/images", exist_ok=True)
        # enumerate through top 10 songs and print names
        print("Top 10 songs:")
        for i, song in enumerate(songs):
            print(f"{i+1}. {song['name']}")
            try:
                # retrieve the image URL of the song
                image_url = song['album']['images'][0]['url']
                # generate a filename for the image
                filename = sanitize_filename(f"{song['name']}.png")
                # set the filepath
                filepath = os.path.join("info", artist_folder, "songs", "images", filename)
                # display loading spinner
                display_loading_spinner()
                # clear the line after loading spinner
                print("\r\033[K", end="")
                # save the image
                urllib.request.urlretrieve(image_url, filepath)

                # get additional information about the song
                song_info = get_song_info(token, song['id'])
                # save the song information to a file
                song_info_filepath = os.path.join("info", artist_folder, "songs", "info", f"{song['name']}.txt")
                with open(song_info_filepath, "w") as file:
                    file.write(json.dumps(song_info, indent=4))
            except(urllib.error.URLError, urllib.error.HTTPError, IOError, RequestException) as e:
                print(f"Error saving image for song '{song['name']}': {str(e)}")

        # add a break between songs and albums
        print("\n" + "-"*20 + "\n")

        # enumerate through top 10 albums and print names
        print("Top 10 albums:")
        for x, album in enumerate(albums[:10]):
            print(f"{x+1}. {album['name']}")
            try:
                # retrieve the image URL of the album
                image_url = album['images'][0]['url']
                # generate a filename for the image
                filename = sanitize_filename(f"{album['name']}.png")
                # set the filepath
                filepath = os.path.join("info", artist_folder, "albums", "images", filename)
                # display loading spinner
                display_loading_spinner()
                # clear the line after loading spinner
                print("\r\033[K", end="")
                # save the image
                urllib.request.urlretrieve(image_url, filepath)

                # get additional information about the album
                album_info = get_song_info(token, album['id'])
                # save the album information to a file
                album_info_filepath = os.path.join("info", artist_folder, "albums", "info", f"{album['name']}.txt")
                with open(album_info_filepath, "w") as file:
                    file.write(json.dumps(album_info, indent=4))
            except(urllib.error.URLError, urllib.error.HTTPError, IOError, RequestException) as e:
                print(f"Error saving image for album '{album['name']}': {str(e)}")
    else:
        print("Artist not found.")
except(urllib.error.URLError, urllib.error.HTTPError, IOError, RequestException) as e:
    print(f"An error occurred during the request: {str(e)}")