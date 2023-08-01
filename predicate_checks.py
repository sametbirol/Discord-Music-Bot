from discord.ext.commands import check

def in_same_voice_channel():
    def predicate(ctx):
        async def funcc(self, ctx, *args):
            user_voice_channel = ctx.author.voice.channel if ctx.author.voice else None
            bot_voice_channel = ctx.guild.me.voice.channel if ctx.guild.me.voice else None
            guild_data = self.voice_clients.get(ctx.guild.id, None)

            if not guild_data:
                await ctx.send("Please first play a song so that I can connect.")
                return False

            if not user_voice_channel:
                await ctx.send("Connect to a voice channel, please.")
                return False

            if not bot_voice_channel:
                await ctx.send("The bot is not connected to a voice channel.")
                return False

            if user_voice_channel != bot_voice_channel:
                await ctx.send("You and the bot must be in the same voice channel to use this command.")
                return False

            return True

        return funcc

    return check(predicate)

def user_in_voice_channel():
    async def in_voice_channel(ctx):
        user_voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        bot_voice_channel = ctx.guild.me.voice.channel if ctx.guild.me.voice else None

        if not user_voice_channel:
            await ctx.send("Connect to a voice channel, please.")
            return False

        if bot_voice_channel and bot_voice_channel != user_voice_channel:
            await ctx.send("Connect to the same voice channel as me.")
            return False
        return True

    return check(in_voice_channel)



# def with_guild_data():
#     def decorator(func):
#         async def wrapper(self, ctx, *args, **kwargs):
#             gd = await self.voice_clients.get(ctx.guild.id, None)
#             vc = gd['vc']
#             queue = gd['queue']
#             return await func(self, ctx, vc, queue, *args, **kwargs)
#         return wrapper
#     return decorator

