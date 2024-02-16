from yt_dlp import YoutubeDL

def search_yt(song_name):
    YDL_params = {'noplaylist': True, 'format' : 'bestaudio'}
    with YoutubeDL(params = YDL_params) as ydl:
        try:
            info = ydl.extract_info("ytsearch:%s" % song_name, download=False)['entries'][0]
            return info['url']
        except Exception:
            pass