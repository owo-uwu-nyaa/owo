import discord
from discord.ext import commands
from datetime import datetime, timezone, timedelta
from pprint import pprint 

class RepostDeletedMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # Use this event to listen for message deletions
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        async for entry in message.guild.audit_logs(limit=10, action=discord.AuditLogAction.message_delete):
            if entry.user.id == message.user.id:
                continue
            cr = entry.created_at + timedelta(seconds=30)
            now = datetime.now(timezone.utc)
#            pprint(entry)
            if cr > now:
                embed = discord.Embed(title="Eine Nachricht wurde fachgerecht entsorgt")
                embed.add_field(name="Member: ", value = message.author.mention, inline=True)
                embed.add_field(name = "Pwobably the nasty deletor: ", value = entry.user.mention, inline=True)
                embed.add_field(name = "Message: ", value = message.content, inline=False)
                embed.add_field(name = "Channel: ", value = message.channel.mention, inline=False)
                await self.bot.get_channel(1056906247372275732).send(embed=embed)
                break

def setup(bot):
    return bot.add_cog(RepostDeletedMessages(bot))
