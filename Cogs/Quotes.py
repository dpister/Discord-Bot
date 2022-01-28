import discord
from discord.ext import commands, pages
from discord.commands import Option
import datetime
from babel.dates import format_date
import random

from main import WarningEmbed, sql_input, sql_fetch


class Quotes(commands.Cog, description="Save the best moments in your server as a quote."):
    
    def __init__(self, bot):
        self.bot = bot
        self.caption = ":speech_balloon: Quotes :speech_balloon:"
        self.color = (189,221,244)
    
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Quotes has loaded successfully.")
      
        
    @commands.message_command()
    async def addquote(self, ctx: commands.Context, message: discord.Message):
        text = message.content.replace("\n"," ")
        author_name = message.author.name
        author_id = message.author.id
        addedby_id = ctx.author.id
        addedby_name = ctx.author.name
        guild_id = message.guild.id
        date = datetime.datetime.now()
        date = format_date(date, locale="en")
        
        quote_id = sql_input(
            "INSERT INTO quotes VALUES (?,?,?,?,?,?,?)",
            (text, author_name, author_id, addedby_name, addedby_id, guild_id, date)
        )
        em = discord.Embed(
            title=":white_check_mark: Success :white_check_mark:",
            description=f"Quote added. Quote ID: #{quote_id}.",
            color=discord.Color.from_rgb(119,178,85)
        )
        em.add_field(name="Quote",value=text+" - "+author_name)    
        await ctx.respond(embed=em)
        
        
    @commands.slash_command(description="Returns a quote from this server's quote list.")
    async def quote(
        self,
        ctx: commands.Context,
        person_or_id: Option(
            str, 
            "Look for a quote with a specific quote ID or written by a specific person.",
            required=False, 
            default=None
        ),
    ):
        guild_id = ctx.guild.id
        if person_or_id is not None:
            if person_or_id.isdigit():
                quote_id = int(person_or_id)
                if quote_id < 1:
                    em = WarningEmbed("Quote ID cannot be negative.")
                    await ctx.respond(embed=em)
                    return
                data = sql_fetch(
                    "SELECT * FROM quotes WHERE rowid=(?) AND guild_id=(?)", 
                    (quote_id, guild_id)
                )
                if len(data) == 0:
                    em = WarningEmbed("Quote ID not found.")
            else:
                person = person_or_id
                data = sql_fetch(
                    "SELECT * FROM quotes WHERE author_name=(?) AND guild_id=(?)",
                    (person, guild_id)
                )
                if len(data) == 0:
                    em = WarningEmbed(f"No quotes by {person} found.")
        else:
            data = sql_fetch("SELECT * FROM quotes WHERE guild_id=(?)", (guild_id,))
            if len(data) == 0:
                em = WarningEmbed("This server has no quotes added yet.")
        
        if len(data) != 0:
            quote = random.choice(data)
            em = discord.Embed(
                title=f"{quote[0]} - {quote[1]}",
                description=f"added by {quote[3]} on {quote[6]}",
                color=discord.Color.teal()
            )
        await ctx.respond(embed=em)
        
        
    @commands.slash_command(description="Deletes a quote.")
    async def deletequote(
        self, 
        ctx: commands.Context, 
        quote_id: Option(int, "Quote ID of the quote to delete", min_value=1)
    ):
        data = sql_fetch("SELECT quote, author_id FROM quotes WHERE rowid=(?)", (quote_id,))
        if len(data) > 0:
            quote, author_id = data[0]
            permissions = ctx.channel.permissions_for(ctx.author)
            if author_id != ctx.author.id and (permissions.manage_messages is False):
                em = WarningEmbed("You can only delete your own quotes.")
            else:
                sql_input("DELETE FROM quotes WHERE rowid=(?)", (quote_id,))
                em = discord.Embed(
                    title=":white_check_mark: Success :white_check_mark:",
                    description="Quote deleted.",
                    color=discord.Color.from_rgb(119,178,85)
                )
                em.add_field(name=f"Deleted quote #{quote_id}:", value=quote)
        else:
            em=WarningEmbed("Quote ID does not exist.")
        await ctx.respond(embed=em)
    
    
    @commands.slash_command(description="Gives a list of all quotes from this server.")
    @commands.has_permissions(manage_messages=True)
    async def quotelist(self, ctx: commands.Context):
        guild_id = ctx.guild.id
        data = sql_fetch("SELECT rowid, * FROM quotes WHERE guild_id=(?)", (guild_id,))
        pagelist=[]
        quotes_per_page=5
        for i, quote in enumerate(data):
            if i % quotes_per_page == 0:
                pagelist.append([])
            author = await self.bot.get_or_fetch_user(quote[3])
            addedby = await self.bot.get_or_fetch_user(quote[5])
            author_mention = author.mention if author is not None else "[not found]"
            addedby_mention = addedby.mention if addedby is not None else "[not found]"
            em = discord.Embed(
                title=f"*{quote[1]}*",
                description=f" by {author_mention} added by {addedby_mention} "
                + "on {quote[7]} (ID: #{quote[0]})"
            )
            pagelist[i//5].append(em)
        if pagelist == []:
            em = WarningEmbed("Quote list is empty")
            pagelist.append(em)
        paginator = pages.Paginator(pages=pagelist)
        await paginator.respond(ctx.interaction)
        
        
def setup(bot):
    bot.add_cog(Quotes(bot))