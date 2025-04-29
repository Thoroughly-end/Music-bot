import urllib.request as request
import spotipy
from bs4 import BeautifulSoup
from config import config
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build # API client library

sp_api = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id = config.SPOTIFY_ID, client_secret = config.SPOTIFY_SECRET))   #設定Spotify class中的各種參數

async def convert_spotify(url):   #將Spotify網址轉換成歌名加作者
    result = ''
    with request.urlopen(url) as response:
        page = response.read().decode("utf-8")
        soup = BeautifulSoup(page, 'html.parser')
        title = soup.find('title')
        title = title.string
        title = title.replace('- song and lyrics ', '')
        title = title.replace('| Spotify', '')
        result = title
    return result

def get_spotify_playlist(url):   #取得播放清單中的歌曲和作者
    songs = []
    code = url.split('/')[4].split('?')[0]   #將網址最後的代碼分離
    if "open.spotify.com/album" in url:
            raw_songs=[]
            results = sp_api.album_tracks(code)
            tracks = results['items']

            while results['next']:   #當資料出現下一頁時
                results = sp_api.next(results)
                tracks.extend(results['items'])
            
            for name in tracks:
                for artist in name['artists']:
                    Name = name['name']
                    Artist = artist['name']
                    dic = {'songname' : Name, 'artist' : Artist}
                    raw_songs.append(dic)
            
            for i in range(len(raw_songs)):   #歌曲有協作者而造成歌曲重複，因此合併相同歌名的作者
                if i == 0:
                    Name = raw_songs[i]['songname']
                    Artist = raw_songs[i]['artist']
                    dic = {'songname' : Name, 'artist' : Artist}
                    songs.append(dic)
                else:
                    co_author = ""
                    if raw_songs[i]['songname'] == raw_songs[i-1]['songname']:
                        co_author = co_author + raw_songs[i]['artist']
                        dic = {'songname' : Name, 'artist' : co_author}
                        songs[len(songs)-1] = dic
                    else:
                        Name = raw_songs[i]['songname']
                        Artist = raw_songs[i]['artist']
                        dic = {'songname' : Name, 'artist' : Artist}
                        songs.append(dic)
    
    if "open.spotify.com/playlist" in url:
        results = sp_api.playlist_items(code)
        tracks = results['items']
        raw_songs=[]
        
        while results['next']:
            results = sp_api.next(results)
            tracks.extend(results['items'])
        
        for track in tracks:
            for artist in track['track']['artists']: 
                Name = track['track']['name']
                Artist = artist['name']
                Link = track['track']['external_urls']['spotify']
                dic = {'songname' : Name, 'artist' : Artist, 'link' : Link}
                raw_songs.append(dic)
        
        for i in range(len(raw_songs)):   #歌曲有協作者而造成歌曲重複，因此合併相同歌名的作者
            if i == 0:
                Name = raw_songs[i]['songname']
                Artist = raw_songs[i]['artist']
                dic = {'songname' : Name, 'artist' : Artist}
                songs.append(dic)
            else:
                co_author = ""
                if raw_songs[i]['songname'] == raw_songs[i-1]['songname'] and raw_songs[i]['link'] == raw_songs[i-1]['link']:   #歌名和連結同時相同，確保為有協作者的歌曲
                    co_author = co_author + raw_songs[i]['artist']
                    dic = {'songname' : Name, 'artist' : co_author}
                    songs[len(songs)-1] = dic
                else:
                    Name = raw_songs[i]['songname']
                    Artist = raw_songs[i]['artist']
                    dic = {'songname' : Name, 'artist' : Artist}
                    songs.append(dic)
    return songs

def get_song_name(songid):   #取得YT歌曲名稱
    youtube = build('youtube', 'v3', developerKey=config.YOUTUBE_API_KEY)
    request = youtube.videos().list(part="snippet ",id=songid)
    response = request.execute()
    try:
        return response['items'][0]['snippet']['title']
    except Exception:
        pass

def get_yt_playlist(playlist_id):   #取得YT播放清單歌曲之網址及名稱
    youtube = build('youtube', 'v3', developerKey=config.YOUTUBE_API_KEY)
    request = youtube.playlistItems().list(part = "snippet",maxResults = 50,playlistId = playlist_id)
    response = request.execute()
    songs = []
    for i in range(len(response['items'])):
        dic={'SongName' : str(response['items'][i]['snippet']['title']), 'url' : "https://www.youtube.com/watch?v="+str(response['items'][i]['snippet']['resourceId']['videoId'])}
        songs.append(dic)
    return songs