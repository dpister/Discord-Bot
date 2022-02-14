import discord
from discord.ext import commands
from discord.commands import SlashCommand
import sqlite3
import os

import config 


bot = discord.Bot(debug_guilds=config.GUILD_IDS)
bot.conn = sqlite3.connect("bot_database.db")
extras={}


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("/help for info."))
    print("Bot has loaded successfully.")



@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = WarningEmbed("Command is on cooldown.")
        await ctx.respond(embed=em)
    elif isinstance(error, commands.MaxConcurrencyReached):
        em = WarningEmbed("This command is already running.")
        await ctx.respond(embed=em)
    else:
        raise error
        
        
        
@bot.slash_command()
async def help(ctx, module_or_command=None):
    em = None
    
    if module_or_command is None: 
        em = discord.Embed(
            title=":grey_question: Help :grey_question:",
            description="Hello, I'm Senketsu and I can do a little bit of everything. " 
            + "Here's a list of my modules. Use `/help [module]` for more info."
            + "\n_ _\n_ _\n",
            color=discord.Color.from_rgb(204,214,221)
        )
        em.set_thumbnail(url=bot.user.avatar.url)
        for cog in bot.cogs.values():
            em.add_field(
                name=cog.caption,
                value=cog.description+"\n_ _\n",
                inline=False
            )
        
    else:
        for key, cog in bot.cogs.items():
            if module_or_command.capitalize() == key:
                key = module_or_command.capitalize()
                em = discord.Embed(
                    title=cog.caption,
                    description=cog.description +"\n_ _\n_ _\n",
                    color=discord.Color.from_rgb(*cog.color)
                )
                for command in cog.walk_commands():
                    em.add_field(
                        name=extras[command.name]["caption"],
                        value=
                            ((command.description+"\n_ _\n") if isinstance(command, SlashCommand)
                            else (extras[command.name]["description"]+"\n_ _\n")),
                        inline=False
                    )
                break
            for command in cog.walk_commands():
                if module_or_command.lower() == command.name:
                    em = discord.Embed(
                        title=extras[command.name]["caption"],
                        description=extras[command.name]["help"]+"\n_ _\n_ _\n",
                        color=discord.Color.from_rgb(*extras[command.name]["color"])
                    )
                    em.add_field(
                        name="**Usage**",
                        value=extras[command.name]["usage"]+"\n_ _\n"
                    )
                    break
                
    if em == None:
        em = WarningEmbed("Command or module doesn't exist.")
    else: 
        em.set_footer(text=f"developed by {config.AUTHOR_NAME}", icon_url=config.AUTHOR_PFP)
    await ctx.respond(embed=em)



class WarningEmbed(discord.Embed):
    def __init__(self, warning: str):
        super().__init__(
            title=":warning: Error :warning:",
            description=warning,
            color=discord.Color.from_rgb(255,204,77)
        )
        
        
        
class BetterButton(discord.ui.Button):        
    def new_callback(self, function, *args):
        def callback(interaction): 
            return function(interaction, *args)
        return callback
 
    
 
def to_extras(**kwargs):
    def decorator(command):
        mydict = {}
        for key, value in kwargs.items():
            mydict[key] = value
        extras[command.name] = mydict
        return command
    return decorator



for filename in os.listdir("./Cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"Cogs.{filename[:-3]}")



bot.run(config.TOKEN)
#self.extras: Optional[Dict] = kwargs.get('extras') to class ApplicationCommand