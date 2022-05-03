import os
import lightbulb
import hikari
import miru
from typing import Union

tickets_plugin = lightbulb.Plugin('Tickets')



def load(bot : lightbulb.BotApp) -> None:
	bot.add_plugin(tickets_plugin)