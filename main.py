from requests import RequestException
from dotenv import load_dotenv
import urllib
import time
import json
import sys
import os
import re

import spotify_functions

# load environment variables
load_dotenv()
# get environment variables and assign to variables
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

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

token = spotify_functions.get_token()

# get user input, check if input is empty
while True:
    user_artist = input("Enter an artist: ")
    if user_artist.strip():
        break
    print("Invalid artist name. Please try again.")

try:
    result = spotify_functions.search_for_artist(token, user_artist)
    # check if artist was found
    if result:
        artist_id = result["id"]
        songs = spotify_functions.get_songs_by_artist(token, artist_id)
        albums = spotify_functions.get_albums_by_artist(token, artist_id)
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
                song_info = spotify_functions.get_song_info(token, song['id'])
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
                album_info = spotify_functions.get_song_info(token, album['id'])
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