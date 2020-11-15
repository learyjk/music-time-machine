from bs4 import BeautifulSoup
from config import client_id, client_secret
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests

user_input = input("What date do you want to travel to? (YYYY-MM-DD): ")

response = requests.get(f"https://www.billboard.com/charts/hot-100/{user_input}")
website_html = response.text
soup = BeautifulSoup(website_html, "html.parser")

all_titles = soup.find_all(class_="chart-element__information__song text--truncate color--primary")
all_artists = soup.find_all(class_="chart-element__information__artist text--truncate color--secondary")

with open("song_list.txt", mode="w") as file:
    for i in range(len(all_titles)):
        file.write(f"{all_titles[i].getText()} :: {all_artists[i].getText()}\n")

song_names = [title.getText() for title in all_titles]

spotify = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=client_id,
        client_secret=client_secret,
        show_dialog=True,
        cache_path="token.txt"
    )
)

user_id = spotify.current_user()["id"]
print(user_id)

song_uris = []
year = user_input.split("-")[0]
for song in song_names:
    result = spotify.search(q=f"track:{song} year:{year}", type="track")
    print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

playlist = spotify.user_playlist_create(user=user_id, name=f"{user_input} Top 100", public=False)

spotify.playlist_add_items(user=user_id, playlist_id=playlist["id"], tracks=song_uris)