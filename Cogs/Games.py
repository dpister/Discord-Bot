import discord
from discord.ext import commands
from discord.commands import Option
import random
import asyncio

from Apps import tictactoe as ttt
from main import WarningEmbed, BetterButton, to_extras




class TicTacToeView(discord.ui.View):

    def __init__(self, ctx, grid, player1, player2, timeout=None):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.grid = grid
        self.msg = None
        self.emojis = {"x": "❌", "o": "⭕", "": None}
        self.players = (player1, player2)
        self.current_player = player1
    
    
    def next_player(self):
        index = self.players.index(self.current_player)
        if index == len(self.players) - 1:
            newindex = 0
        else:
            newindex = index + 1
        self.current_player = self.players[newindex]
    
    
    async def end_game(self, winner_symbol):
        if winner_symbol == "":
            em = discord.Embed(
                 title=":left_right_arrow: It's a draw. :left_right_arrow:",
                 color=discord.Color.from_rgb(59,136,195)
            )
        if winner_symbol == "x":
            em = discord.Embed(
                 title=f":crown: Congratulations! {self.players[0].display_name} won. :crown:",
                 color=discord.Color.green()
            )
        if winner_symbol == "o":
            if self.players[1] is None:
                em = discord.Embed(
                     title=":computer: Computer won. :computer:",
                     color=discord.Color.from_rgb(174,187,193)
                )
            else:
                em = discord.Embed(
                     title=f":crown: Congratulations! {self.players[1].display_name} won. :crown:",
                     color=discord.Color.green()
                )
        for button in self.children:
            if button.custom_id == "button_ff":
                ff_button = button
            else:
                button.disabled = True
        self.remove_item(ff_button)
        await self.msg.edit(embed=em, view=self)
        self.stop()
    
    
    async def on_timeout(self):
        em = WarningEmbed("Game timed out.")
        self.clear_items()
        await self.msg.edit(embed=em, view=self)
    
    
    async def computer_move(self):
        self.grid.comp_move()
        winner = self.grid.check_winner()   
        
        for row in range(3):   
            for col in range(3):
                button = [x for x in self.children if x.custom_id == f"button_{row}{col}"][0]
                button.emoji = self.emojis[self.grid.grid[row, col]]
                button.disabled = False if self.grid.grid[row, col] == "" else True
                
        if self.grid.turn_count == 9 or winner != "":
            await self.msg.edit(view=self)
            await self.end_game(winner)
        else:
            self.next_player()
            em = discord.Embed(
                title=f"It's your turn, {self.current_player.display_name}. Pick a box.",
                color=discord.Color.from_rgb(221,46,68)
            )
            await self.msg.edit(embed=em,view=self)
 
    
    #player move    
    def add_buttons(self):
        for row in range(3):
            for col in range(3):
                mybutton = BetterButton(
                    label=" ",style=discord.ButtonStyle.grey, row=row, 
                    custom_id=f"button_{row}{col}", disabled=True
                )
                async def button_callback(interaction, row, col):
                    if interaction.user != self.current_player:
                        return
                    symbol = "x" if self.current_player == self.players[0] else "o"
                    
                    for button in self.children:
                        if self.players[1] is None:
                            button.disabled = False if button.custom_id == "button_ff" else True
                        if button.custom_id == f"button_{row}{col}":
                            button.emoji = self.emojis[symbol]
                            button.disabled = True
                            
                    self.grid.grid[row, col] = symbol
                    self.grid.turn_count += 1
                    winner = self.grid.check_winner()
                    if self.grid.turn_count == 9 or winner  != "":
                        await self.end_game(winner)
                    else:
                        self.next_player()
                        title =(f"It's your turn, {self.current_player.display_name}" 
                                if self.current_player is not None else "It's my turn...")
                        em = discord.Embed(
                            title=title,
                            color=discord.Color.from_rgb(221,46,68)
                        )
                        await interaction.response.edit_message(embed=em, view=self)
                        if self.current_player is None:
                            await asyncio.sleep(2)
                            await self.computer_move()
                mybutton.callback = mybutton.new_callback(button_callback, row, col)
                self.add_item(mybutton)
         
                
        button = discord.ui.Button(label="give up",style=discord.ButtonStyle.red, row=1, 
                           custom_id="button_ff")
        async def button_ff_callback(interaction):
            if not interaction.user == self.current_player:
                return
            name = (self.current_player.display_name if self.current_player is not None 
                    else self.players[0].display_name)
            em = discord.Embed(
                title=f":flag_white: {name} surrendered. :flag_white:",
                color=discord.Color.from_rgb(255,255,255)
            )
            self.clear_items()
            await interaction.response.edit_message(embed=em, view=self)
            self.stop()
        button.callback=button_ff_callback
        self.add_item(button)
        



