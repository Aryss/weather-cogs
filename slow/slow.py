"""
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

import discord
from discord.ext import commands
from .utils import checks
from __main__ import send_cmd_help, settings
from cogs.utils.dataIO import dataIO
import os
import re
import asyncio


class slow:
    """Allows to enable slow mode in a specific channel"""

    __author__ = "_Lynx"
    __version__ = "v1.0"

    def __init__(self, bot):
        self.bot = bot
        self.location = 'data/slow/settings.json'
        self.json = dataIO.load_json(self.location)

    
    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def slowmode(self, message, args):
        num = int(args[0])
        if num == 0:
            await self.bot.send_message(
                message.channel,
                "The slow mode interval cannot be 0!"
            )
            return
        storage = await self.get_storage(message.server)
        await storage.sadd(
            'slowmode:channels',
            message.channel.id
        )
        await storage.set(
            'slowmode:{}:interval'.format(
                message.channel.id
            ),
            num
        )
        await self.bot.send_message(
            message.channel,
            "{} is now in slow mode. ({} seconds)".format(
                message.channel.mention,
                num
            )
        )

    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def slowoff(self, message, args):
        storage = await self.get_storage(message.server)
        # Get the slowed_channels
        slowed_channels = await storage.smembers('slowmode:channels')
        if message.channel.id not in slowed_channels:
            return
        # Delete the channel from the slowed channel
        await storage.srem('slowmode:channels', message.channel.id)
        # Get the slowed_members
        slowed_members = await storage.smembers(
            'slowmode:{}:slowed'.format(message.channel.id)
        )
        # Delete the slowed_members TTL
        for user_id in slowed_members:
            await storage.delete('slowmode:{}:slowed:{}'.format(
                message.channel.id,
                user_id
            ))
        # Delete the slowed_members list
        await storage.delete('slowmode:{}:slowed'.format(
            message.channel.id
        ))
        # Confirm message
        await self.mee6.send_message(
            message.channel,
            "{} is no longer in 🐌 mode 😉.".format(
                message.channel.mention
            )
        )

    async def slow_check(self, message):
        storage = await self.get_storage(message.server)
        # Check if the user is a mod/admin/etc
        roles = [r.name for r in user.roles]
        bot_admin = settings.get_server_admin(message.server)
        bot_mod = settings.get_server_mod(message.server)
        if message.channel.id in self.json[message.server.id]['excluded_channels']:
            return
        elif user.id == settings.owner:
            return
        elif bot_admin in roles:
            return
        elif bot_mod in roles:
            return
        elif user.permissions_in(message.channel).manage_messages is True:
            return
        # Check if the channel is in slowmode
        slowed_channels = await storage.smembers('slowmode:channels')
        if message.channel.id not in slowed_channels:
            return
        # Grab the slowmode interval
        interval = await storage.get(
            'slowmode:{}:interval'.format(message.channel.id)
        )
        if not interval:
            return

        # If the user not in the slowed list
        # Add the user to the slowed list
        await storage.sadd(
            'slowmode:{}:slowed'.format(
                message.channel.id
            ),
            message.author.id
        )
        # Check if user slowed
        slowed = await storage.get('slowmode:{}:slowed:{}'.format(
            message.channel.id,
            message.author.id)
        ) is not None

        if slowed:
            await self.bot.delete_message(message)
        else:
            # Register a TTL key for the user
            await storage.set(
                'slowmode:{}:slowed:{}'.format(
                    message.channel.id,
                    message.author.id
                ),
                interval
            )
            await storage.expire(
                'slowmode:{}:slowed:{}'.format(
                    message.channel.id,
                    message.author.id
                ),
                int(interval)
            )


def check_folder():
    if not os.path.exists('data/slow'):
        os.makedirs('data/slow')


def check_file():
    f = 'data/slow/settings.json'
    if dataIO.is_valid_json(f) is False:
        dataIO.save_json(f, {})


def setup(bot):
    check_folder()
    check_file()
    n = slow(bot)
    bot.add_cog(n)
    bot.add_listener(n.slow_check, 'on_message')
