import discord
from discord.ext import commands
from discord.commands import Option
import random
import asyncio

from lists import get_8ball_answers
from main import WarningEmbed


class Choice(commands.Cog, description="Commands that choose something based on RNG"):
    
    def __init__(self, bot):
        self.bot = bot
        self.caption = ":thinking: Choice :thinking:"
        self.color = (255,203,76)
    
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Choice has loaded successfully.")
    
    
    @commands.slash_command(description="Pick things from a given list.")
    async def pick(
        self,
        ctx: commands.Context,
        things: Option(str, "Things to pick from"),
        amount: Option(int, "Number of things to pick", required=False, 
                       default=1, min_value=1)
    ):             
        if amount < 1:
            em = WarningEmbed("Amount is negative.")
            await ctx.respond(embed=em)
            return
        things = things.split(",")
        
        if amount > len(things):
            em = WarningEmbed("Number of picks is higher than number of things.")
            await ctx.respond(embed=em)
            return
        
        for i, element in enumerate(things):     
            if element == "":
                em = WarningEmbed("Some things are empty.")
                await ctx.respond(embed=em)
                return
            while element[0] == " ":
                element = element[1:]
            while element[-1] == " ":
                element = element[:-1]
            if element == "":
                em = WarningEmbed("Some things are empty.")
                await ctx.respond(embed=em)
                return
            things[i] = element
            
        choice = random.sample(things, amount)
        em = discord.Embed(
            title=":game_die: The die is cast :game_die:",
            description="Final choice:\n"+", ".join(choice),
            color=discord.Color.from_rgb(234,89,110)
        )
        await ctx.respond(embed=em)


    @commands.slash_command(
        name="8ball",
        description="The allmighty 8ball will answer your question."
    )
    async def eight_ball(
        self,
        ctx: commands.Context,
        question: Option(str, "Your question")
    ):
        em = discord.Embed(
            title="**Your question:**",
            description=question,
            color=discord.Color.from_rgb(49,55,61)
        )
        em.add_field(
            name="**My answer**:",
            value=random.choice(get_8ball_answers())
        )
        await ctx.respond(embed=em)
        
    
def setup(bot):
    bot.add_cog(Choice(bot))