class RequestView(discord.ui.View):
    
    def __init__(self, player1, player2, timeout=300):
        super().__init__(timeout=timeout)
        self.msg = None
        self.pressed = False
        self.player1 = player1
        self.player2 = player2
        
        
    @discord.ui.button(
        label="Accept",
        style=discord.ButtonStyle.green,
        custom_id="accept"
    )
    async def accept_callback(self, button, interaction):
        if not interaction.user == self.player2:
            return
        self.accepted = True
        self.stop()
    
    
    @discord.ui.button(
        label="Decline",
        style=discord.ButtonStyle.red,
        custom_id="decline"
    )
    async def decline_callback(self, button, interaction):
        if not interaction.user == self.player2:
            return
        self.clear_items()
        em = discord.Embed(
            title="Request declined.", 
            color=discord.Color.from_rgb(255,0,0)
        )
        await interaction.response.edit_message(embed=em, view=self)
        self.stop()
        
        
    @discord.ui.button(
        label="Cancel",
        style=discord.ButtonStyle.grey,
        custom_id="cancel"
    )
    async def cancel_callback(self, button, interaction):
        if interaction.user != self.player1:
            return
        self.clear_items()
        em = discord.Embed(
            title="Request cancelled.", 
            color=discord.Color.from_rgb(255,0,0)
        )
        await interaction.response.edit_message(embed=em, view=self)
        self.stop()        
 
         
    async def on_timeout(self):
        em = WarningEmbed("Game timed out.")
        self.clear_items()
        await self.msg.edit(embed=em, view=self)




class Games(commands.Cog, description="Play some minigames"):
    
    def __init__(self, bot):
        self.bot = bot
        self.caption = ":video_game: Games :video_game:"
        self.color = (20,23,26)
    
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Games has loaded successfully.")
    
    
    @to_extras(
        help="Play a game of Tic Tac Toe. Play against the computer or "
            + " tag a member to play against them.",
        caption=":x::o: TicTacToe :o::x:",
        usage="`/tictactoe [member]`",
        color=(221,46,68)
    )
    @commands.slash_command(description="Play a game of Tic Tac Toe.")
    @commands.max_concurrency(1, commands.BucketType.user)
    async def tictactoe(
        self,
        ctx : discord.ApplicationContext,
        player2: Option(discord.Member, "Tag a member to play with.",
                       required=False, default=None)
    ):
        player1 = ctx.author
        
        if player2 is not None:
            em = discord.Embed(
                title=f"{player1.display_name} has challenged "
                + f"{player2.display_name} to a game of Tic Tac Toe!",
                color=discord.Color.teal()
            )
            view = RequestView(player1, player2)
            response = await ctx.respond(embed=em,view=view)
            msg = await response.original_message()
            view.msg = msg
            await view.wait()
            if view.accepted is not True:
                return
              
        grid = ttt.Grid()
        view = TicTacToeView(ctx, grid, player1, player2, timeout=60)
        view.add_buttons()
        opponent = "computer" if player2 is None else player2.display_name
        em = discord.Embed(
            title=":o: :x: Welcome to Tic Tac Toe! :x: :o:",
            description=f"{player1.display_name} plays :x: and {opponent} plays :o:",
            color=discord.Color.from_rgb(221,46,68)
        )
        if player2 is None:
            response = await ctx.respond(embed=em, view=view)
            msg = await response.original_message()
        else:
            await msg.edit(embed=em,view=view)
        view.msg = msg
        await asyncio.sleep(1)
        
        if random.random() > 0.5:
            view.next_player()
        if view.current_player is None:
            em.description += "\n\n**It's my turn first...**"
            await view.msg.edit(embed=em, view=view)
            await asyncio.sleep(2)
            await view.computer_move()         
        else:
            em.description += f"\n\n**It's your turn, {view.current_player.display_name}. Pick a box.**"
            for button in view.children:
                button.disabled = False
            await view.msg.edit(embed=em, view=view)
            
        
        
def setup(bot):
    bot.add_cog(Games(bot))