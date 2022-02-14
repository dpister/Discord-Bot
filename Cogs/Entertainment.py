import discord
from discord.ext import commands
from discord.commands import Option
import random
import asyncio

from main import WarningEmbed, to_extras


class Entertainment(commands.Cog, description="Stuff to pass some time"):
    
    def __init__(self, bot):
        self.bot = bot
        self.caption = ":ferris_wheel: Entertainment :ferris_wheel:"
        self.color = (85,55,136)
    
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Choice has loaded successfully.")
    
    
    @to_extras(
        help="Picks things from a given list. Seperate things with a comma. "
            + "Specify the number of things to pick via `[!number_of_things]`.",
        usage="`/pick [!number_of_things] <element1,element2,...>`",
        caption=":game_die: Pick :game_die:",
        color=(234,89,110)
    )
    @commands.slash_command(description="Pick things from a given list.")
    async def pick(
        self,
        ctx: discord.ApplicationContext,
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



    @to_extras(
        help="The allmighty 8ball will answer your question.",
        caption=":8ball: 8Ball :8ball:",
        usage="`/8ball <question>`",
        color=(49,55,61)
    )
    @commands.slash_command(
        name="8ball",
        description="The allmighty 8ball will answer your question.",
    )
    async def eight_ball(
        self,
        ctx: discord.ApplicationContext,
        question: Option(str, "Your question")
    ):
        with open("Apps/8ball.txt","r") as file:
            answers = file.readlines()
        answer = random.choice(answers)
        em = discord.Embed(
            title="**Your question:**",
            description=question,
            color=discord.Color.from_rgb(54,57,63)
        )
        em.add_field(
            name="**My answer**:",
            value=answer
        )
        await ctx.respond(embed=em)
        
        
    @to_extras(
        help="Gives you a random question to discuss.",
        caption=":ice_cube::left_facing_fist: Icebreaker :right_facing_fist::ice_cube:",
        usage="`/icebreaker`",
        color=(193,225,234)
    )
    @commands.slash_command(description="Gives you a random question to discuss.")
    async def icebreaker(self, ctx: discord.ApplicationContext):
        with open("Apps/icebreakers.txt","r") as file:
            answers = file.readlines()
        answer = random.choice(answers)
        em = discord.Embed(
            title=f"**{answer}**",
            color=discord.Color.from_rgb(193,225,234)
        )
        await ctx.respond(embed=em)
        
        
     
    @to_extras(
        help="Pings a member every 3 seconds. Specify number of "
            + "messages via `[amount]` and content of message via `[message]`.",
        caption=":rage: Annoy :rage:",
        usage="`/annoy <@member> [amount] [message]`",
        color=(218,47,71))
    @commands.slash_command(description="Pings a member every 3 seconds.")                       
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def annoy(
        self,
        ctx: discord.ApplicationContext,
        member: Option(discord.Member, "The user you want to annoy"),
        amount: Option(int, "Number of times to ping the user", required=False,
                       default=5, min_value=1, max_value=1000),
        content: Option(str, "The message you want to spam", required=False, default="")
    ):
        if amount < 1:
            em = WarningEmbed("Amount is negative.")
            await ctx.respond(embed=em)
            return  
        em = discord.Embed(
            title=f":angry: Annoying {member.display_name} :angry:",
            color=discord.Color.from_rgb(255,203,76)
        )
        await ctx.respond(embed=em,delete_after=60)
        
        
        class MyView(discord.ui.View):
            def __init__(self, ctx):
                super().__init__(timeout=5)
                self.status = 0
                self.ctx = ctx
                self.msg = None
            
            @discord.ui.button(label="Stop!", style=discord.ButtonStyle.danger)
            async def button_callback(self, button, interaction):
                button.label = "Stopped"
                button.style = discord.ButtonStyle.green
                button.disabled = True
                await interaction.response.edit_message(view=self)
                self.timeout = None
                self.status = 1
            
            async def on_timeout(self):
                await self.msg.edit(view=None)
                self.status = -1
            
            async def delete_button(self):
                await self.msg.edit(view=None)
        
        views = []
        for i in range(amount):
            view = MyView(ctx)
            msg = await ctx.respond(member.mention+' '+content, view=view, delete_after=60)
            view.msg = msg
            views.append(view)
            await asyncio.sleep(3.1)
            views[:] = [x for x in views if not x.status == -1]         
            for j,item in enumerate(views):
                if item.status == 1:
                    for k,item in enumerate(views):
                        if k != j:
                            await item.delete_button()
                    return
    
    
def setup(bot):
    bot.add_cog(Entertainment(bot))