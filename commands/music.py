from discord.ext import commands
import discord
import link as link
import search as search

class Music(commands.Cog):   #繼承類別
    def __init__(self, bot):
        self.bot = bot
    
    queue = []   #音樂佇列
    
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
            await voice_client.disconnect(force = True)
        except:
            await ctx.send("I am not in a voice channel")
    
    @commands.command(name = 'play', help = 'To play songs')
    async def play(self, ctx, message: str = ""):
        self.queue = []   #清空佇列
        if "open.spotify.com/track/" in message:   #若是單首歌曲
            song = await link.convert_spotify(message)
            url = search.search_yt(song)
            await ctx.send(f"Now is playing {song}")
            if not ctx.voice_client():   #若沒有建立語音連線
                await Music.join(self, ctx)
            if ctx.voice_client.is_playing():   #若在播放音樂中
                ctx.voice_client.pause()
            ctx.voice_client.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.leave(self, ctx))
        elif "open.spotify.com/playlist/" or "open.spotify.com/album/" in message:   #若是播放清單或專輯
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
            ctx.voice_client.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: next_song(ctx, self.queue))

    @commands.command(name = 'skip', help = 'To skip the song')
    async def skip(self, ctx):
        url = search.search_yt(self.queue[1])
        await ctx.send(f"Now is playing {self.queue[1]}")
        self.queue.remove(self.queue[0])
        ctx.voice_client.pause()
        if len(self.queue) == 0:
            ctx.voice_client.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.leave(self, ctx))
        else:
            ctx.voice_client.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: next_song(ctx, self.queue))
    
    @commands.command(name = 'info', help = 'To get what is playing now')
    async def info(self, ctx):
        ctx.send(f"Now is playing {self.queue[0]}")

async def setup(bot):
    await bot.add_cog(Music(bot))

def next_song(ctx, queue):
        url = search.search_yt(queue[1])
        queue.remove(queue[0])
        if len(queue) == 0:
            ctx.voice_client.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.leave(ctx))
        else:
            ctx.voice_client.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: next_song(ctx, queue))