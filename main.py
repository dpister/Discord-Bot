import discord
from discord.ext import commands
from discord.commands import SlashCommand
import sqlite3
import os

import config 


bot = discord.Bot(debug_guilds=config.GUILD_IDS)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("/help for info."))
    print("Bot has loaded successfully.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = WarningEmbed("Command is on cooldown.")
        await ctx.respond(embed=em)
    else:
        raise error
        
          
@bot.slash_command()
async def help(ctx, module=None):
    em = None
    
    if module is None: 
        em = discord.Embed(
            title=":grey_question: Help :grey_question:",
            description="Hello, these are the modules I have. "
            + "Use `/help [module]` to see all commands inside a module.",
            color=discord.Color.from_rgb(204,214,221)
        )
        for cog in bot.cogs.values():
            em.add_field(
                name=cog.caption,
                value=cog.description
            )
        
    else:
        for key, cog in bot.cogs.items():
            if module.capitalize() == key:
                key = module.capitalize()
                cog = bot.cogs[key]
                em = discord.Embed(
                    title=cog.caption,
                    description=cog.description,
                    color=discord.Color.from_rgb(*cog.color)
                )
                for command in cog.walk_commands():
                    em.add_field(
                        name=command.name,
                        value=command.description if isinstance(command, SlashCommand) else "No description given"
                    )             
    if em == None:
        em = WarningEmbed("Command or module doesn't exist.")
    await ctx.respond(embed=em)


class WarningEmbed(discord.Embed):
    def __init__(self, warning: str):
        super().__init__(
            title=":warning: Error :warning:",
            description=warning,
            color=discord.Color.from_rgb(255,204,77)
        )
 

def sql_input(string: str, mytuple: tuple):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute(string, mytuple)
    conn.commit()
    quote_id = cursor.lastrowid
    conn.close()
    return quote_id


def sql_fetch(string: str, mytuple: tuple):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute(string, mytuple)
    data = cursor.fetchall()
    conn.commit()
    conn.close()
    return data


for filename in os.listdir("./Cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"Cogs.{filename[:-3]}")


bot.run(config.TOKEN)