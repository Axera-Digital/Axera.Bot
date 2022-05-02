import datetime
from operator import ge
import hikari
import lightbulb

gen_plugin = lightbulb.Plugin("General")



def load(bot: lightbulb.BotApp):
    bot.add_plugin(gen_plugin)