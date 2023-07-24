import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from admin_cog import admin_cog
from help_cog import help_cog
from music_cog import music_cog

load_dotenv()


TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!",intents=intents)

@bot.event
async def on_ready():
    bot.remove_command("help")
    await bot.add_cog(help_cog(bot))
    await bot.add_cog(music_cog(bot))
    await bot.add_cog(admin_cog(bot))
bot.run(TOKEN)