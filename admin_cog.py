from discord.ext import commands
from error_logger import log_error, log_info  # for logging error
import os
from dotenv import load_dotenv

load_dotenv()


class admin_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin = int(os.getenv('ADMIN_ID'))

    @commands.command(name="delete_messages", aliases=["del"], help="Deletes messages : delete_messages <Count>")
    async def delete_messages(self, ctx, num_messages: int):
        if ctx.author.id != self.admin:
            await ctx.send('You are not authorized to use this command')
            return
        channel = ctx.channel
        messages = [message async for message in channel.history(limit=num_messages)]
        await ctx.send(f'I made {len(messages)} moderation actions.')
        await channel.delete_messages(messages)
