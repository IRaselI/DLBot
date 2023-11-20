import atexit
import datetime
import discord
from discord.ext import commands
import pickle
import re

try:
    autoroles: dict[int, tuple[int, int]] = pickle.load(open('autoroles.pkl', 'rb'))
    log_channels: dict[int, int] = pickle.load(open('log_channels.pkl', 'rb'))
except FileNotFoundError:
    autoroles = dict()
    log_channels = dict()
atexit.register(
    lambda: [pickle.dump(autoroles, open('autoroles.pkl', 'wb')),
             pickle.dump(log_channels, open('log_channels.pkl', 'wb'))])

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

regex = re.compile(
    r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')


# ----------------------------------------------------------------------------------------------------
# Autorole

@bot.tree.command(name='autorole', description='Setup autorole')
async def autorole(interaction: discord.Interaction, role_member: discord.Role, role_bot: discord.Role):
    """
    Setup autorole
    :param interaction: interaction
    :param role_member: role for members
    :param role_bot: role for bots
    :return:
    """
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You don't have permissions to do this", ephemeral=True)
        return
    autoroles[interaction.id] = (role_member.id, role_bot.id)
    await interaction.response.send_message('Autorole is configured', ephemeral=True)


# ----------------------------------------------------------------------------------------------------
# Moderation

@bot.tree.command(name='kick', description='Kick member')
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = ''):
    """
    kick member
    :param interaction: interaction
    :param member: member to kick
    :param reason: reason for kick
    :return:
    """
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("You don't have permissions to do this", ephemeral=True)
        return
    elif interaction.user.top_role <= member.top_role:
        await interaction.response.send_message(f"Your top role is same/lower than **{member}**'s", ephemeral=True)
        return
    if len(reason) > 0:
        reason = f'. Reason: **{reason}**'
    await member.send(f'You were kicked from **{interaction.guild}** by **{interaction.user}**{reason}')
    await member.kick(reason=reason)
    await interaction.response.send_message(f'**{member}** was kicked', ephemeral=True)


@bot.tree.command(name='ban', description='Ban member')
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = ''):
    """
    ban member
    :param interaction: interaction
    :param member: member to ban
    :param reason: reason for ban
    :return:
    """
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("You don't have permissions to do this", ephemeral=True)
        return
    elif interaction.user.top_role <= member.top_role:
        await interaction.response.send_message(f"Your top role is same/lower than **{member}**'s", ephemeral=True)
        return
    if len(reason) > 0:
        reason = f'. Reason: **{reason}**'
    await member.send(f'You were banned from **{interaction.guild}** by **{interaction.user}**{reason}')
    await member.ban(reason=reason)
    await interaction.response.send_message(f'**{member}** was banned', ephemeral=True)


@bot.tree.command(name='unban', description='Unban user')
async def unban(interaction: discord.Interaction, user: discord.User, reason: str = ''):
    """
    unban user
    :param interaction:
    :param user: user to unban
    :param reason: reason for unban
    :return:
    """
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("You don't have permissions to do this", ephemeral=True)
        return
    try:
        if len(reason) > 0:
            reason = f'. Reason: **{reason}**'
        await interaction.guild.unban(user)
        await user.send(f'You were unbanned at **{interaction.guild}** by **{interaction.user}**{reason}')
        await interaction.response.send_message(f'**{user}** was unbanned', ephemeral=True)
    except discord.errors.NotFound:
        await interaction.response.send_message(f'**{user}** is not banned', ephemeral=True)


