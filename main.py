import hikari
import lightbulb
import os
import datetime
from dotenv import load_dotenv

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

#Delete X amount of messages from a channel. Limited to messages < 14 days old by Discord.
@bot.command
@lightbulb.option('amount', 'How many messages do you want deleted?')
@lightbulb.command('purge', 'Purge the channel of a set number of messages.')
@lightbulb.implements(lightbulb.SlashCommand)
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