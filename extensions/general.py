import hikari
import lightbulb

gen_plugin = lightbulb.Plugin("General")

#DO NOT NEED A GROUP

def load(bot: lightbulb.BotApp):
    bot.add_plugin(gen_plugin)