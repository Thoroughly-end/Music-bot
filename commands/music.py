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
    playlist_url = ""
    
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
    async def play(self, ctx, message: str = ""):
        self.queue = []   #清空佇列
        self.mode = ''
        self.playlist_url = ''
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
        elif "open.spotify.com/playlist/" or "open.spotify.com/album/" in message:   #若是播放清單或專輯
            self.mode = 'loop'
            self.playlist_url = message
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

    @commands.command(name = 'skip', help = 'To skip the song')
    async def skip(self, ctx):
        url = search.search_yt(self.queue[1])
        await ctx.send(f"Now is playing {self.queue[1]}")
        self.queue.remove(self.queue[0])
        ctx.voice_client.pause()
        ctx.voice_client.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self, ctx))
    
    @commands.command(name = 'info', help = 'To get what is playing now')
    async def info(self, ctx):
        ctx.send(f"Now is playing {self.queue[0]}")
    
    @commands.command(name = 'shuffle', help = 'To switch to shuffle mode')
    async def shuffle(self, ctx):
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
    
    @commands.command(name = 'loop', help = 'To switch to loop mode')
    async def loop(self, ctx):
        if len(self.queue) <= 1:
            await ctx.send("There is no song left")
        elif self.mode == 'loop':
            await ctx.send("It is already loop mode")
        else:
            playing = self.queue[0]
            songs = link.get_spotify_playlist(self.playlist_url)
            new_list = []
            a = 0
            for i in range(len(songs)):
                songName_artist = songs[i]['songname'] + " " + songs[i]['artist']
                if songName_artist == playing or a == 1:
                    new_list.append(songName_artist)
                    a = 1
            self.queue = new_list

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
        if len(self.queue) == 1:   #若音樂佇列只剩最後一首歌(已經播放完畢)
            self.queue = []   #清空佇列
        else:
            url = search.search_yt(self.queue[1])
            self.queue.remove(self.queue[0])
            ctx.voice_client.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self, ctx))

async def setup(bot):
    await bot.add_cog(Music(bot))