import discord
from discord.ext import commands, pages
from discord.commands import Option
import datetime
from babel.dates import format_date
import random

from main import WarningEmbed, to_extras


class Quotes(commands.Cog, description="Save the best moments in your server as a quote"):
    
    def __init__(self, bot):
        self.bot = bot
        self.caption = ":speech_balloon: Quotes :speech_balloon:"
        self.color = (189,221,244)
    
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Quotes has loaded successfully.")
      
        
    @to_extras(
        description="Adds the message to a list of quotes.",
        help="Adds the message to a list of quotes.\n "
            + "Quote ID: A number used to uniquely identify every quote.",
        usage="as message command",
        caption=":speech_balloon::white_check_mark: Addquote "
            + ":white_check_mark::speech_balloon:",
        color=(119,178,85)
    )
    @commands.message_command()
    async def addquote(self, ctx: discord.ApplicationContext, message: discord.Message):
        text = message.content.replace("\n"," ")
        author_name = message.author.name
        author_id = message.author.id
        addedby_id = ctx.author.id
        addedby_name = ctx.author.name
        guild_id = message.guild.id
        date = datetime.datetime.now()
        date = format_date(date, locale="en")
        
        cursor = self.bot.conn.cursor()
        cursor.execute(
            "INSERT INTO quotes VALUES (?,?,?,?,?,?,?)",
            (text, author_name, author_id, addedby_name, addedby_id, guild_id, date)
        )
        self.bot.conn.commit()
        quote_id = cursor.lastrowid
        
        em = discord.Embed(
            title=":white_check_mark: Success :white_check_mark:",
            description=f"Quote added. Quote ID: #{quote_id}.",
            color=discord.Color.from_rgb(119,178,85)
        )
        em.add_field(name="Quote",value=text+" - "+author_name)    
        await ctx.respond(embed=em)
        
        

    @to_extras(
        help="Returns a quote from this server's quote list. "
            + "Use `[person_or_id]` to specify a person or a quote ID."
            + "\nQuote ID: A number used to uniquely identify every quote.",
        caption=":speech_balloon: Quote :speech_balloon:",
        color=(189,221,244),
        usage="`/quote [person_or_id]`"
    )
    @commands.slash_command(description="Returns a quote from this server's quote list.")
    async def quote(
        self,
        ctx: discord.ApplicationContext,
        person_or_id: Option(
            str, 
            "Look for a quote with a specific quote ID or written by a specific person.",
            required=False, 
            default=None
        ),
    ):
        guild_id = ctx.guild.id
        cursor = self.bot.conn.cursor()
        if person_or_id is not None:
            if person_or_id.isdigit():
                quote_id = int(person_or_id)
                if quote_id < 1:
                    em = WarningEmbed("Quote ID cannot be negative.")
                    await ctx.respond(embed=em)
                    return
                cursor.execute(
                    "SELECT * FROM quotes WHERE rowid=(?) AND guild_id=(?)", 
                    (quote_id, guild_id)
                )
                data = cursor.fetchall()
                if len(data) == 0:
                    em = WarningEmbed("Quote ID not found.")
            else:
                person = person_or_id
                cursor.execute(
                    "SELECT * FROM quotes WHERE author_name=(?) AND guild_id=(?)",
                    (person, guild_id)
                )
                data = cursor.fetchall()
                if len(data) == 0:
                    em = WarningEmbed(f"No quotes by {person} found.")
        else:
            cursor.execute("SELECT * FROM quotes WHERE guild_id=(?)", (guild_id,))
            data = cursor.fetchall()
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
        
    @to_extras(
        help="Deletes the quote associated with `[quote_id]`. "
            + "Regular users can only delete their own quotes."
            + "\nQuote ID: A number used to uniquely identify every quote.",
        caption=":speech_balloon::wastebasket: Deletequote "
            + ":wastebasket::speech_balloon:",
        usage="`/quote <quote_id>`",
        color=(154,170,180)
    )  
    @commands.slash_command(
        description="Deletes the quote associated with `[quote_id]`.")
    async def deletequote(
        self, 
        ctx: discord.ApplicationContext, 
        quote_id: Option(int, "Quote ID of the quote to delete", min_value=1)
    ):
        cursor = self.bot.conn.cursor()
        cursor.execute("SELECT quote, author_id FROM quotes WHERE rowid=(?)", (quote_id,))
        data = cursor.fetchall()
        if len(data) > 0:
            quote, author_id = data[0]
            permissions = ctx.channel.permissions_for(ctx.author)
            if author_id != ctx.author.id and (permissions.manage_messages is False):
                em = WarningEmbed("You can only delete your own quotes.")
            else:
                cursor.execute("DELETE FROM quotes WHERE rowid=(?)", (quote_id,))
                self.bot.conn.commit()
                em = discord.Embed(
                    title=":white_check_mark: Success :white_check_mark:",
                    description="Quote deleted.",
                    color=discord.Color.from_rgb(119,178,85)
                )
                em.add_field(name=f"Deleted quote #{quote_id}:", value=quote)
        else:
            em=WarningEmbed("Quote ID does not exist.")
        await ctx.respond(embed=em)
    
    
    @to_extras(
        help="Gives a list of all quotes from this server. "
            + "Only useable by mods with permission to manage messages.",
        caption=":speech_balloon::clipboard: Quotelist :clipboard::speech_balloon:",
        color=(255,255,255),
        usage="`/quotelist`"
    )
    @commands.slash_command(description="Gives a list of all quotes from this server.")
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3600, commands.BucketType.guild)
    async def quotelist(self, ctx: discord.ApplicationContext):
        guild_id = ctx.guild.id
        cursor = self.bot.conn.cursor()
        cursor.execute("SELECT rowid, * FROM quotes WHERE guild_id=(?)", (guild_id,))
        data = cursor.fetchall()
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
                description=f"by {author_mention}"
            )
            em.add_field(name="added by",
                         value=f"{addedby_mention} on {quote[7]} (ID: #{quote[0]})")
            pagelist[i//10].append(em)
        if pagelist == []:
            em = WarningEmbed("Quote list is empty")
            pagelist.append(em)
        paginator = pages.Paginator(pages=pagelist)
        await paginator.respond(ctx.interaction)
        
        
def setup(bot):
    bot.add_cog(Quotes(bot))