from yt_dlp import YoutubeDL

def search_yt(song_name):   #用歌名搜尋
    YDL_params = {'noplaylist': True, 'format' : 'bestaudio'}
    with YoutubeDL(params = YDL_params) as ydl:
        try:
            info = ydl.extract_info("ytsearch:%s" % song_name, download=False)['entries'][0]
            return info['url']
        except Exception:
            pass

def url_search_yt(url):   #用網址搜尋
    YDL_params = {'noplaylist': True, 'format' : 'bestaudio'}
    with YoutubeDL(params = YDL_params) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            music_url = info.get("url", None)
            return music_url
        except Exception:
            pass