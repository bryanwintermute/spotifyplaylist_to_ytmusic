from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json
import settings
import argparse
from datetime import datetime
import os
from SpotifyExport import Spotify

path = os.path.dirname(os.path.realpath(__file__)) + os.sep


class YouService:
    client = None
    scopes = ["https://www.googleapis.com/auth/youtube"]

    @classmethod
    def authorize(cls, client_secrets):
        return InstalledAppFlow.from_client_secrets_file(
            client_secrets, scopes=cls.scopes
        ).run_console()

    @classmethod
    def get_client(cls):
        if not cls.client:
            info = json.loads(settings['youtube']['credentials'])
            credentials = Credentials.from_authorized_user_info(
                info, scopes=cls.scopes
            )
            cls.client = build("youtube", "v3", credentials=credentials)
        return cls.client

    @classmethod
    def search_track(cls, track):
        params = dict(
            part="snippet",
            maxResults=1,
            q=track,
            type="video",
            topicId="/m/04rlf"
        )

        response = cls.get_client().search().list(**params).execute()
        for item in response.get("items", []):
            if item["id"]["kind"] == "youtube#video":
                return item["id"]["videoId"]

    @classmethod
    def create_playlist(cls, title, description, public=False):
        params = dict(
            body=dict(
                snippet=dict(title=title, description=description),
                status=dict(privacyStatus="public" if public else "private"),
            ),
            part="snippet,status",
        )
        return cls.get_client().playlists().insert(**params).execute()["id"]

    @classmethod
    def add_songs(cls, playlist, tracks):
        songIds, notFound = YouService.search_songs(tracks)

        cls.add_songs_to_playlist(playlist, songIds)

        with open(path + 'noresults_youtube.txt', 'w', encoding="utf-8") as f:
            f.write("\n".join(notFound))
            f.close()

    @classmethod
    def add_songs_to_playlist(cls, playlist, tracks):
        for i, song in enumerate(tracks):
            YouService.create_playlist_item(playlist, song)
            if i % 20 == 0:
                print(str(i) + ' inserted')

    @classmethod
    def search_songs(cls, tracks):
        songIds=[]
        notFound = list()
        try:
            for i, song in enumerate(tracks):
                song = song.replace(" &", "")
                result = YouService.search_track(song + ' "auto-generated by youtube"')
                if result is None:
                    notFound.append(song)
                else:
                    songIds.append(result)
                if i % 20 == 0:
                    print(str(i) + ' searched')
        except Exception as ex:
            print(ex)

        return songIds, notFound

    @classmethod
    def get_categories(cls):
        ids = ','.join(str(i) for i in range(1, 20))
        params = dict(
            id=ids,
            part="snippet,id"
        )
        return cls.get_client().videoCategories().list(**params).execute()

    @classmethod
    def create_playlist_item(cls, playlist, video_id):
        params = dict(
            body=dict(
                snippet=dict(
                    playlistId=playlist,
                    resourceId=dict(kind="youtube#video", videoId=video_id),
                )
            ),
            part="snippet",
        )
        return cls.get_client().playlistItems().insert(**params).execute()
    #
    # @classmethod
    # def remove_playlist_item(cls, playlist_item: PlaylistItem):
    #     params = dict(id=playlist_item.id)
    #     return cls.get_client().playlistItems().delete(**params).execute()

def get_args():
    parser = argparse.ArgumentParser(description='Transfer spotify playlist to YouTube Music.')
    parser.add_argument("playlist", type=str, help="Provide a playlist Spotify link. Alternatively, provide a text file (one song per line)")
   #parser.add_argument("-u", "--update", type=str, help="Delete all entries in the provided Google Play Music playlist and update the playlist with entries from the Spotify playlist.")
    parser.add_argument("-n", "--name", type=str, help="Provide a name for the YouTube Music playlist. Default: Spotify playlist name")
    parser.add_argument("-i", "--info", type=str, help="Provide description information for the YouTube Music Playlist. Default: Spotify playlist description")
    parser.add_argument("-s", "--search", type=int, help="Only search for items due to YouTube Quota limit. Provide starting index in playlist to search from")
    parser.add_argument("-d", "--date", action='store_true', help="Append the current date to the playlist name")
    parser.add_argument("-p", "--public", action='store_true', help="Make the playlist public. Default: private")
    #parser.add_argument("-r", "--remove", action='store_true', help="Remove playlists with specified regex pattern.")
    #parser.add_argument("-a", "--all", action='store_true', help="Transfer all public playlists of the specified user (Spotify User ID).")
    return parser.parse_args()


def main():
    args = get_args()
    date = ""
    if args.date:
        date = " " + datetime.today().strftime('%m/%d/%Y')
    try:
        playlist = Spotify().getSpotifyPlaylist(args.playlist)
    except Exception as ex:
        print("Could not get Spotify playlist. Please check the playlist link.\n Error: " + repr(ex))
        return

    if args.search:
        if len(playlist['tracks']) > args.search:
            return
        songIds = YouService.search_songs(playlist['tracks'][args.search:])
        with open('youtube.txt', 'a') as out:
            [out.write(str(item) + '\n') for item in songIds]
        return

    name = args.name + date if args.name else playlist['name'] + date
    info = playlist['description'] if (args.info is None) else args.info
    playlistId = YouService.create_playlist(name, info, args.public)
    if len(playlist['tracks']) <= 60:
        YouService.add_songs(playlistId, playlist['tracks'])
        print("Success: created playlist \"" + name + "\"")
    else:
        songIds = YouService.search_songs(playlist['tracks'])
        with open(path + 'youtube.txt', 'w') as out:
            [out.write(str(item) + '\n') for item in songIds]
        print("Success: searched " + str(len(songIds)) + " songs for playlist " + name + " and saved to youtube.txt")


if __name__ == "__main__":
    main()