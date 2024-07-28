from discord.ext import commands
import discord
import link as link
import search as search
import asyncio
import random

class Music(commands.Cog):   #繼承類別
    def __init__(self, bot):
        self.bot = bot
    
    queue = []   #音樂佇列
    mode = ''
    playlist_url = ''
    yt_url_list = []
    
    @commands.command(name='join', help='Tells the bot to join the voice channel')
    async def join(self, ctx):
        if ctx.message.author.voice:
            channel = ctx.message.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("Please join a voice channel")

    @commands.command(name = 'leave', help = 'To make the bot leave the voice channel')
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        try:
            ctx.voice_client.pause()
            self.queue = []
            await voice_client.disconnect(force = True)
        except:
            await ctx.send("I am not in a voice channel")
    
    @commands.command(name = 'play', help = 'To play songs')
    async def play(self, ctx, message):
        self.queue = []   #清空佇列
        self.mode = ''
        self.playlist_url = ''
        self.yt_url_list = []
        if "open.spotify.com/track/" in message:   #若是單首歌曲
            song = await link.convert_spotify(message)
            self.queue.append(song)
            url = search.search_yt(song)
            if not ctx.voice_client:   #若沒有建立語音連線
                await Music.join(self, ctx)
            if ctx.voice_client.is_playing():   #若在播放音樂中
                ctx.voice_client.pause()
            await ctx.send(f"Now is playing {song}")
            ctx.voice_client.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self, ctx))

        elif "open.spotify.com/playlist/" in self.playlist_url or "open.spotify.com/album/" in self.playlist_url:   #若是播放清單或專輯
            self.mode = 'loop'
            self.playlist_url = str(message)
            songs = link.get_spotify_playlist(message)
            for i in range(len(songs)):
                songName_artist = songs[i]['songname'] + " " + songs[i]['artist']
                self.queue.append(songName_artist)   #將擷取到的音樂輸入佇列
            songName_artist = songs[0]['songname'] + " " + songs[0]['artist']
            url = search.search_yt(songName_artist)
            if not ctx.voice_client:   #若沒有語音連線
                await Music.join(self, ctx)
            if ctx.voice_client.is_playing():   #若正在播放音樂
                ctx.voice_client.pause()
            ctx.voice_client.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self, ctx))
        
        elif "https://www.youtube.com/watch?v=" in message:   #若是YT單曲
            url = str(message)
            if "&list=" in url:   #取得歌曲id
                id = url.replace('https://www.youtube.com/watch?v=', '')
                num = id.find("&list=")
                id = id[:num]
            else:
                id = url.replace('https://www.youtube.com/watch?v=', '')
            song = link.get_song_name(id)
            dlurl = search.url_search_yt(url)
            self.queue.append(song)
            if not ctx.voice_client:   #若沒有建立語音連線
                await Music.join(self, ctx)
            if ctx.voice_client.is_playing():   #若在播放音樂中
                ctx.voice_client.pause()
            await ctx.send(f"Now is playing {song}")
            ctx.voice_client.play(discord.FFmpegPCMAudio(dlurl, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self, ctx))
        
        elif "https://youtube.com/playlist?list=" in message:   #若是YT播放清單
            self.mode = 'loop'
            self.playlist_url = str(message)
            id = self.playlist_url.replace('https://youtube.com/playlist?list=', '')   #取得播放清單id
            num = id.find('&')
            id = id[:num]
            songs = link.get_yt_playlist(id)
            dlurl = search.url_search_yt(songs[0]['url'])
            for i in range(len(songs)):
                self.queue.append(songs[i]['SongName'])
                self.yt_url_list.append(songs[i]['url'])
            if not ctx.voice_client:   #若沒有語音連線
                await Music.join(self, ctx)
            if ctx.voice_client.is_playing():   #若正在播放音樂
                ctx.voice_client.pause()
            ctx.voice_client.play(discord.FFmpegPCMAudio(dlurl, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self, ctx))


    @commands.command(name = 'skip', help = 'To skip the song')
    async def skip(self, ctx):
        if "https://youtube.com/playlist?list=" in self.playlist_url:
            url = self.yt_url_list[1]
            self.yt_url_list.remove(self.yt_url_list[0])
            self.queue.remove(self.queue[0])
            dlurl = search.url_search_yt(url)
            try:
                ctx.voice_client.pause()
                ctx.voice_client.play(discord.FFmpegPCMAudio(dlurl, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self, ctx))
            except Exception:
                Music.next_song(self,ctx)
        elif "open.spotify.com/playlist/" in self.playlist_url or "open.spotify.com/album/" in self.playlist_url:
            url = search.search_yt(self.queue[1])
            self.queue.remove(self.queue[0])
            ctx.voice_client.pause()
            ctx.voice_client.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self, ctx))
        else:
            pass
    
    @commands.command(name = 'info', help = 'To get what is playing now')
    async def info(self, ctx):
        await ctx.send(f"Now is playing {self.queue[0]}")
    
    @commands.command(name = 'shuffle', help = 'To switch to shuffle mode')
    async def shuffle(self, ctx):
        if "open.spotify.com/playlist/" in self.playlist_url or "open.spotify.com/album/" in self.playlist_url:
            if len(self.queue) <= 1:
                await ctx.send("There is no song left")
            elif self.mode == 'shuffle':
                await ctx.send("It is already shuffle mode")
            else:
                playing = self.queue[0]
                random.shuffle(self.queue)
                self.queue.remove(playing)
                self.queue.insert(0, playing)
                self.mode = 'shuffle'
                await ctx.send("Switch to shuffle mode successfully")
        elif "https://youtube.com/playlist?list=" in self.playlist_url:
            if len(self.yt_url_list) <= 1:
                await ctx.send("There is no song left")
            elif self.mode == 'shuffle':
                await ctx.send("It is already shuffle mode")
            else:
                temp = []
                for i in range(len(self.yt_url_list)):
                    temp_dic = {'url' : str(self.yt_url_list[i]), 'title' : str(self.queue[i])}
                    temp.append(temp_dic)
                playing = temp[0]
                random.shuffle(temp)
                temp.remove(playing)
                temp.insert(0, playing)
                for i in range(len(temp)):
                    self.queue[i] = temp[i]['title']
                    self.yt_url_list[i] = temp[i]['url']
                self.mode = 'shuffle'
                await ctx.send("Switch to shuffle mode successfully")
        else:
            pass
        
    @commands.command(name = 'loop', help = 'To switch to loop mode')
    async def loop(self, ctx):
        if len(self.queue) <= 1:
            await ctx.send("There is no song left")
        elif self.mode == 'loop':
            await ctx.send("It is already loop mode")
        else:
            if "open.spotify.com/playlist/" in self.playlist_url or "open.spotify.com/album/" in self.playlist_url:
                playing = self.queue[0]
                songs = link.get_spotify_playlist(self.playlist_url)
                new_list = []
                status = False
                for i in range(len(songs)):   #直到找到現在正在播放的歌曲再加入佇列
                    songName_artist = songs[i]['songname'] + " " + songs[i]['artist']
                    if songName_artist == playing or status == True:
                        new_list.append(songName_artist)
                        status = True
                self.queue = new_list
                self.mode = 'loop'
                await ctx.send("Switch to loop mode successfully")
            elif "https://youtube.com/playlist?list=" in self.playlist_url:
                playing = self.yt_url_list[0]
                id = self.playlist_url.replace('https://youtube.com/playlist?list=', '')
                num = id.find('&')
                id = id[:num]
                songs = link.get_yt_playlist(id)
                new_url_list = []
                new_title_list = []
                status = False
                for i in range(len(songs)):
                    if songs[i]['url'] == playing or status == True:
                        new_url_list.append(songs[i]['url'])
                        new_title_list.append(songs[i]['SongName'])
                        status = True
                self.queue = new_title_list
                self.yt_url_list = new_url_list
                self.mode = 'loop'
                await ctx.send("Switch to loop mode successfully")
            else:
                pass

    @commands.command(name = 'pause', help = 'To pause the playing song')
    async def pause(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
    
    @commands.command(name = 'resume', help = 'To resume playing')
    async def resume(self, ctx):
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):   #在播放完音樂之後自動退出
        if not member.id == self.bot.user.id:   #確保是被機器人本身觸發
            return
        elif before.channel is None:   #確保不是因為機器人斷線觸發
            voice_client = after.channel.guild.voice_client
            time = 0
            while True:
                await asyncio.sleep(1)   #每秒檢查一次
                time = time + 1
                if voice_client.is_playing() and not voice_client.is_paused():   #音樂結束時
                    time = 0
                if time == 30:   #30秒時
                    await voice_client.disconnect()   #斷線
                if not voice_client.is_connected():   #若無連線則跳出迴圈
                    break
    
    def next_song(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
        if len(self.queue) == 1:   #若音樂佇列只剩最後一首歌(已經播放完畢)
            self.queue = []   #清空佇列
        else:
            if "https://youtube.com/playlist?list=" in self.playlist_url:
                url = self.yt_url_list[1]
                self.yt_url_list.remove(self.yt_url_list[0])
                self.queue.remove(self.queue[0])
                dlurl = search.url_search_yt(url)
                try:
                    ctx.voice_client.play(discord.FFmpegPCMAudio(dlurl, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self, ctx))
                except Exception:   #若下一首不可播放則再下一首
                    Music.next_song(self,ctx)
            else:
                url = search.search_yt(self.queue[1])
                self.queue.remove(self.queue[0])
                try:
                    ctx.voice_client.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self, ctx))
                except Exception:
                    Music.next_song(self,ctx)

async def setup(bot):
    await bot.add_cog(Music(bot))