import discord
import json
import os
from dotenv import load_dotenv
from discord.ext import commands
from yt_dlp import YoutubeDL
from logging_result import log_music_search_result
from error_logger import log_error,log_info # for logging error

load_dotenv()


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = False
        self.is_paused = False
        self.music_queue = []

        self.YDL_OPTIONS = json.loads(os.getenv('YDL_OPTIONS'))

        self.FFMPEG_OPTIONS = json.loads(os.getenv('FFMPEG_OPTIONS'))
        self.vc = None
    def reset(self):
        self.is_playing = False
        self.is_paused = False
        self.music_queue = []
    # return a list of available songs
    def search_yt(self, item,guildID):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)
                collectiveList = log_music_search_result(guildID, item, info)
                return collectiveList
            except Exception as e:
                log_error(e)
                return False

    def play_next(self):
        log_info("play_next() is called")
        if len(self.music_queue) == 0:
            log_info("Since music queue is empty, returned")
            self.reset()
            return
        else :
            log_info("will pop the queue",self.music_queue)
            self.music_queue.pop(0)
            

        if len(self.music_queue) > 0:
            self.is_playing = True
            self.is_paused = False
            m_url = self.music_queue[0][0]['source']
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next)
        else:
            self.reset()

    async def play_music(self, ctx):
        log_info(f"play_music() is called")
        if len(self.music_queue) > 0:
            self.is_playing = True
            self.is_paused = False
            m_url = self.music_queue[0][0]['source']

            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()
                if self.vc == None:
                    await ctx.send("Could't connect to a voice channel")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next)
        else:
            self.reset()

    @commands.command(name="play", aliases=["p"], help="It plays the selected song from Youtube")
    async def play(self, ctx, *args):
        log_info(f"!play is called by {ctx.author}")
        query = " ".join(args)
        try:
            voice_channel = ctx.author.voice.channel
        except Exception as e:
            log_error(e)
            voice_channel = None
            await ctx.send("Conncet to a voice channel please.")
            return
        if self.is_paused and query == "":
            self.vc.resume()
        else:
            songs = self.search_yt(query,ctx.guild.id)
            log_error(songs)
            if type(songs) == type(True) or not len(songs):
                await ctx.send("Couldn't find the requested song. Incorrect format, try a different keyword")
            else:
                await ctx.send("Song added to the queue")
                for song in songs:
                    self.music_queue.append([song, voice_channel])
                    await ctx.send(f"kpbs: {song['abr']}")
                    

                if self.is_playing == False:
                    await self.play_music(ctx)
                    log_info(f"!queue is called internally")
                    await self.queue(ctx)
                else:
                    log_info(f"!queue is called internally")
                    await self.queue(ctx)

    @commands.command(name="pause", aliases=["pouse"], help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        log_info(f"!pause is called by {ctx.author}")
        if self.vc == None:
            return
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()

    @commands.command(name="resume", aliases=["r", "res"], help="Resumes the last paused song")
    async def resume(self, ctx, *args):
        log_info(f"!resume is called by {ctx.author}")
        if self.vc == None:
            return
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Skips the currently playing song")
    async def skip(self, ctx, *args):
        log_info(f"!skip is called by {ctx.author}")
        if self.vc != None and self.vc.is_connected():
            self.vc.stop()
            self.music_queue.pop(0)
            await self.play_music(ctx)

    @commands.command(name="queue", aliases=["q"], help="Lists the musics in the queue")
    async def queue(self, ctx, *args):
        log_info(f"!queue is called by {ctx.author}")
        retval = ""
        for i in range(0, len(self.music_queue)):
            if i > 9:
                break
            retval += f'{i + 1}. {"Now playing:" if i == 0 else " "} {self.music_queue[i][0]["title"] }  URL: {self.music_queue[i][0]["source"][:50]} \n'
        if retval != "":
            await ctx.send(f'Queue:\n{retval}')
        else:
            await ctx.send("No music in the queue.")

    @commands.command(name="clear", aliases=["c"], help="Stops the current song and clears the music queue")
    async def clear(self, ctx, *args):
        if self.vc == None:
            self.reset()
            return
        if self.vc != None and self.is_playing:
            self.vc.stop()
            self.reset()
        await ctx.send("Music queue cleared")

    @commands.command(name="leave", aliases=["l", "d", "disconnect"], help="Kick the bot from voice channel")
    async def leave(self, ctx, *args):
        if self.vc == None:
            return
        self.reset()
        await self.vc.disconnect()
        self.vc = None
