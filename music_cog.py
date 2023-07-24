import discord
import os
import json
from dotenv import load_dotenv
from discord.ext import commands
from yt_dlp import YoutubeDL
from logging_result import log_music_search_result

load_dotenv()


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = False
        self.is_paused = False
        self.music_queue = []

        self.YDL_OPTIONS = {
            "format": "bestaudio",
            "noplaylist": False,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "128",
                }
            ],
        }

        self.FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5","options": "-vn"}
        self.vc = None

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                item = item.replace('&', r'\&')
                info = ydl.extract_info("ytsearch:%s" % item, download=False)
                # Get the server name from the voice channel (assuming it exists)
                server_name = self.bot.get_guild(
                    self.music_queue[0][1].guild.id).name if self.music_queue else "UnknownServer"
                # Log the search result
                collectiveList = log_music_search_result(server_name, item, info)
                if 'entries' in info:
                    # If it's a playlist, return a list of song dictionaries
                    return [{'source': entry['source'], 'title': entry['title']} for entry in collectiveList]
                else:
                    # If it's a single video, return it as a list to handle it like a playlist
                    return [{'source': collectiveList[0]['source'], 'title': collectiveList[0]['title']}]
            except Exception:
                return False

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            # self.is_paused = False
            m_url = self.music_queue[0][0]['source']
            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegAudio(
                m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(self))
        else:
            self.is_playing = False

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            # self.is_paused = False
            m_url = self.music_queue[0][0]['source']

            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()
                if self.vc == None:
                    await ctx.send("Could't connect to a voice channel")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(
                m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    @commands.command(name="play", aliases=["p"], help="It plays the selected song from Youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("Conncet to a voice channel please.")
        elif self.is_paused:
            self.vc.resume()
        else:
            songs = self.search_yt(query)
            if type(songs) == type(True):
                await ctx.send("Couldn't find the requested song. Incorrect format, try a different keyword")
            else:
                await ctx.send("Song added to the queue")
                for song in songs:
                    self.music_queue.append([song, voice_channel])

                if self.is_playing == False:
                    await self.play_music(ctx)

    @commands.command(name="pause", aliases=["pouse"], help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()

    @commands.command(name="resume", aliases=["r", "res"], help="Resumes the last paused song")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Skips the currently playing song")
    async def skip(self, ctx, *args):
        if self.vc != None and self.vc:
            self.vc.stop()
            await self.play_music(ctx)

    @commands.command(name="queue", aliases=["q"], help="Lists the musics in the queue")
    async def queue(self, ctx, *args):
        retval = ""
        for i in range(0, len(self.music_queue)):
            if i > 9:
                break
            retval += f'{i}. {self.music_queue[i][0]["title"] } URL: {self.music_queue[i][0]["source"][:50]} \n'
        if retval != "":
            await ctx.send(f'Queue:\n{retval}')
        else:
            await ctx.send("No music in the queue.")

    @commands.command(name="clear", aliases=["c"], help="Stops the current song and clears the music queue")
    async def clear(self, ctx, *args):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Music queue cleared")

    @commands.command(name="leave", aliases=["l", "d", "disconnect"], help="Kick the bot from voice channel")
    async def leave(self, ctx, *args):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()
