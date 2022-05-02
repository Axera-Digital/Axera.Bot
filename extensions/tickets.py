import os
import lightbulb
import hikari
import miru
from typing import Union

tickets_plugin = lightbulb.Plugin('Tickets')

async def create_ticket(ctx : Union[lightbulb.Context, miru.Context], reason : Union[str, None]) -> hikari.GuildTextChannel:
	if not id:
		id = 0
	else:
		id = id[0]
	
	user_overwrites = hikari.PermissionOverwrite(
		id = ctx.member.id,
		type = hikari.PermissionOverwriteType.MEMBER,
		allow = (
			hikari.Permissions.VIEW_CHANNEL |
			hikari.Permissions.READ_MESSAGE_HISTORY |
			hikari.Permissions.SEND_MESSAGES
		),
	)
	staff_overwrites = hikari.PermissionOverwrite(
		id = os.getenv('STAFFROLEID'),
		type = hikari.PermissionOverwriteType.ROLE,
		allow = (
			hikari.Permissions.VIEW_CHANNEL |
			hikari.Permissions.READ_MESSAGE_HISTORY |
			hikari.Permissions.SEND_MESSAGES |
			hikari.Permissions.MANAGE_MESSAGES
		),
	)
	everyone_overwrites = hikari.PermissionOverwrite(
		id = ctx.guild_id,
		type = hikari.PermissionOverwriteType.ROLE,
		deny = (
			hikari.Permissions.VIEW_CHANNEL |
			hikari.Permissions.READ_MESSAGE_HISTORY
		),
	)
	ticket_channel = await ctx.get_guild().create_text_channel(f'ticket-id-{id + 1}', category = os.getenv('TICKETSCATEGORYID'), permission_overwrites= [user_overwrites, staff_overwrites, everyone_overwrites])

	await ticket_channel.send(
		f"{ctx.member.mention}",
		embed = hikari.Embed(
			title = f"Ticket #{id + 1}",
			description = (
				f"Hey {ctx.member.mention}, thanks for choosing Axera.Digital! A staff member will soon get in touch with you shortly."
                ""
                "In the meantime, please tell us why you have opened this ticket so we can help you faster."
			),
			colour = 0x479760
		).add_field(
			"Reason for opening ticket:",
			reason if reason else f"No reason was provided"
		),
		user_mentions = [ctx.member.id]
	)

	await ctx.app.rest.create_message(
		os.getenv('TICKETSLOGCHANNELID'), 
		embed = hikari.Embed(
			title = f"Ticket #{id + 1} opened",
			description = f"Reason: {reason}",
			colour = 0x479760
		).set_author(
			name = f"{ctx.member} ({ctx.member.id})",
			icon = ctx.member.display_avatar_url or ctx.member.default_avatar_url
		)
	)

	return ticket_channel

async def delete_ticket(ctx : lightbulb.Context, reason : Union[str, None], db) -> None:
	await ctx.app.rest.create_message(
		os.getenv('TICKETSLOGCHANNELID'),
		embed = hikari.Embed(
			title = f"Ticket #{db[0]} closed.",
			description = f"Reason for closing ticket: {reason}",
			colour = 0xf8312f
		).set_author(
			name = f"{ctx.author} ({ctx.author.id})",
			icon = ctx.author.display_avatar_url or ctx.author.default_avatar_url
		)
	)
	
	message_history = await ctx.app.rest.fetch_messages(
		ctx.channel_id
	).sort(key = lambda x : x.id , reverse = False)

	user = ctx.get_guild().get_member(db[1])

	if not user:
		user = await ctx.bot.rest.fetch_user(db[1])

	with open("TicketTranscript.txt", "w+") as f:
		f.write(f"Ticket ID #{db[0]} opened by {user} ({user.id}). All times in this transcript are UTC.\n\n")
		i = 1
		for message in message_history:
			str = f"[{message.timestamp.day}-{message.timestamp.month}-{message.timestamp.year} {message.timestamp.hour}:{message.timestamp.minute}:{message.timestamp.second}] {message.author} ({message.author.id}) : {message.content}"
			if message.embeds:
				for embed in message.embeds:
					str = str + f" (type : embed, "
					if embed.title:
						str = str + f"title : '{embed.title}', "
					if embed.description:
						str = str + f"description : '{embed.description}', "
					if embed.fields:
						for field in embed.fields:
							str = str + f"field '{field.name}' : '{field.value}', "
					str = str + f")"
			if message.attachments:
				for attachment in message.attachments:
					str = str + f" (type : attachment, filetype : '{attachment.extension}', filename : '{attachment.filename}')"
					await ctx.app.rest.create_message(
						os.getenv('TICKETSLOGCHANNELID'),
						f"Attachment {i}.{attachment.extension}",
						attachment = hikari.Bytes(await attachment.read(), f"attachment {i}.{attachment.extension}")
					)
					i += 1
			str = str + f"\n"
			f.write(str)

	await ctx.respond(
		os.getenv('TICKETSLOGCHANNELID'),
		f"Transcript for Ticket #{db[0]}",
		attachment = hikari.File("TicketTranscript.txt", f"Ticket_No_{db[0]}_Transcript.txt")
	)

	await ctx.get_channel().delete()


