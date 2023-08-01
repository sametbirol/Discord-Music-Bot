

# help_cog.py
import discord
from discord.ext import commands


class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.text_channel_text = []
        embed = discord.Embed(
            colour=discord.Colour.brand_green()
        )
        embed.set_author(name='Help')
        embed.add_field(
            name='!help', value='displays all the available commands', inline=False)
        embed.add_field(name='!p <keywords>',
                        value='finds the song on youtube and plays it in your current channel.\
                          Will resume playing the current song if it was paused', inline=False)
        embed.add_field(
            name='!q', value='displays the current music queue', inline=False)
        embed.add_field(
            name='!skip', value='skips the current song being played', inline=False)
        embed.add_field(
            name='!clear', value='stops the music and clears the queue', inline=False)
        embed.add_field(
            name='!leave', value='disconnects the bot from the voice channel', inline=False)
        embed.add_field(
            name='!pause', value='pauses the current song being played', inline=False)
        embed.add_field(
            name='!resume', value='resumes playing the current song', inline=False)
        self.embed = embed
    # Move the on_ready function outside the __init__ method

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_text.append(channel)

        await self.send_to_all("I am online")

    async def send_to_all(self, msg):
        for text_channel in self.text_channel_text:
            await text_channel.send(msg)

    @commands.command(name="help", help="Displays all the available commands")
    async def help(self, ctx):
        await ctx.send(embed=self.embed, ephemeral=True)
