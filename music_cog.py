from typing import Optional
import discord
import json
import os
from dotenv import load_dotenv
from discord.ext import commands
from yt_dlp import YoutubeDL
from logging_result import filter_info
from error_logger import log_error, log_info  # for logging error
from datetime import datetime
from predicate_checks import in_same_voice_channel, user_in_voice_channel

load_dotenv()


class MusicButtons(discord.ui.View):
    def __init__(self, queue, vc):
        super().__init__()
        self.queue = queue
        self.vc = vc

    @discord.ui.button(label="Click Here!", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        button1 = [x for x in self.children if x.custom_id == "danger"][0]
        button1.disabled = True
        button1.label = "No more danger"
        
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Danger!", style=discord.ButtonStyle.blurple, custom_id="danger")
    async def danger_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.edit_original_response("!!!")


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.YDL_OPTIONS = json.loads(os.getenv('YDL_OPTIONS'))
        self.FFMPEG_OPTIONS = json.loads(os.getenv('FFMPEG_OPTIONS'))
        self.voice_clients = {}

    async def get_embed(self, queue):
        current = queue[0][0]
        embed = discord.Embed(
            title=current["title"],
            url=current["webpage_url"],
            colour=0x00b0f4,
            timestamp=datetime.now()
            # description=current["description"]
        )
        embed.set_author(name="Music Queue")
        embed.add_field(name="Duration", value=current["duration_string"])

        for i in range(1, len(queue)):
            listitem = queue[i][0]
            inner_embed = discord.Embed(
                title=f'🔊{listitem["title"]}',
                url=listitem["webpage_url"],
                colour=0x00b0f4,
                description=listitem["description"]
            )
            # Set small thumbnail for inner embed
            inner_embed.set_thumbnail(url=listitem["thumbnail"])
            # Empty value for spacing
            embed.add_field(
                name=f'{i + 1}. - {listitem["title"] }  {listitem["duration_string"]}', value=" ", inline=False)

        embed.set_thumbnail(url=current["thumbnail"])

        return embed

    # return a list of available songs

    async def set_guild_data(self, ctx, voice_channel):
        if not self.voice_clients.get(ctx.guild.id, None):
            self.voice_clients[ctx.guild.id] = {
                'vc': await voice_channel.connect(),
                'queue': []
            }
        return self.voice_clients.get(ctx.guild.id)

    async def get_guild_data(self, ctx):
        return self.voice_clients.get(ctx.guild.id, None)

    async def remove_guild_data(self, ctx):
        self.voice_clients.pop(ctx.guild.id, None)

    async def get_user_voice_channel(self, ctx):
        return ctx.author.voice.channel if ctx.author.voice else None

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)
                return filter_info(info)
            except Exception as e:
                log_error(e)
                return False

    def play_next(self, gd):
        vc = gd['vc']
        queue = gd['queue']
        if len(queue) == 0:
            vc.stop()
            queue = []
            return
        else:
            vc.stop()
            queue.pop(0)

        if len(queue) > 0:
            m_url = queue[0][0]['source']
            vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                    after=lambda e: self.play_next(gd))
        else:
            vc.stop()
            gd['queue'] = []

    async def play_music(self, ctx):
        gd = await self.get_guild_data(ctx)
        vc = gd['vc']
        queue = gd['queue']
        log_info(f"play_music() is called")
        if len(queue) > 0:
            m_url = queue[0][0]['source']

            if not vc or not vc.is_connected():
                vc = await queue[0][1].connect()
                if not vc:
                    await ctx.send("Could't connect to the voice channel")
                    return
            else:
                await vc.move_to(queue[0][1])
            vc.play(discord.FFmpegPCMAudio(
                m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(gd))
        else:
            vc.stop()

    @commands.command(name="queue", aliases=["q"], help="Lists the musics in the queue")
    @in_same_voice_channel()
    async def queue(self, ctx, *args):
        gd = await self.get_guild_data(ctx)
        queue = gd['queue']
        vc = gd['vc']
        log_info(f"!queue is called by {ctx.author}")

        if len(queue):
            embedded_queue = await self.get_embed(queue)
            await ctx.send(embed=embedded_queue)
            await ctx.send(view=MusicButtons(queue, vc))
        else:
            await ctx.send("No music in the queue.")

    @commands.command(name="play", aliases=["p"], help="It plays the selected song from Youtube")
    @user_in_voice_channel()
    async def play(self, ctx, *args):
        voice_channel = await self.get_user_voice_channel(ctx)
        gd = await self.set_guild_data(ctx, voice_channel)
        vc = gd['vc']
        queue = gd['queue']
        query = " ".join(args)
        if vc.is_paused() and queue != []:
            vc.resume()
        else:
            songs = self.search_yt(query)
            if type(songs) == type(True) or not len(songs):
                await ctx.send("Couldn't find the requested song. Incorrect format, try a different keyword")
            else:
                await ctx.send("Song added to the queue")
                for song in songs:
                    queue.append([song, voice_channel])
                    await ctx.send(f"kpbs: {song['abr']}")

                if vc.is_playing() == False:
                    await self.play_music(ctx)
                await self.queue(ctx)

    @commands.command(name="pause", aliases=["pouse"], help="Pauses the current song being played")
    @in_same_voice_channel()
    async def pause(self, ctx, *args):
        gd = await self.get_guild_data(ctx)
        vc = gd['vc']
        if vc.is_playing():
            vc.pause()

    @commands.command(name="resume", aliases=["r", "res"], help="Resumes the last paused song")
    @in_same_voice_channel()
    async def resume(self, ctx, *args):
        gd = await self.get_guild_data(ctx)
        vc = gd['vc']
        if vc.is_paused():
            vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Skips the currently playing song")
    @in_same_voice_channel()
    async def skip(self, ctx, *args):
        log_info(f"!skip is called by {ctx.author}")
        gd = await self.get_guild_data(ctx)
        vc = gd['vc']
        queue = gd['queue']
        if vc != None and vc.is_connected():
            vc.stop()
            await self.queue(ctx)
            await self.play_music(ctx)

    @commands.command(name="clear", aliases=["c"], help="Stops the current song and clears the music queue")
    @in_same_voice_channel()
    async def clear(self, ctx, *args):
        gd = await self.get_guild_data(ctx)
        vc = gd['vc']
        queue = gd['queue']
        if vc != None:
            vc.stop()
            gd['queue'] = []
        await ctx.send("Music queue cleared")

    @commands.command(name="leave", aliases=["l", "d", "disconnect"], help="Kick the bot from voice channel")
    @in_same_voice_channel()
    async def leave(self, ctx, *args):
        gd = await self.get_guild_data(ctx)
        vc = gd['vc']
        await vc.disconnect()
        await self.remove_guild_data(ctx)
