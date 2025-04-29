from discord.ext import commands
import discord
import link as link
import search as search
import asyncio
import random
from discord import app_commands
import ai

class Music(commands.Cog):   #繼承類別
    def __init__(self, bot):
        self.bot = bot
    
    queue = []   #音樂佇列
    mode = ''
    playlist_url = ''
    yt_url_list = []
    end = 0
    Spotify_track_url = ''
    

    async def join(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("Please join a voice channel")
            return 0
        else:
            destinate = interaction.user.voice.channel
            await destinate.connect()
            return 1

    @app_commands.command(name = 'leave', description = 'To make the bot leave the voice channel')
    async def leave(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        self.end = 1
        try:
            voice_client.stop()
            await voice_client.disconnect(force = True)
            await interaction.response.send_message("I left the voice channel")
        except:
            await interaction.response.send_message("I am not in a voice channel")
    
    @app_commands.command(name='play', description = 'To play a song or playlist')
    async def play(self, interaction: discord.Interaction, music_link: str):
        self.queue = []   #清空佇列
        self.mode = 'default'
        self.playlist_url = ''
        self.Spotify_track_url = ''
        self.yt_url_list = []
        self.end = 0

        if "open.spotify.com/track/" in music_link:   #若是單首歌曲
            try:   #建立語音連線
                status = await Music.join(self, interaction)
                if status == 0:
                    return
            except Exception as e:
                print(e)
            await interaction.response.defer()
            voice_client = interaction.guild.voice_client
            if voice_client.is_playing():   #若正在播放音樂
                voice_client.stop()

            song = await link.convert_spotify(music_link)
            self.queue.append(song)
            url = search.search_yt(song)
            self.Spotify_track_url = music_link
            
            await interaction.followup.send(f"Now is playing {song}")
            voice_client.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self,voice_client))
            

        elif "open.spotify.com/playlist/" in music_link or "open.spotify.com/album/" in music_link:   #若是播放清單或專輯
            try:   #建立語音連線
                status = await Music.join(self, interaction)
                if status == 0:
                    return
            except Exception as e:
                print(e)
            await interaction.response.defer()
            voice_client = interaction.guild.voice_client
            if voice_client.is_playing():   #若正在播放音樂
                voice_client.stop()
                

            self.playlist_url = str(music_link)
            songs = link.get_spotify_playlist(music_link)
            for i in range(len(songs)):
                songName_artist = songs[i]['songname'] + " by " + songs[i]['artist']
                self.queue.append(songName_artist)   #將擷取到的音樂輸入佇列
            songName_artist = songs[0]['songname'] + " by " + songs[0]['artist']
            url = search.search_yt(songName_artist)
                
            await interaction.followup.send(f"Now is playing {songName_artist}")
            voice_client.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self, voice_client))
        
        elif "https://www.youtube.com/watch?v=" in music_link or "https://youtu.be/" in music_link:   #若是YT單曲
            try:   #建立語音連線
                status = await Music.join(self, interaction)
                if status == 0:
                    return
            except Exception as e:
                print(e)
            await interaction.response.defer()
            voice_client = interaction.guild.voice_client

            if voice_client.is_playing():   #若正在播放音樂
                voice_client.stop()

            url = str(music_link)
            if "https://www.youtube.com/watch?v=" in url:
                if "&" in url:   #取得歌曲id
                    id = url.replace('https://www.youtube.com/watch?v=', '')
                    num = id.find("&list=")
                    id = id[:num]
                else:
                    id = url.replace('https://www.youtube.com/watch?v=', '')
            elif "https://youtu.be/" in url:
                if "?" in url:
                    tmpurl = url.replace("https://youtu.be/", "")
                    num = tmpurl.find("?")
                    id = tmpurl[:num]
                else:
                    id = url.replace("https://youtu.be/", "")
            song = link.get_song_name(id)
            dlurl = search.url_search_yt(url)
            self.queue.append(song)
            
            await interaction.followup.send(f"Now is playing {song}")
            voice_client.play(discord.FFmpegPCMAudio(dlurl, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self, voice_client))
        
        elif "https://youtube.com/playlist?list=" in music_link:   #若是YT播放清單
            try:   #建立語音連線
                status = await Music.join(self, interaction)
                if status == 0:
                    return
            except Exception as e:
                print(e)
            await interaction.response.defer()
            voice_client = interaction.guild.voice_client
            if voice_client.is_playing():   #若正在播放音樂
                voice_client.stop()

            self.playlist_url = str(music_link)
            id = self.playlist_url.replace('https://youtube.com/playlist?list=', '')   #取得播放清單id
            num = id.find('&')
            id = id[:num]
            songs = link.get_yt_playlist(id)
            dlurl = search.url_search_yt(songs[0]['url'])
            for i in range(len(songs)):
                self.queue.append(songs[i]['SongName'])
                self.yt_url_list.append(songs[i]['url'])

            await interaction.followup.send(f"Now is playing {songs[0]['SongName']}")
            voice_client.play(discord.FFmpegPCMAudio(dlurl, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self, voice_client))
        
        else:
            await interaction.response.send_message("Not valid url")
            return


    @app_commands.command(name='skip', description = 'To skip a song')
    async def skip(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        
        if voice_client == None:
            await interaction.response.send_message("I am not in a voice channel")
            return
        if voice_client.is_playing() == False:
            await interaction.response.send_message("Now is not playing song")
            return
        
        if len(self.queue) == 1:
            await interaction.response.send_message("There is no song left")
            if self.mode != 'ai':
                self.end = 1
            voice_client.stop()
            return
        else:
            if "https://youtube.com/playlist?list=" in self.playlist_url:
                await interaction.response.send_message(f"Now is playing {self.queue[1]}")
                voice_client.stop()
                return
                
                
            elif "open.spotify.com/playlist/" in self.playlist_url or "open.spotify.com/album/" in self.playlist_url:
                await interaction.response.send_message(f"Now is playing {self.queue[1]}")
                voice_client.stop()
                return
            
            elif self.mode == 'ai':
                await interaction.response.send_message(f"Now is playing {self.queue[1]}")
                voice_client.stop()
                return
            
            
    
    @app_commands.command(name='info', description = 'To get what is playing now')
    async def info(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client == None:
            await interaction.response.send_message("I am not in a voice channel")
            return
        if voice_client.is_playing() == False:
            await interaction.response.send_message("Now is not playing song")
            return
        await interaction.response.send_message(f"Now is playing {self.queue[0]}")
    
    @app_commands.command(name = 'shuffle', description = 'To switch to shuffle mode')
    async def shuffle(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client == None:
            await interaction.response.send_message("I am not in a voice channel")
            return
        if voice_client.is_playing() == False:
            await interaction.response.send_message("Now is not playing song")
            return
        
        if "open.spotify.com/playlist/" not in self.playlist_url and "open.spotify.com/album/" not in self.playlist_url and "https://youtube.com/playlist?list=" not in self.playlist_url:
            await interaction.response.send_message("You are not playing a playlist")
            return

        if "open.spotify.com/playlist/" in self.playlist_url or "open.spotify.com/album/" in self.playlist_url:
            if len(self.queue) <= 1:
                await interaction.response.send_message("There is no song left")
                return
            elif self.mode == 'shuffle':
                await interaction.response.send_message("It is already shuffle mode")
                return
            else:
                playing = self.queue[0]
                random.shuffle(self.queue)
                self.queue.remove(playing)
                self.queue.insert(0, playing)
                self.mode = 'shuffle'
                await interaction.response.send_message("Switch to shuffle mode successfully")
        elif "https://youtube.com/playlist?list=" in self.playlist_url:
            if len(self.yt_url_list) <= 1:
                await interaction.response.send_message("There is no song left")
                return
            elif self.mode == 'shuffle':
                await interaction.response.send_message("It is already shuffle mode")
                return
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
                await interaction.response.send_message("Switch to shuffle mode successfully")
        else:
            return
        
    @app_commands.command(name = 'loop', description =  'To switch to loop mode')
    async def loop(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        
        if voice_client == None:
            await interaction.response.send_message("I am not in a voice channel")
            return
        if voice_client.is_playing() == False:
            await interaction.response.send_message("Now is not playing song")
            return
        
        if "open.spotify.com/playlist/" not in self.playlist_url and "open.spotify.com/album/" not in self.playlist_url and "https://youtube.com/playlist?list=" not in self.playlist_url:
            await interaction.response.send_message("You are not playing a playlist")
            return

        if self.mode == 'loop':
            await interaction.response.send_message("It is already loop mode")
            return
        else:
            if "open.spotify.com/playlist/" in self.playlist_url or "open.spotify.com/album/" in self.playlist_url:
                playing = self.queue[0]
                songs = link.get_spotify_playlist(self.playlist_url)
                new_list = []
                status = False
                for i in range(len(songs)):   #直到找到現在正在播放的歌曲再加入佇列
                    songName_artist = songs[i]['songname'] + " by " + songs[i]['artist']
                    if songName_artist == playing or status == True:
                        new_list.append(songName_artist)
                        status = True
                self.queue = new_list
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
            else:
                pass
            self.mode = 'loop'
            await interaction.response.send_message("Switch to loop mode successfully")
            return

    @app_commands.command(name = 'ai', description = 'switch to ai suggest mode, only support spotify track')
    async def ai(self, interaction: discord.Interaction):
        if "open.spotify.com/track/" in self.Spotify_track_url:
            self.mode = 'ai'
            await interaction.response.send_message("Switch to ai mode successfully")
            return
        else:
            await interaction.response.send_message("You are not playing Spotify track")
            return

    @app_commands.command(name = 'pause', description = 'To pause the playing song')
    async def pause(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        
        if voice_client == None:
            await interaction.response.send_message("I am not in a voice channel")
            return
        if voice_client.is_playing() == False:
            await interaction.response.send_message("Now is not playing song")
            return
        else:
            voice_client.pause()
            await interaction.response.send_message("Paused")
            return
    
    @app_commands.command(name = 'resume', description = 'To resume playing')
    async def resume(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        
        if voice_client == None:
            await interaction.response.send_message("I am not in a voice channel")
            return
        if voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("Resumed")
            return
        else:
            await interaction.response.send_message("Now is not pausing")
            return
        
    @app_commands.command(name = 'show', description = 'To show the queue')
    async def show(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        
        if voice_client == None:
            await interaction.response.send_message("I am not in a voice channel")
            return
        if voice_client.is_playing() == False:
            await interaction.response.send_message("Now is not playing song")
            return
        else:
            output = ""
            i = 0
            for element in self.queue:
                output += (element + " ")
                if i%5 == 0 and i != 0:
                    output += "\n"
                i += 1
            await interaction.response.send_message(f"{output}")


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
                if len(voice_client.channel.members) != 1:
                    time = 0
                if time == 30:   #30秒時
                    self.end = 1
                    await voice_client.disconnect()   #斷線
                if not voice_client.is_connected():   #若無連線則跳出迴圈
                    break
    
    def next_song(self, voice_client):
        if self.end == 1:
            print("session end")
            self.queue = []   #清空佇列
            self.yt_url_list = []
            return
        if len(self.queue) == 0:
            return
        if len(self.queue) == 1:   #若音樂佇列只剩最後一首歌(已經播放完畢)
            if self.mode == "loop":
                self.queue = []   #清空佇列
                self.yt_url_list = []
                if "https://youtube.com/playlist?list=" in self.playlist_url:
                    id = self.playlist_url.replace('https://youtube.com/playlist?list=', '')   #取得播放清單id
                    num = id.find('&')
                    id = id[:num]
                    songs = link.get_yt_playlist(id)
                    dlurl = search.url_search_yt(songs[0]['url'])
                    for i in range(len(songs)):
                        self.queue.append(songs[i]['SongName'])
                        self.yt_url_list.append(songs[i]['url'])
                    try:
                        voice_client.play(discord.FFmpegPCMAudio(dlurl, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self, voice_client))
                    except Exception:
                        Music.next_song(self, voice_client)
                elif "open.spotify.com/playlist/" in self.playlist_url or "open.spotify.com/album/" in self.playlist_url:
                    songs = link.get_spotify_playlist(self.playlist_url)
                    for i in range(len(songs)):
                        songName_artist = songs[i]['songname'] + " by " + songs[i]['artist']
                        self.queue.append(songName_artist)   #將擷取到的音樂輸入佇列
                    songName_artist = songs[0]['songname'] + " by " + songs[0]['artist']
                    url = search.search_yt(songName_artist)
                    try:
                        voice_client.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self, voice_client))
                    except Exception:
                        Music.next_song(self, voice_client)
            elif self.mode == "ai":
                songs = ai.ai_get_songs(self.queue[0])
                self.queue.pop(0)
                song1 = songs[0]['title']+" by "+songs[0]['artist']
                song2 = songs[1]['title']+" by "+songs[1]['artist']
                self.queue.extend([song1,song2])
                url = search.search_yt(song1)
                try:
                    voice_client.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self, voice_client))
                except Exception:
                    voice_client.stop()
            else:
                self.queue = []   #清空佇列
                self.yt_url_list = []
                self.end = 1
                voice_client.stop()
                return
            
        else:
            if "https://youtube.com/playlist?list=" in self.playlist_url:
                url = self.yt_url_list[1]
                self.yt_url_list.pop(0)
                self.queue.pop(0)
                dlurl = search.url_search_yt(url)
                try:
                    voice_client.play(discord.FFmpegPCMAudio(dlurl, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self, voice_client))
                except Exception:   #若下一首不可播放則再下一首
                    Music.next_song(self, voice_client)
                    
            elif "open.spotify.com/playlist/" in self.playlist_url or "open.spotify.com/album/" in self.playlist_url or self.mode == 'ai':
                url = search.search_yt(self.queue[1])
                self.queue.pop(0)
                try:
                    voice_client.play(discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after = lambda x: Music.next_song(self, voice_client))
                except Exception:
                    Music.next_song(self, voice_client)
                    

async def setup(bot):
    await bot.add_cog(Music(bot))