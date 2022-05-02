import hikari
import lightbulb

music_plugin = lightbulb.Plugin("Music")

@music_plugin.command
@lightbulb.command('music', 'Commands that deal with music streaming')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def music():
	pass

def load(bot: lightbulb.BotApp):
    bot.add_plugin(music_plugin)