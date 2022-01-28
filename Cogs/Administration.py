import discord
from discord.ext import commands
from discord.commands import Option
import datetime
from babel.dates import format_date

from main import WarningEmbed, sql_input, sql_fetch


class Administration(commands.Cog, description="Server management and administration"):
    
    def __init__(self, bot):
        self.bot = bot
        self.caption = ":tools: Administration :tools:"
        self.color = (136,153,166)
    
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Administration has loaded successfully.")
        
        
    @commands.slash_command(description="Deletes messages above.")
    @commands.has_permissions(manage_messages=True)
    async def clear(
        self,
        ctx: commands.Context,
        amount: Option(int, "Amount of messages to delete", required=False,
                       default=1, min_value=1)
    ):
        await ctx.channel.purge(limit=1+amount)
        em = discord.Embed(
            title=":put_litter_in_its_place: Deleted sucessfully :put_litter_in_its_place:",
            color=discord.Color.from_rgb(59,136,195)
        )
        await ctx.respond(embed=em, delete_after=5)
        
        
    @commands.slash_command(description="Warns the member.")
    @commands.has_permissions(ban_members=True)
    async def warn(
        self,
        ctx : commands.Context,
        member: Option(discord.Member, "The member to warn"),
        reason: Option(str, "Reason why you're warning member",
                       required=False, default="No reason given.")
    ):
        member_id = member.id
        member_nick = member.display_name
        guild_id = ctx.guild.id
        warnedby_id = ctx.author.id
        date = datetime.datetime.now()
        date = format_date(date, locale="en")
        
        warning_id = sql_input("INSERT INTO warnings VALUES (?,?,?,?,?)",
                               (member_id, reason, guild_id, warnedby_id, date))
        
        warnings = sql_fetch(
            "SELECT rowid FROM warnings WHERE guild_id=(?) AND member_id=(?)",
            (guild_id, member_id))
        
        num_warnings = len(warnings)
        
        em = discord.Embed(
            title=f":exclamation: {member_nick} has been warned. "
                + f"{member_nick} has {num_warnings} warnings now.",
            description=f"Reason: {reason} (ID: #{warning_id})",
            color=discord.Color.from_rgb(190,25,49)
        )
        await ctx.respond(embed=em, delete_after=60)
        
        
    @commands.slash_command(description="Shows the warnings of a member.")
    async def warncheck(
        self,
        ctx: commands.Context,
        member: Option(discord.Member,"Member to check warnings", required=False, default=None)
    ):
        if member is None:
            member = ctx.author
        
        permissions = ctx.channel.permissions_for(ctx.author)
        perm_check = member == ctx.author or permissions.ban_members
        guild_id = ctx.guild.id
        member_id = member.id
        member_nick = member.display_name
        
        warnings = sql_fetch(
            "SELECT rowid, * FROM warnings WHERE guild_id=(?) AND member_id=(?)",
            (guild_id, member_id))
        
        em = discord.Embed(
            title=f"{member_nick} has {len(warnings)} warnings.",
            color=discord.Color.from_rgb(190,25,49)
        )
        if perm_check:
            for warning in warnings:
                warnedby = await self.bot.get_or_fetch_user(warning[4])
                em.add_field(
                    name=warning[2]+f" (ID: #{warning[0]})", 
                    value=f"warned by {warnedby.mention} on {warning[5]}")
        
        await ctx.respond(embed=em, ephemeral=True)
        
        
    @commands.slash_command(description="Deletes a warning.")
    @commands.has_permissions(ban_members=True)
    async def deletewarn(
        self,
        ctx: commands.Context,
        warning_id: Option(int, "ID of warning to delete", min_value=1)
    ):  
        guild_id = sql_fetch("SELECT guild_id FROM warnings WHERE rowid=(?)",(warning_id,))
        
        if len(guild_id) == 0:
            em = WarningEmbed("Wrong ID. Warning doesn't exist.")
        elif guild_id[0][0] != ctx.guild.id:
            em = WarningEmbed("Wrong ID. Warning not found.")
        else:
            sql_input("DELETE FROM warnings WHERE rowid=(?)", (warning_id,))
            em = discord.Embed(
                title=f"Deleted warning with ID #{warning_id} .",
                color=discord.Color.from_rgb(190,25,49)
            )
        
        await ctx.respond(embed=em) 
    
        
def setup(bot):
    bot.add_cog(Administration(bot))