@tickets_plugin.command
@lightbulb.command('ticket', "All ticket related commands", auto_defer = True)
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def ticket_group(ctx : lightbulb.Context) -> None:
	await ctx.respond(
		embed = hikari.Embed(
			title = "You are forgetting something...",
			description = "This command has subcommands.\nType `?help ticket` to see them all or just use slash commands tbh.",
			colour = 0xf8312f
		)
	)

@ticket_group.child
@lightbulb.option('reason', 'Reason for opening the ticket', type = str, modifier = lightbulb.OptionModifier.CONSUME_REST, required = False, default = "No reason was given.")
@lightbulb.command('open', "Open a new ticket to get assistance from staff or give suggestions.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def ticket_open(ctx : lightbulb.Context) -> None:
	ticket_channel = await create_ticket(ctx, ctx.options.reason)
	
	await ctx.respond(
		f"{ctx.author.mention}, Ticket created in {ticket_channel.mention}.", 
		flags = hikari.MessageFlag.EPHEMERAL,
		delete_after = 10,
		user_mentions = [ctx.author]
	)

@ticket_group.child
@lightbulb.option('reason', 'Reason for closing the ticket', type = str, modifier = lightbulb.OptionModifier.CONSUME_REST, required = False, default = "No reason was given.")
@lightbulb.command('close', "Close the ticket.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def ticket_close(ctx : lightbulb.Context) -> None:
	
	await ctx.respond("<a:bot_loading:809318632723185714> Closing this ticket. Please wait.")
	await delete_ticket(ctx, ctx.options.reason)

@ticket_group.child
@lightbulb.option('user', "The user to add to the ticket", type = hikari.User, required = True)
@lightbulb.command('adduser', "Add a user to this ticket.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def ticket_adduser(ctx : lightbulb.Context) -> None:
	
	user : hikari.User = ctx.options.user

	await ctx.get_channel().edit_overwrite(
		user,
		target_type = hikari.PermissionOverwriteType.MEMBER,
		allow = (
			hikari.Permissions.VIEW_CHANNEL |
			hikari.Permissions.READ_MESSAGE_HISTORY |
			hikari.Permissions.SEND_MESSAGES
		),
	)

	await ctx.respond(f"Added {user.mention} ({user.id}) to the ticket.")

@ticket_group.child
@lightbulb.option('user', 'The user to remove from this ticket', type = hikari.User, required = True)
@lightbulb.command('removeuser', "Remove a user from this ticket.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def ticket_removeuser(ctx : lightbulb.Context) -> None:
	
	await ctx.get_channel().edit_overwrite(
		ctx.options.user,
		target_type = hikari.PermissionOverwriteType.MEMBER,
		deny = (
			hikari.Permissions.VIEW_CHANNEL |
			hikari.Permissions.READ_MESSAGE_HISTORY |
			hikari.Permissions.SEND_MESSAGES
		),
	)

	await ctx.respond(f"Removed {ctx.options.user.mention} ({ctx.options.user.id}) from the ticket.")

class TicketButton(miru.View):
	def __init__(self,) -> None:
		super().__init__(timeout=None, autodefer=True)
	
	@miru.button(label = "Open Ticket", custom_id = "ticket_create_button")
	async def create_ticket(self, button : miru.Button, ctx : miru.Context) -> None:
		ticket_channel = await create_ticket(ctx, reason = None)
		await ctx.respond(
			f"{ctx.member.mention}, Ticket created in {ticket_channel.mention}.",
			flags = hikari.MessageFlag.EPHEMERAL
		)

@ticket_group.child
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command('setbutton', "Set the button")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def tickets_button(ctx : lightbulb.Context) -> None:
	view = TicketButton()
	message = await ctx.respond(
		embed = hikari.Embed(
			title = "Create Ticket",
			description = (
				"If you want to create a ticket to submit a complaint or a suggestion privately to the Admins or Moderators then press the button below."
				"This will make a new channel below this channel that only you and the staff members can join. You can then clarify more, send attachments as evidence there."
			),
			colour = 0x6db6ea,
		),
		components = view.build() 
	)
	view.start(await message.message())

def load(bot : lightbulb.BotApp) -> None:
	bot.add_plugin(tickets_plugin)