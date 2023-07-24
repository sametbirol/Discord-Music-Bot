import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

from help_cog import help_cog
from music_cog import music_cog

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()

bot = commands.AutoShardedBot(command_prefix="!",intents=intents)



@bot.event
async def on_ready():
    print(f'{bot.user.name} connected to Discord!')
    bot.remove_command("help")
    await bot.add_cog(help_cog(bot))
    await bot.add_cog(music_cog(bot))
    print(f'Configurations connecteddd to Discord!!')



bot.run(TOKEN)