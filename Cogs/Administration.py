import discord
from discord.ext import commands
from discord.commands import Option
import datetime
from babel.dates import format_date

from main import WarningEmbed, to_extras


class Administration(commands.Cog, description="Server management and administration"):
    
    def __init__(self, bot):
        self.bot = bot
        self.caption = ":tools: Administration :tools:"
        self.color = (136,153,166)
    
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Administration has loaded successfully.")
        
    
    @to_extras(
        help="Deletes messages above. Specify number of messages via [amount].",
        caption=":wastebasket: Clear :wastebasket:",
        usage="`/delet [amount]`",
        color=(154,170,180)
    )
    @commands.slash_command(description="Deletes messages above.")
    @commands.has_permissions(manage_messages=True)
    async def clear(
        self,
        ctx: discord.ApplicationContext,
        amount: Option(int, "Amount of messages to delete", required=False,
                       default=1, min_value=1)
    ):
        await ctx.channel.purge(limit=1+amount)
        em = discord.Embed(
            title=":put_litter_in_its_place: Deleted sucessfully :put_litter_in_its_place:",
            color=discord.Color.from_rgb(59,136,195)
        )
        await ctx.respond(embed=em, delete_after=5)
        
    
    @to_extras(
        help="Warns a member",
        caption=":warning::bust_in_silhouette: Warn :bust_in_silhouette::warning:",
        usage="`/warn <member> [reason]`",
        color=(34,102,153)
    )
    @commands.slash_command(description="Warns the member.")
    @commands.has_permissions(ban_members=True)
    async def warn(
        self,
        ctx : discord.ApplicationContext,
        member: Option(discord.Member, "The member to warn"),
        reason: Option(str, "Reason why you're warning member",
                       required=False, default="No reason given.")
    ):
        cursor = self.bot.conn.cursor()
        member_id = member.id
        member_nick = member.display_name
        guild_id = ctx.guild.id
        warnedby_id = ctx.author.id
        date = datetime.datetime.now()
        date = format_date(date, locale="en")
        
        cursor.execute("INSERT INTO warnings VALUES (?,?,?,?,?)",
                               (member_id, reason, guild_id, warnedby_id, date))
        self.bot.conn.commit()
        warning_id = cursor.lastrowid
        cursor.execute(
            "SELECT rowid FROM warnings WHERE guild_id=(?) AND member_id=(?)",
            (guild_id, member_id))
        warnings = cursor.fetchall()

        num_warnings = len(warnings)
        x = bool(num_warnings-1)
        em = discord.Embed(
            title=f":exclamation: {member_nick} has been warned. "
                + f"{member_nick} has {num_warnings} warning{x*'s'} now.",
            description=f"Reason: {reason} (ID: #{warning_id})",
            color=discord.Color.from_rgb(190,25,49)
        )
        await ctx.respond(embed=em, delete_after=60)
        
    
    @to_extras(
        help="Shows the number of warnings of a member. Shows a full list to "
            + "mods and members checking their own warnings. Defaults to own warnings",
        caption=":warning::clipboard: Warncheck :warning::clipboard:",
        usage="`/checkwarn [member]`",
        color=(255,255,255)
    )
    @commands.slash_command(description="Shows the warnings of a member.")
    async def checkwarn(
        self,
        ctx: discord.ApplicationContext,
        member: Option(discord.Member,"Member to check warnings", required=False, default=None)
    ):
        cursor = self.bot.conn.cursor()
        if member is None:
            member = ctx.author
        
        permissions = ctx.channel.permissions_for(ctx.author)
        perm_check = member == ctx.author or permissions.ban_members
        guild_id = ctx.guild.id
        member_id = member.id
        member_nick = member.display_name
        
        cursor.execute(
            "SELECT rowid, * FROM warnings WHERE guild_id=(?) AND member_id=(?)",
            (guild_id, member_id))
        warnings = cursor.fetchall()
        
        x = bool(len(warnings)-1)
        em = discord.Embed(
            title=f":exclamation: {member_nick} has {len(warnings)} " 
                + f"warning{x*'s'}.",
            color=discord.Color.from_rgb(190,25,49)
        )
        if perm_check:
            for warning in warnings:
                warnedby = await self.bot.get_or_fetch_user(warning[4])
                em.add_field(
                    name=warning[2]+f" (ID: #{warning[0]})", 
                    value=f"warned by {warnedby.mention} on {warning[5]}")
        
        await ctx.respond(embed=em, ephemeral=True)
        
    
    @to_extras(
        help="Deletes the warning associated with `[warning_id]`",
        caption=":warning::wastebasket: Deletewarn :warning::wastebasket:",
        usage="`/deletewarn <warning_id>`",
        color=(154,170,180)
    )
    @commands.slash_command(description="Deletes a warning.")
    @commands.has_permissions(ban_members=True)
    async def deletewarn(
        self,
        ctx: discord.ApplicationContext,
        warning_id: Option(int, "ID of warning to delete", min_value=1)
    ):  
        cursor = self.bot.conn.cursor()
        cursor.execute("SELECT guild_id FROM warnings WHERE rowid=(?)",(warning_id,))
        guild_id = cursor.fetchone()
        
        
        if len(guild_id) == 0:
            em = WarningEmbed("Wrong ID. Warning doesn't exist.")
        elif guild_id[0] != ctx.guild.id:
            em = WarningEmbed("Wrong ID. Warning not found.")
        else:
            cursor.execute("DELETE FROM warnings WHERE rowid=(?)", (warning_id,))
            self.bot.conn.commit()
            em = discord.Embed(
                title=f"Deleted warning with ID #{warning_id} .",
                color=discord.Color.from_rgb(190,25,49)
            )
        
        await ctx.respond(embed=em) 
    
        
def setup(bot):
    bot.add_cog(Administration(bot))