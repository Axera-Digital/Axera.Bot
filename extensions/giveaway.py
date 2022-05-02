import asyncio
import datetime
import random
import hikari
import lightbulb

giveaway_plugin = lightbulb.Plugin("Giveaway")



def load(bot: lightbulb.BotApp):
    bot.add_plugin(giveaway_plugin)