import spotipy
from spotipy.oauth2 import SpotifyOAuth

def get_favorite_tracks(sp):
    tracks = []
    results = sp.current_user_saved_tracks()
    
    while True:
        for item in results['items']:
            tracks.append(item['track'])
        if not results['next']:
            break
        results = sp.next(results)
    
    return tracks
    
def get_favorite_albums(sp):
    albums = []
    results = sp.current_user_saved_albums()
    
    while True:
        for item in results['items']:
            albums.append(item['album'])
        if not results['next']:
            break
        results = sp.next(results)
    
    return albums
    
def get_playlists(sp):
    playlists = []
    results = sp.current_user_playlists()

    while True:
        for item in results['items']:
            playlists.append(item)
        if not results['next']:
            break
        results = sp.next(results)
    
    return playlists
    
def get_playlist_tracks(sp, playlist_id):
    playlist_tracks = []
    results = sp.playlist(playlist_id=playlist_id, fields="tracks.items(track(id)),tracks.next")
    results = results['tracks']
    
    while True:
        for item in results['items']:
            playlist_tracks.append(item['track'])
        if not results['next']:
            break
        results = sp.next(results)
        
    return playlist_tracks

def get_user_id(sp):
    user = sp.current_user()
    
    return user['id']

def create_playlist(sp, user_id, playlist_name):
    results = sp.user_playlist_create(user=user_id, name=playlist_name, public=False, description='List of all favorite tracks, created by script')
    
    return results

def add_playlist_tracks(sp, playlist_id, tracks):
     results = sp.playlist_add_items(playlist_id, tracks)
     
     return results

def remove_playlist_tracks(sp, playlist_id, tracks):
     results = sp.playlist_remove_all_occurrences_of_items(playlist_id, tracks)
     
     return results


def main():
    playlist_name = 'AllFavoriteSongs'
    track_post_limit = 100
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="<ENTER CLIENT ID HERE>",
                                                   client_secret="<ENTER CLIENT SECRET HERE>",
                                                   redirect_uri="http://localhost:8080",
                                                   scope="user-library-read playlist-read-private playlist-modify-private playlist-modify-public"))

    track_ids = set()
    tracks = get_favorite_tracks(sp)
    for track in tracks:
        track_ids.add(track['id'])

    print('Found', len(track_ids), 'individual favorite tracks')

    album_track_ids = set()
    albums = get_favorite_albums(sp)
    for album in albums:
        for track in album['tracks']['items']:
            album_track_ids.add(track['id'])

    print('Found', len(album_track_ids), 'tracks from favorite albums')

    all_track_ids = track_ids.union(album_track_ids)

    user_id = get_user_id(sp)

    playlists = get_playlists(sp)

    playlist_id = None
    for playlist in playlists:
        if playlist['owner']['id'] == user_id and playlist['name'] == playlist_name:
            playlist_id = playlist['id']
            print('Found existing playlist')

    if not playlist_id:
        results = create_playlist(sp, user_id, playlist_name)
        playlist_id = results['id']
        print('Created new playlist')

    playlist_track_ids = set()
    playlist_tracks = get_playlist_tracks(sp, playlist_id)
    for playlist_track in playlist_tracks:
        playlist_track_ids.add(playlist_track['id'])

    print('Found', len(playlist_track_ids), 'tracks in playlist')

    missing_tracks_ids = list(track_ids.difference(playlist_track_ids))
    print('Adding', len(missing_tracks_ids), 'missing individual favorite tracks')
    for i in range(0, len(missing_tracks_ids), track_post_limit):
        add_playlist_tracks(sp, playlist_id, missing_tracks_ids[i:i+track_post_limit])
    
    missing_album_tracks_ids = list(album_track_ids.difference(playlist_track_ids))
    print('Adding', len(missing_album_tracks_ids), 'missing tracks from favorite albums')
    for i in range(0, len(missing_album_tracks_ids), track_post_limit):
        add_playlist_tracks(sp, playlist_id, missing_album_tracks_ids[i:i+track_post_limit])
    
    obsolete_tracks_ids = list(playlist_track_ids.difference(all_track_ids))
    print('Removing', len(obsolete_tracks_ids), 'obsolete tracks in playlist')
    for i in range(0, len(obsolete_tracks_ids), track_post_limit):
        remove_playlist_tracks(sp, playlist_id, obsolete_tracks_ids[i:i+track_post_limit])
        
    print('All done, have fun!')



if __name__ == '__main__':
    main()
