import hikari
import lightbulb
import os
import datetime
from dotenv import load_dotenv
from pkg_resources import require

load_dotenv()

#set the instance of the bot
bot = lightbulb.BotApp(
	token=os.getenv('TOKEN'), # pull the toekn from the .env files
	default_enabled_guilds=(586275458518351875), #bypass 1 hour wait time to update commands
)

#load our extensiosn
bot.load_extensions_from("./extensions/", must_exist=True)

#let's us known when the bot has fired up
#Hikari already has a nice console GUI that does this but it helps to know when your code starts
@bot.listen(hikari.StartedEvent)
async def on_started(evemt):
	print('Bot has come online!')


"""   Utility Commands  """

#implement a slash command group // they can't do anything so we just pass it // use it for organizing commands
@bot.command
@lightbulb.command('utils', 'Commands that deal with general server maintenance')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def utils():
	pass

#Delete X amount of messages from a channel. Limited to messages < 14 days old by Discord.
@utils.command
@lightbulb.option('amount', 'How many messages do you want deleted?', type=int, require=True, minimum=1)
@lightbulb.command('purge', 'Purge the channel of a set number of messages.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def purge(ctx):
    #query the channel that the command was called from for X messages < 14 days old
    messages = (
        await ctx.app.rest.fetch_messages(ctx.channel_id)
        .take_until(lambda m: datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14) > m.created_at)
        .limit({ctx.options.amount})
    )

    #if we have messages to delete, delete them and send a message with how many we purged
    if messages:
        await ctx.app.rest.delete_messages(ctx.channel_id, messages)
        await ctx.interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            f"Purged {len(messages)} messages.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
    else:
    #if there aren't any messages to delete, say so
        await ctx.interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            "Couldn\'t find any deletable messages.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


"""   Music Commands   """

#implement a slash command group // they can't do anything so we just pass it // use it for organizing commands
@bot.command
@lightbulb.command('music', 'Commands that deal with music')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def music():
	pass


"""    Bot Control Commands   """

#implement a slash command group // they can't do anything so we just pass it // use it for organizing commands
@bot.command
@lightbulb.command('bot', 'Commands that deal with controlling the bot (admin only)')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def bot():
	pass

@bot.command
@lightbulb.add_checks()
@lightbulb.command("shutdown", "Shut the bot down.", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def cmd_shutdown(ctx: lightbulb.SlashContext):
    await ctx.respond("Now shutting down.")
    await ctx.bot.close()



bot.run(
    activity=hikari.Activity(
            name="your commands • Use /help",
            type=hikari.ActivityType.LISTENING,
        )
    )