@bot.tree.command(name='mute', description='Mute (timeout) member')
async def mute(interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = ''):
    """
    mute (timeout) member
    :param interaction: interaction
    :param member: member to mute (timeout)
    :param duration: amount of time member should be muted (timed out) for (example: 1h30m, 1d)
    :param reason: reason for mute (timeout)
    :return:
    """
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("You don't have permissions to do this", ephemeral=True)
        return
    elif interaction.user.top_role <= member.top_role:
        await interaction.response.send_message(f"Your top role is same/lower than **{member}**'s", ephemeral=True)
        return
    if len(reason) > 0:
        reason = f'. Reason: **{reason}**'
    until = regex.match(duration)
    until = until.groupdict(0)
    until = {k: int(v) for k, v in until.items()}
    until = min(datetime.timedelta(**until), datetime.timedelta(days=28))
    await member.timeout(until, reason=reason)
    await member.send(f'You were muted at **{interaction.guild}** for **{until}** by **{interaction.user}**{reason}')
    await interaction.response.send_message(f'**{member}** was muted', ephemeral=True)


@bot.tree.command(name='unmute', description='Unmute member')
async def unmute(interaction: discord.Interaction, member: discord.Member, reason: str = ''):
    """
    unmute member
    :param interaction: interaction
    :param member: member to unmute
    :param reason: reason for unmute
    :return:
    """
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("You don't have permissions to do this", ephemeral=True)
        return
    elif interaction.user.top_role <= member.top_role:
        await interaction.response.send_message(f"Your top role is same/lower than **{member}**'s", ephemeral=True)
        return
    if len(reason) > 0:
        reason = f'. Reason: **{reason}**'
    await member.timeout(None)
    await member.send(f'You were unmuted at **{interaction.guild}** by **{interaction.user}**{reason}')
    await interaction.response.send_message(f'**{member}** was unmuted', ephemeral=True)


@bot.tree.command(name='purge', description='Purge messages')
async def purge(interaction: discord.Interaction, limit: int, reason: str = ''):
    """
    purge messages
    :param interaction:
    :param limit: limit of messages to purge
    :param reason: reason for purge
    :return:
    """
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("You don't have permissions to do this", ephemeral=True)
        return
    if len(reason) > 0:
        reason = f'. Reason: **{reason}**'
    deleted = await interaction.channel.purge(limit=limit)
    await interaction.response.send_message(f'Deleted {len(deleted)} message(s){reason}', ephemeral=True)


