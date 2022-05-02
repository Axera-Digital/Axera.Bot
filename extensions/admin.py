import asyncio
import datetime
import hikari
import lightbulb

admin_plugin = lightbulb.Plugin("Admin")

#implement a slash command group // they can't do anything so we just pass it // use it for organizing commands
@admin_plugin.command
@lightbulb.command('admin', 'Commands that deal with admin things')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def admin():
	pass

@admin.command
@lightbulb.add_checks(lightbulb.checks.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option("target", "The member to get information about. Leave blank for your info.", hikari.User, required=False)
@lightbulb.command("whois", "Get info on a server member.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def userinfo(ctx: lightbulb.Context):
    target = ctx.get_guild().get_member(ctx.options.target or ctx.user)

    if not target:
        await ctx.respond("That user is not in the server.")
        return

    created_at = int(target.created_at.timestamp())
    joined_at = int(target.joined_at.timestamp())
    roles = (await target.fetch_roles())[1:]  # All but @everyone

    embed = (
        hikari.Embed(
            title=f"User Info - {target.display_name}",
            description=f"ID: `{target.id}`",
            colour=0x3B9DFF,
            timestamp=datetime.now().astimezone(),
        )
        .set_footer(
            text=f"Requested by {ctx.member.display_name}",
            icon=ctx.member.avatar_url or ctx.member.default_avatar_url,
        )
        .set_thumbnail(target.avatar_url or target.default_avatar_url)
        .add_field(
            "Bot?",
            str(target.is_bot),
            inline=True,
        )
        .add_field(
            "Created account on",
            f"<t:{created_at}:d>\n(<t:{created_at}:R>)",
            inline=True,
        )
        .add_field(
            "Joined server on",
            f"<t:{joined_at}:d>\n(<t:{joined_at}:R>)",
            inline=True,
        )
        .add_field(
            "Roles",
            ", ".join(r.mention for r in roles),
            inline=False,
        )
    )

    await ctx.respond(embed)

#ban a user from the Discord server
@admin.command
@lightbulb.add_checks(lightbulb.checks.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
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
    await ctx.respond(f"{ctx.options.user.mention} got the ban hammer!\n**Reason:** {ctx.options.reason or 'None provided.'}")

#purge the channel
@admin.command
@lightbulb.option("messages", "The number of messages to purge.", type=int, required=True)
@lightbulb.command("purge", "Purge messages.", aliases=["clear"])
@lightbulb.implements(lightbulb.SlashSubCommand)
async def purge_messages(ctx: lightbulb.Context):
    num_msgs = ctx.options.messages
    channel = ctx.channel_id

    # If the command was invoked using the PrefixCommand, it will create a message
    # before we purge the messages, so you want to delete this message first
    if isinstance(ctx, lightbulb.PrefixContext):
        await ctx.event.message.delete()

    msgs = await ctx.bot.rest.fetch_messages(channel).limit(num_msgs)
    await ctx.bot.rest.delete_messages(channel, msgs)

    resp = await ctx.respond(f"{len(msgs)} messages deleted")

    await asyncio.sleep(5)
    await resp.delete()


def load(bot: lightbulb.BotApp):
    bot.add_plugin(admin_plugin)