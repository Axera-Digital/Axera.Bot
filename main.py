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