# ----------------------------------------------------------------------------------------------------
# Logs
@bot.tree.command(name='logs', description='Set channel for logs')
async def logs(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You don't have permissions to do this", ephemeral=True)
        return
    log_channels[interaction.guild.id] = interaction.channel.id
    await interaction.response.send_message(f'**{interaction.channel.name}** is now channel for logs', ephemeral=True)


def check_single(before, after, name: str = None) -> str:
    if name is None:
        name = after.__name__
    log = ''
    if before != after:
        log += f'{name}: {getattr(before, "mention", before)} -> {getattr(after, "mention", after)}\n'
    return log


def check_several(before, after, name: str = None) -> str:
    if name is None:
        name = f'{after.__name__}s'
    log = ''
    if before != after:
        removed = [getattr(item, "mention", str(item)) for item in before if item not in after]
        added = [getattr(item, "mention", str(item)) for item in after if item not in before]
        if len(removed) > 0:
            log += f'{name} removed: {f", ".join(removed)}\n'
        if len(added) > 0:
            log += f'{name} added: {f", ".join(added)}\n'
    return log


# App Commands

@bot.event
async def on_raw_app_command_permissions_update(payload: discord.RawAppCommandPermissionsUpdateEvent):
    log_channel = log_channels.get(payload.guild.id, None)
    if log_channel is None:
        return
    log_channel = payload.guild.get_channel(log_channel)

    await log_channel.send('Application command permissions are updated')


@bot.event
async def on_app_command_completion(interaction: discord.Interaction,
                                    command: discord.app_commands.Command | discord.app_commands.ContextMenu):
    log_channel = log_channels.get(interaction.guild.id, None)
    if log_channel is None:
        return
    log_channel = interaction.guild.get_channel(log_channel)

    await log_channel.send(f'**{command}** command has successfully completed without error')


# AutoMod


@bot.event
async def on_automod_rule_create(rule: discord.AutoModRule):
    log_channel = log_channels.get(rule.guild.id, None)
    if log_channel is None:
        return
    log_channel = rule.guild.get_channel(log_channel)

    await log_channel.send(f'**{rule}** rule is created')


@bot.event
async def on_automod_rule_delete(rule: discord.AutoModRule):
    log_channel = log_channels.get(rule.guild.id, None)
    if log_channel is None:
        return
    log_channel = rule.guild.get_channel(log_channel)

    await log_channel.send(f'**{rule}** rule is deleted')


@bot.event
async def on_automod_rule_update(rule: discord.AutoModRule):
    log_channel = log_channels.get(rule.guild.id, None)
    if log_channel is None:
        return
    log_channel = rule.guild.get_channel(log_channel)

    await log_channel.send(f'**{rule}** rule is updated')


@bot.event
async def on_automod_rule_action(execution: discord.AutoModAction):
    log_channel = log_channels.get(execution.guild.id, None)
    if log_channel is None:
        return
    log_channel = execution.guild.get_channel(log_channel)

    await log_channel.send(f"**{execution.member}**'s message has triggered the rule. Result: {execution.action.type}\n"
                           f"Message:\n{execution.content}")


# Channels

@bot.event
async def on_guild_channel_create(channel: discord.abc.GuildChannel):
    log_channel = log_channels.get(channel.guild.id, None)
    if log_channel is None:
        return
    log_channel = channel.guild.get_channel(log_channel)

    await log_channel.send(f'**{channel}** channel is created')


@bot.event
async def on_guild_channel_delete(channel: discord.abc.GuildChannel):
    log_channel = log_channels.get(channel.guild.id, None)
    if log_channel is None:
        return
    log_channel = channel.guild.get_channel(log_channel)

    await log_channel.send(f'**{channel}** channel is deleted')


@bot.event
async def on_guild_channel_update(before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
    log_channel = log_channels.get(after.guild.id, None)
    if log_channel is None:
        return
    log_channel = after.guild.get_channel(log_channel)

    content = f'{after.mention} channel is updated\n'
    content += check_single(before.name, after.name, 'Name')
    content += check_single(before.guild, after.guild, 'Guild')
    content += check_single(before.position, after.position, 'Position')
    content += check_several(before.changed_roles, after.changed_roles, 'Roles')
    content += check_single(before.mention, after.mention, 'Mention')
    content += check_single(before.jump_url, after.jump_url, 'URL')
    content += check_single(before.created_at, after.created_at, 'Creation time')
    # before.overwrites, after.overwrites, 'Overwrites'
    content += check_single(before.category, after.category, 'Category')
    content += check_single(before.permissions_synced, after.permissions_synced, 'Permissions synced')
    await log_channel.send(content)


@bot.event
async def on_guild_channel_pins_update(channel: discord.abc.GuildChannel | discord.Thread,
                                       last_pin: datetime.datetime | None):
    log_channel = log_channels.get(channel.guild.id, None)
    if log_channel is None:
        return
    log_channel = channel.guild.get_channel(log_channel)

    ...


@bot.event
async def on_private_channel_update(before: discord.GroupChannel, after: discord.GroupChannel):
    log_channel = log_channels.get(after.guild.id, None)
    if log_channel is None:
        return
    log_channel = after.guild.get_channel(log_channel)

    content = f'{after} group is updated\n'
    content += check_several(before.recipients, after.recipients, 'Recipients')
    content += check_single(before.me, after.me, 'Alt user')
    content += check_single(before.id, after.id, 'ID')
    content += check_single(before.owner, after.owner, 'Owner')
    content += check_single(before.name, after.name, 'Name')
    content += check_single(before.type, after.type, 'Type')
    content += check_single(before.guild, after.guild, 'Guild')
    content += check_single(before.icon, after.icon, 'Icon')
    content += check_single(before.created_at, after.created_at, 'Creation time')
    content += check_single(before.jump_url, after.jump_url, 'URL')
    await log_channel.send(content)


@bot.event
async def on_private_channel_pins_update(channel: discord.abc.PrivateChannel, last_pin: datetime.datetime | None):
    log_channel = log_channels.get(channel.id, None)
    if log_channel is None:
        return

    ...


@bot.event
async def on_typing(channel: discord.abc.Messageable, user: discord.User | discord.Member, when: datetime.datetime):
    if type(channel) == discord.TextChannel:
        channel: discord.TextChannel
        log_channel = log_channels.get(channel.guild.id, None)
        if log_channel is None:
            return
        log_channel = channel.guild.get_channel(log_channel)
        # await log_channel.send(f'{user.mention} started tying in {channel.mention} at {when}')
    else:
        channel: discord.GroupChannel | discord.DMChannel
        log_channel = log_channels.get(channel.id, None)
        if log_channel is None:
            return
        log_channel = channel
        # await log_channel.send(f'{user.mention} started typing in {channel} at {when}')


# @bot.event
# async def on_raw_typing(payload: discord.RawTypingEvent):
#     ...


# Connection

@bot.event
async def on_connect():
    print('Client has successfully connected to Discord')


@bot.event
async def on_disconnect():
    print('Client has disconnected from Discord, or a connection attempt to Discord has failed')


@bot.event
async def on_shard_connect(shard_id: int):
    print(f'Shard {shard_id} has connected to Discord')


@bot.event
async def on_shard_disconnect(shard_id: int):
    print(f'Shard {shard_id} has disconnected from Discord')


# Debug

@bot.event
async def on_error(event: str, *args, **kwargs):
    print(f'{event} raised an exception\nPositional arguments: {args}\nKeyword arguments: {kwargs}')


@bot.event
async def on_socket_event_type(event_type: str):
    # print(f'{event_type} is received from the WebSocket')
    # print(event_type)
    pass


# @bot.event
# async def on_socket_raw_receive(msg: str):
#     print(f'{msg}')


# @bot.event
# async def on_socket_raw_send(payload: bytes | str):
#     print(f'{payload}')


# Gateway

@bot.event
async def on_ready():
    """
    sync the commands tree
    :return:
    """
    # bot.tree.copy_global_to(guild=discord.Object(id=964109254833356860))
    await bot.tree.sync()
    # await bot.tree.sync(guild=discord.Object(id=964109254833356860))
    print('Client is done preparing the data received from Discord')


@bot.event
async def on_resumed():
    print('Client has resumed a session')


@bot.event
async def on_shard_ready(shard_id: int):
    print(f'Shard {shard_id} is ready')


@bot.event
async def on_shard_resumed(shard_id: int):
    print(f'Shard {shard_id} is resumed')


# Guilds

@bot.event
async def on_guild_available(guild: discord.Guild):
    log_channel = log_channels.get(guild.id, None)
    if log_channel is None:
        return
    log_channel = guild.get_channel(log_channel)

    await log_channel.send(f'{guild} server has become available')


@bot.event
async def on_guild_unavailable(guild: discord.Guild):
    log_channel = log_channels.get(guild.id, None)
    if log_channel is None:
        return
    log_channel = guild.get_channel(log_channel)

    await log_channel.send(f'{guild} server has become unavailable')


@bot.event
async def on_guild_join(guild: discord.Guild):
    """
    preparing server when joins
    :param guild: guild which bot joined
    :return:
    """
    await guild.create_voice_channel('Create channel')

    log_channel = log_channels.get(guild.id, None)
    if log_channel is None:
        return
    log_channel = guild.get_channel(log_channel)

    await log_channel.send(f'{guild} server was joined')


@bot.event
async def on_guild_remove(guild: discord.Guild):
    log_channel = log_channels.get(guild.id, None)
    if log_channel is None:
        return
    log_channel = guild.get_channel(log_channel)

    await log_channel.send(f'{guild} server was removed')


@bot.event
async def on_guild_update(before: discord.Guild, after: discord.Guild):
    log_channel = log_channels.get(after.id, None)
    if log_channel is None:
        return
    log_channel = after.get_channel(log_channel)

    content = f'{after} server is updated\n'
    content += check_single(before.name, after.name, 'ID')
    content += check_several(before.emojis, after.emojis, 'Emojis')
    content += check_several(before.stickers, after.stickers, 'Stickers')
    content += check_single(before.afk_timeout, after.afk_timeout, 'AFK timeout (seconds)')
    content += check_single(before.id, after.id, 'ID')
    content += check_single(before.owner, after.owner, 'Owner')
    content += check_single(before.unavailable, after.unavailable, 'Unavailability')
    content += check_single(before.max_presences, after.max_presences, 'Maximum presences')
    content += check_single(before.max_members, after.max_members, 'Maximum members')
    content += check_single(before.max_video_channel_users, after.max_video_channel_users,
                            'Maximum users in a video channel')
    content += check_single(before.description, after.description, 'Description')
    content += check_single(before.verification_level, after.verification_level, 'Verification level')
    content += check_single(before.vanity_url_code, after.vanity_url_code, 'URL code')
    content += check_single(before.explicit_content_filter, after.explicit_content_filter, 'Explicit content filter')
    content += check_single(before.default_notifications, after.default_notifications, 'Notifications')
    content += check_several(before.features, after.features, 'Features')
    content += check_single(before.premium_tier, after.premium_tier, 'Server Nitro level')
    content += check_single(before.premium_subscription_count, after.premium_subscription_count, 'Boosts')
    content += check_single(before.preferred_locale, after.preferred_locale, 'Locale')
    content += check_single(before.nsfw_level, after.nsfw_level, 'NSFW level')
    content += check_single(before.mfa_level, after.mfa_level, 'MFA level')
    content += check_single(before.approximate_member_count, after.approximate_member_count,
                            'Approximate number of members')
    content += check_single(before.approximate_presence_count, after.approximate_presence_count,
                            'Approximate number of presences')
    content += check_single(before.premium_progress_bar_enabled, after.premium_progress_bar_enabled,
                            'Server Boost level progress bar')
    content += check_single(before.widget_enabled, after.widget_enabled, 'Widget enabled')
    content += check_single(before.max_stage_video_users, after.max_stage_video_users,
                            'Maximum users in a stage video channel')
    content += check_several(before.channels, after.channels, 'Channels')
    content += check_several(before.threads, after.threads, 'Threads')
    content += check_single(before.large, after.large, 'Is large')
    content += check_several(before.voice_channels, after.voice_channels, 'Voice channels')
    content += check_several(before.stage_channels, after.stage_channels, 'Stage channels')
    content += check_single(before.me, after.me, 'Alt member')
    content += check_single(before.voice_client, after.voice_client, 'Voice client')
    content += check_several(before.text_channels, after.text_channels, 'Text channels')
    content += check_several(before.categories, after.categories, 'Categories')
    content += check_several(before.forums, before.forums, 'Forums')
    content += check_single(before.afk_channel, after.afk_channel, 'Inactive (AFK) channel')
    content += check_single(before.system_channel, after.system_channel, 'System channel')
    # before.system_channel_flags, after.system_channel_flags
    content += check_single(before.rules_channel, after.rules_channel, 'Rules channel')
    content += check_single(before.public_updates_channel, after.public_updates_channel, 'Community updates channel')
    content += check_single(before.safety_alerts_channel, after.safety_alerts_channel, 'Safety alerts channel')
    content += check_single(before.widget_channel, after.widget_channel, 'Widget channel')
    content += check_single(before.emoji_limit, after.emoji_limit, 'Emoji limit')
    content += check_single(before.sticker_limit, after.sticker_limit, 'Sticker limit')
    content += check_single(before.bitrate_limit, after.bitrate_limit, 'Bitrate limit')
    content += check_single(before.filesize_limit, after.filesize_limit, 'File size limit (bytes)')
    content += check_several(before.members, after.members, 'Members')
    content += check_several(before.premium_subscribers, after.premium_subscribers, 'Boosters')
    content += check_several(before.roles, after.roles, 'Roles')
    content += check_single(before.default_role, after.default_role, 'Default role')
    content += check_single(before.premium_subscriber_role, after.premium_subscriber_role, 'Booster role')
    content += check_single(before.self_role, after.self_role, 'Alt role')
    content += check_several(before.stage_instances, after.stage_instances, 'Stage instances')
    content += check_several(before.scheduled_events, after.scheduled_events, 'Scheduled events')
    content += check_single(before.owner, after.owner, 'Owner')
    content += check_single(before.icon, after.icon, 'Icon')
    content += check_single(before.banner, after.banner, 'Banner')
    content += check_single(before.splash, after.splash, 'Invite splash')
    content += check_single(before.discovery_splash, after.discovery_splash, 'Discovery splash')
    content += check_single(before.member_count, after.member_count, 'Number of members')
    # content += check_single(before.chunked, after.chunked, 'Chunked')
    content += check_single(before.shard_id, after.shard_id, 'Shard ID')
    content += check_single(before.created_at, after.created_at, 'Creation time')

    await log_channel.send(content)


#

@bot.event
async def on_member_join(member: discord.Member):
    """
    auto role
    :param member: recently joined member
    :return:
    """
    role = autoroles.get(member.guild.id, None)
    if role is not None:
        role = role[member.bot]
        role = member.guild.get_role(role)
        await member.add_roles(role)

    log_channel = log_channels.get(member.guild.id, None)
    if log_channel is None:
        return
    log_channel = member.guild.get_channel(log_channel)

    await log_channel.send(f'{member.mention} has joined the server')


@bot.event
async def on_member_remove(member: discord.Member):
    log_channel = log_channels.get(member.guild.id, None)
    if log_channel is None:
        return
    log_channel = member.guild.get_channel(log_channel)

    await log_channel.send(f'{member.mention} has left the server')


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    log_channel = log_channels.get(after.guild.id, None)
    if log_channel is None:
        return
    log_channel = after.guild.get_channel(log_channel)

    content = f'{after.mention} has updated their profile\n'
    content += check_single(before.name, after.name, 'Name')
    content += check_single(before.global_name, after.global_name, 'Global name')
    content += check_single(before.display_name, after.display_name, 'Display name')
    content += check_several(before.roles, after.roles, 'Roles')
    await log_channel.send(content)


@bot.event
async def on_member_ban(guild: discord.Guild, user: discord.User | discord.Member):
    log_channel = log_channels.get(guild.id, None)
    if log_channel is None:
        return
    log_channel = guild.get_channel(log_channel)

    await log_channel.send(f'{user.mention} was banned')


@bot.event
async def on_member_unban(guild: discord.Guild, user: discord.User):
    log_channel = log_channels.get(guild.id, None)
    if log_channel is None:
        return
    log_channel = guild.get_channel(log_channel)

    await log_channel.send(f'{user.mention} was unbanned')


@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    log_channel = log_channels.get(after.guild.id, None)
    if log_channel is None:
        return
    log_channel = after.guild.get_channel(log_channel)

    await log_channel.send(
        f'{after.author.mention} has changed their message in {after.channel.mention}\n'
        f'Before:\n{before.content}\nAfter:\n{after.content}')


@bot.event
async def on_message_delete(message: discord.Message):
    log_channel = log_channels.get(message.guild.id, None)
    if log_channel is None:
        return
    log_channel = message.guild.get_channel(log_channel)

    await log_channel.send(
        f'{message.author.mention} has deleted their message in {message.channel.mention}\n'
        f'Message:\n{message.content}')


@bot.event
async def on_guild_role_create(role: discord.Role):
    log_channel = log_channels.get(role.guild.id, None)
    if log_channel is None:
        return
    log_channel = role.guild.get_channel(log_channel)

    await log_channel.send(f'{role.mention} role was created')


@bot.event
async def on_guild_role_delete(role: discord.Role):
    log_channel = log_channels.get(role.guild.id, None)
    if log_channel is None:
        return
    log_channel = role.guild.get_channel(log_channel)

    await log_channel.send(f'{role.mention} role was deleted')


@bot.event
async def on_guild_role_update(before: discord.Role, after: discord.Role):
    log_channel = log_channels.get(after.guild.id, None)
    if log_channel is None:
        return
    log_channel = after.guild.get_channel(log_channel)

    content = f'{after.mention} role was updated\n'
    if before.name != after.name:
        content += f'Name: **{before.name}** -> **{after.name}**\n'
    if before.color != after.color:
        content += f'Color: **{before.color}** -> **{after.color}**\n'
    before_permissions = [permission for permission in before.permissions]
    after_permissions = [permission for permission in after.permissions]
    removed_permissions = []
    added_permissions = []
    for before_permission, after_permission in zip(before_permissions, after_permissions):
        if before_permission[1] and not after_permission[1]:
            removed_permissions.append(before_permission[0])
        if not before_permission[1] and after_permission[1]:
            added_permissions.append(after_permission[0])
    if len(removed_permissions) > 0:
        content += f'Removed permissions: **{"**, **".join(removed_permissions)}**\n'
    if len(added_permissions) > 0:
        content += f'Added permissions: **{"**, **".join(added_permissions)}**\n'
    await log_channel.send(content)


@bot.event
async def on_thread_create(thread: discord.Thread):
    log_channel = log_channels.get(thread.guild.id, None)
    if log_channel is None:
        return
    log_channel = thread.guild.get_channel(log_channel)

    await log_channel.send(f'{thread.mention} was created in {thread.parent.mention}')


@bot.event
async def on_thread_join(thread: discord.Thread):
    log_channel = log_channels.get(thread.guild.id, None)
    if log_channel is None:
        return
    log_channel = thread.guild.get_channel(log_channel)

    await log_channel.send(f'{thread.mention} was joined in {thread.parent.mention}')


@bot.event
async def on_thread_update(before: discord.Thread, after: discord.Thread):
    log_channel = log_channels.get(after.guild.id, None)
    if log_channel is None:
        return
    log_channel = after.guild.get_channel(log_channel)

    ...


@bot.event
async def on_thread_remove(thread: discord.Thread):
    log_channel = log_channels.get(thread.guild.id, None)
    if log_channel is None:
        return
    log_channel = thread.guild.get_channel(log_channel)

    await log_channel.send(f'{thread.mention} was removed from {thread.parent.mention}')


@bot.event
async def on_thread_delete(thread: discord.Thread):
    log_channel = log_channels.get(thread.guild.id, None)
    if log_channel is None:
        return
    log_channel = thread.guild.get_channel(log_channel)

    await log_channel.send(f'{thread.mention} was deleted from {thread.parent.mention}')


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    """
    creating member's voice channel
    :param member: member, whose voice state is updated
    :param before: voice state before update
    :param after: voice state after update
    :return:
    """
    if after.channel is not None and after.channel.name == 'Create channel':
        channel = await member.guild.create_voice_channel(f'Created by {member.name}', category=after.channel.category)
        await member.move_to(channel)
    if before.channel is not None and before.channel.name == f'Created by {member.name}':
        await before.channel.delete()

    log_channel = log_channels.get(member.guild.id, None)
    if log_channel is None:
        return
    log_channel = member.guild.get_channel(log_channel)

    if before.channel is None and after.channel is not None:
        await log_channel.send(f'{member.mention} has joined {after.channel.mention} channel')
    elif before.channel is not None and after.channel is None:
        await log_channel.send(f'{member.mention} has left {before.channel.mention} channel')


# ----------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    # Alt
    # bot.run('MTA4OTg2MjU5ODkzNTE4NzU4Nw.G3fGIt.llr7zr_3c1s2mqZ9Bskybxcj4ye--_1zEEmur0')
    # Grind
    bot.run('TOKEN')
    bot.run('OTIyNzYzNjgzNjEwOTE0ODQ3.GaRcAN.YPh9Ju1qkGnnYodI5AQcnRPIFu_AgqvcUH8MGI')
