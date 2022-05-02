import random
import hikari
import lightbulb

plugin = lightbulb.Plugin("Events")

@plugin.listener(lightbulb.CommandErrorEvent)
async def on_command_err(event: lightbulb.CommandErrorEvent):

    if isinstance(event.exception, lightbulb.CommandNotFound):
        return None

    if isinstance(event.exception, lightbulb.CommandIsOnCooldown):
        return await event.context.respond('**The command is on cooldown still!**', flags=hikari.MessageFlag.EPHEMERAL)

    if isinstance(event.exception, lightbulb.NotOwner):
        return await event.context.respond('**You are not the owner!**', flags=hikari.MessageFlag.EPHEMERAL)

    if isinstance(event.exception, lightbulb.BotMissingRequiredPermission):
        return await event.context.respond('**I am missing the required permissions to do that!**', flags=hikari.MessageFlag.EPHEMERAL)

    if isinstance(event.exception, lightbulb.MissingRequiredPermission):
        return await event.context.respond('**You do not have permission to do that!**', flags=hikari.MessageFlag.EPHEMERAL)

    print(event.exception)
    return await event.context.respond('**An error has occured when executing this command.**', flags=hikari.MessageFlag.EPHEMERAL)

def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)