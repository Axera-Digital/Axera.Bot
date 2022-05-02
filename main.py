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


"""   Admin Commands   """

#implement a slash command group // they can't do anything so we just pass it // use it for organizing commands
@bot.command
@lightbulb.command('admin', 'Commands that deal with all things administrative')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def admin():
	pass

#ban a user from the Discord server
@admin.command
@lightbulb.add_checks(lightbulb.checks.has_roles(953091979745574942))
@lightbulb.option("reason", "Reason for the ban", required=False)
@lightbulb.option("user", "The user to ban.", type=hikari.User)
@lightbulb.command("ban", "Ban a user from the server.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def ban(ctx):
    if not ctx.guild_id:
        await ctx.respond("This command can only be used in a server.")
        return

    # create a deferred response as the ban may take longer than 3 seconds
    await ctx.respond(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    # perform the ban
    await ctx.app.rest.ban_user(ctx.guild_id, ctx.options.user.id, reason=ctx.options.reason or hikari.UNDEFINED)
    # provide feedback to the server
    await ctx.respond(f"{ctx.options.user.mention} got the ban hammer.\n**Reason:** {ctx.options.reason or 'None provided.'}")


"""   Entertainment Commands   """

#implement a slash command group // they can't do anything so we just pass it // use it for organizing commands
@bot.command
@lightbulb.command('entertainment', 'Commands that deal with music, games, and other fun things')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def entertainment():
	pass
    