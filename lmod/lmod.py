from discord.ext import commands
from cogs.utils.dataIO import fileIO
from cogs.utils import checks
from __main__ import send_cmd_help
import os
import asyncio


class lmod:
    
    
    @commands.command(pass_context=True, no_pm=True)
    async def uinfo(self, ctx, *, user: discord.Member=None):
        """Shows users's informations"""
        author = ctx.message.author
        server = ctx.message.server

        if not user:
            user = author

        roles = [x.name for x in user.roles if x.name != "@everyone"]

        joined_at = self.fetch_joined_at(user, server)
        since_created = (ctx.message.timestamp - user.created_at).days
        since_joined = (ctx.message.timestamp - joined_at).days
        user_joined = joined_at.strftime("%d %b %Y %H:%M")
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        voicechan = user.voice.voice_channel
        member_number = sorted(server.members,
                               key=lambda m: m.joined_at).index(user) + 1

        created_on = "{}\n({} days ago)".format(user_created, since_created)
        joined_on = "{}\n({} days ago)".format(user_joined, since_joined)
        

        game = "Chilling in {} status".format(user.status)
                
        names = self.past_names[user.id] if user.id in self.past_names else None
        try:
            nicks = self.past_nicknames[server.id][user.id]
            nicks = [escape_mass_mentions(nick) for nick in nicks]
        except:
            nicks = None
        nameslist = ""
        if names:
            names = [escape_mass_mentions(name) for name in names]
            nameslist += "**Past 20 names**:\n"
            nameslist += ", ".join(names)
        if nicks:
            if nameslist:
                nameslist += "\n\n"
            nameslist += "**Past 20 nicknames**:\n"
            nameslist += ", ".join(nicks)
        if nameslist:
            prevnames = nameslist
        else:
            prevnames = "That user doesn't have any recorded name or nickname change."

        if voicechan is None:
            curvoice = "None"
        else:
            curvoice = voicechan

        if user.game is None:
            pass
        elif user.game.url is None:
            game = "Playing {}".format(user.game)
        else:
            game = "Streaming: [{}]({})".format(user.game, user.game.url)

        if roles:
            roles = sorted(roles, key=[x.name for x in server.role_hierarchy
                                       if x.name != "@everyone"].index)
            roles = ", ".join(roles)
        else:
            roles = "None"

        data = discord.Embed(description=game, colour=user.colour)
        data.add_field(name="Joined Discord on", value=created_on)
        data.add_field(name="Joined this server on", value=joined_on)
        data.add_field(name="Roles", value=roles, inline=False)
        data.add_field(name="Past names", value=prevnames, inline=False)
        data.add_field(name="Current voice channel", value=str(voicechan), inline=False)
        data.set_footer(text="Member #{} | User ID:{}"
                             "".format(member_number, user.id))

        name = str(user)
        name = " ~ ".join((name, user.nick)) if user.nick else name

        if user.avatar_url:
            data.set_author(name=name, url=user.avatar_url)
            data.set_thumbnail(url=user.avatar_url)
        else:
            data.set_author(name=name)

        try:
            await self.bot.say(embed=data)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission "
                               "to send this")
 
    
#    @commands.command(no_pm=True, pass_context=True)
#    @checks.admin_or_permissions(ban_members=True)
#    async def wipe(self, ctx, user_id: int, channel : discord.Channel=None):
#        """Wipes X last messages of a user in certain channel
#
#        A user ID needs to be provided as well as channels name"""
#        user_id = str(user_id)
#        channel = ctx.message.channel
#        author = ctx.message.author
#        server = author.server
#        is_bot = self.bot.user.bot
#        has_permissions = channel.permissions_for(server.me).manage_messages
#        self_delete = user == self.bot.user
#
#        def check(m):
#            if m.author == user:
#                return True
#            elif m == ctx.message:
#                return True
#            else:
#                return False
#
#        to_delete = [ctx.message]
#
#        if not has_permissions and not self_delete:
#            await self.bot.say("I'm not allowed to delete messages.")
#            return
#
#        tries_left = 5
#        tmp = ctx.message
#
#        while tries_left and len(to_delete) - 1 < number:
#            async for message in self.bot.logs_from(channel, limit=100,
#                                                    before=tmp):
#                if len(to_delete) - 1 < number and check(message):
#                    to_delete.append(message)
#                tmp = message
#            tries_left -= 1
#
#        logger.info("{}({}) deleted {} messages "
#                    " made by {}({}) in channel {}"
#                    "".format(author.name, author.id, len(to_delete),
#                              user.name, user.id, channel.name))
#
#        if is_bot and not self_delete:
#            # For whatever reason the purge endpoint requires manage_messages
#            await self.mass_purge(to_delete)
#        else:
#            await self.slow_deletion(to_delete)
    



def setup(bot):
    check_folder()
    check_file()
    n = FTickets(bot)
    bot.add_cog(n)