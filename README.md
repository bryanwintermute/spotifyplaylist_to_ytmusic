# Transfer a Spotify Playlist to YouTube Music

A simple command line script to clone a Spotify playlist to YouTube Music.

- Transfer a single Spotify playlist
- Transfer all playlists for a Spotify user
- Transfer a playlist exported as a CSV using the **third-party site** [Exportify](https://watsonbox.github.io/exportify/)
- "Like" tracks on YouTube while optionally creating an associated playlist

## Requirements

- Python 3.6+ - https://www.python.org
- Python extensions: `pip install -U -r requirements`
- Have made at least one playlist manually on YouTube Music

## Setup

1. Initially you should create a new `settings.ini` containing your Spotify credentials.

Simply copy `settings.ini.example` to a new file `settings.ini`:

```zsh
$ cp settings.ini.example settings.ini
```

2. Generate a new app at https://developer.spotify.com/my-applications

3. Fill in your `client_id` and `client_secret` from your Spotify app

4. For YouTube Music, open a console in the source code folder and run

`python Setup.py youtube`

5. Open your browser and copy your request headers according to the instructions at https://ytmusicapi.readthedocs.io/en/latest/setup.html. 
   Paste them into the terminal to proceed.

This Setup.py procedure stores all credentials locally in the file `settings.ini`.

## Transfer a playlist

After you've created the settings file, you can simply run the script from the command line using:

`python YouTube.py <spotifylink>`

where `<spotifylink>` is a link like https://open.spotify.com/user/edmsauce/playlist/3yGp845Tz2duWCORALQHFO
Alternatively you can also **use a file name** in place of a spotify link. The file should contain one song per line.

The script will log its progress and output songs that were not found in YouTube Music to **noresults.txt**.

## Transfer all playlists of a Spotify user

For migration purposes, it is possible to transfer all public playlists of a user by using the Spotify user's ID (unique username).

`python YouTube.py --all <spotifyuserid>`

## Import tracks exported as a CSV using [Exportify](https://watsonbox.github.io/exportify/)
Some Spotify playlists are not accessible using the public API (e.g., generated playlists, "Liked" songs, private playlists, etc.). In these cases, it is still possible to import these playlists after exporting them using a third party tool such as [Exportify](https://watsonbox.github.io/exportify/). Simply visit that site (**NOTE**: these projects are unaffiliated with eachother, use at your own risk), follow the instructions to login, and then export the playlists you desire as CSVs. Then use the following command to import the tracks, specifying the path to the CSV file as a source.

`python YoutTube.py -e <path to CSV>`

Additional notes: 
1. This tool only really cares that the first column is a list of Spotify track ID links (e.g., `spotify:track:1w2b7yH3BlYMzDGN3QNQra`).
2. If no name is provided using the `-n` argument, the playlist name will be set to the CSV filename (e.g., "liked_songs.csv").
3. If no description is provided using the `-i` argument, the playlist description will be left blank. 

## "Like" the tracks when importing to YouTube Music

To "like" the music tracks being imported to YouTube Music, simply use the `-l` argument. This is particularly useful for importing Spotify's "Liked Songs" playlist.

Additionally, if you ONLY want to "like" the tracks instead of also creating a separate playlist, you can use the `-s` argument. **Note**: using `-s` without `-l` will effectively result in no action being taken.

Note: Currently, there is a baked-in delay of 2 seconds between "likes" to prevent overloading the API. Without this the action seems to fail silently.

## Command line options

There are some additional command line options for setting the playlist name and determining whether it's public or not. To view them, run

`> python YouTube.py -h`

Arguments:

```
usage: YouTube.py [-h] [-u UPDATE] [-n NAME] [-i INFO] [-d] [-p] [-r] [-a] [-e] [-l] [-s] playlist

Transfer spotify playlist to YouTube Music.

positional arguments:
  playlist              Provide a playlist Spotify link, a Spotify user ID (with -a), or a path to CSV file (with -e).

optional arguments:
  -h, --help            show this help message and exit
  -u UPDATE, --update UPDATE
                        Delete all entries in the provided Google Play Music playlist and update the playlist with entries from the Spotify playlist.
  -n NAME, --name NAME  Provide a name for the YouTube Music playlist. Default: Spotify playlist name
  -i INFO, --info INFO  Provide description information for the YouTube Music Playlist. Default: Spotify playlist description
  -d, --date            Append the current date to the playlist name
  -p, --public          Make the playlist public. Default: private
  -r, --remove          Remove playlists with specified regex pattern.
  -a, --all             Transfer all public playlists of the specified user (Spotify User ID).
  -e, --exportify       The playlist is a file path to a CSV exported from Exportify instead of a Spotify playlist link.
  -l, --like            'Like' the tracks on YouTube Music
  -s, --skip            Skip creation of the playlist on YouTube Music (useful for only 'liking' tracks)
```
