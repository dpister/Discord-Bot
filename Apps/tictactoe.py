import random as rd
import numpy as np

class Grid:
    
    def __init__(self):
        self.grid = np.array([["","",""], ["","",""], ["","",""]])
        self.turn_count = 0

    def rotate(self):
        new_grid = np.array([["","",""],["","",""],["","",""]])    
        new_grid[1,1] = self.grid[1,1]
        new_grid[0,0] = self.grid[2,0]
        new_grid[2,0] = self.grid[2,2]
        new_grid[2,2] = self.grid[0,2]
        new_grid[0,2] = self.grid[0,0]
        new_grid[0,1] = self.grid[1,0]
        new_grid[1,0] = self.grid[2,1]
        new_grid[2,1] = self.grid[1,2]
        new_grid[1,2] = self.grid[0,1]
        self.grid = new_grid

    def mirror(self):
        new_grid = np.array([["","",""], ["","",""], ["","",""]])
        new_grid[:,0] = self.grid[:,2]
        new_grid[:,1] = self.grid[:,1]
        new_grid[:,2] = self.grid[:,0]
        self.grid = new_grid
        
    def reverse(self, i, j):
        while j < 4:
            self.rotate()
            j += 1
        if i == 1:
            self.mirror()
        # undo loop through symmetry group of grid with rotate and mirror

    def best_move(self):
        pos_diag = ((2,0), (1,1), (0,2))
        neg_diag = ((0,0), (1,1), (2,2))
        empty_spots = []
        
        # check if can win
        for i in range(3):
            for j in range(3):
                if self.grid[i,j] == "":
                    empty_spots.append((i,j)) # save empty spots
                if (self.grid[i,j] == self.grid[(i+1)%3,j] == "o" 
                and self.grid[(i+2)%3,j] == ""):
                    self.grid[(i+2)%3,j] = "o" #columns
                    return 
                if (self.grid[i,j] == self.grid[i,(j+1)%3] == "o" 
                    and self.grid[i,(j+2)%3] == ""):
                    self.grid[i,(j+2)%3] = "o" #rows
                    return 
        for i in range(3):
            if (self.grid[pos_diag[i]] == self.grid[pos_diag[(i+1)%3]] == "o" 
            and self.grid[pos_diag[(i+2)%3]] == ""):
                self.grid[pos_diag[(i+2)%3]] = "o" #pos diagonal
                return 
            if (self.grid[neg_diag[i]] == self.grid[neg_diag[(i+1)%3]] == "o" 
            and self.grid[neg_diag[(i+2)%3]] == ""):
                self.grid[neg_diag[(i+2)%3]] = "o" #neg diagonal
                return 
        
        # check if has to block
        for i in range(3):
            for j in range(3):
                if (self.grid[i,j] == self.grid[(i+1)%3,j] == "x" 
                and self.grid[(i+2)%3,j] == ""):
                    self.grid[(i+2)%3,j] = "o" #columns
                    return 
                if (self.grid[i,j] == self.grid[i,(j+1)%3] == "x" 
                and self.grid[i,(j+2)%3] == ""):
                    self.grid[i,(j+2)%3] = "o" #rows
                    return 
        for i in range(3):
            if (self.grid[pos_diag[i]] == self.grid[pos_diag[(i+1)%3]] == "x" 
            and self.grid[pos_diag[(i+2)%3]] == ""):
                self.grid[pos_diag[(i+2)%3]] = "o" #pos diagonal
                return 
            if (self.grid[neg_diag[i]] == self.grid[neg_diag[(i+1)%3]] == "x" 
            and self.grid[neg_diag[(i+2)%3]] == ""):
                self.grid[neg_diag[(i+2)%3]] = "o" #neg diagonal
                return 
            
        # else pick a random empty cell
        self.grid[rd.choice(empty_spots)] = "o"
    

    def draw(self):
        lines=[
            f"  {self.grid[0,0]}  |   {self.grid[0,1]}   |  {self.grid[0,2]}  ",
            "------------------",
            f"  {self.grid[1,0]}  |   {self.grid[1,1]}   |  {self.grid[1,2]}  ",
            "------------------",
            f"  {self.grid[2,0]}  |   {self.grid[2,1]}   |  {self.grid[2,2]}  "
        ]    
        for line in lines:
            print(line)
    
    def check_winner(self) -> str:
        winner_symbol = ""
        for i in range(3):
            if self.grid[i,0] == self.grid[i,1] == self.grid[i,2] != "":
                winner_symbol = self.grid[i,0] # row
            if self.grid[0,i] == self.grid[1,i] == self.grid[2,i] != "":
                winner_symbol = self.grid[0,i] # column
        if self.grid[0,0] == self.grid[1,1] == self.grid[2,2] !="" :
            winner_symbol = self.grid[0,0] # neg diag
        if self.grid[0,2] == self.grid[1,1] == self.grid[2,0] != "":
            winner_symbol = self.grid[1,1] # pos diag
        return winner_symbol

    
    def comp_move(self):
        corners = [(0,0),(2,0),(0,2),(2,2)] 
        
        if self.turn_count == 1: # 1 symbol placed
            self.turn_count += 1
            if self.grid[1,1] == "x": # mid blocked: pick random corner
                self.grid[rd.choice(corners)] = "o"
            else:
                self.grid[1,1] = "o" # mid available: pick mid
            return
        
        if self.turn_count == 3: # 3 symbols placed
            self.turn_count += 1
            
            if self.grid[1,1] == "o": # comp played mid in turn 1
                if (self.grid[0,0] == self.grid[2,2] == "x" 
                or self.grid[0,2] == self.grid[2,0] == "x"):
                    self.grid[0,1] = "o" # copposite corners: pick side
                    return
                if (self.grid[1,0] == self.grid[1,2] == "x" 
                or self.grid[0,1] == self.grid[2,1] == "x"):
                    self.grid[0,0] = "o" #opposite sides: pick a corner 
                    return
               
                for i in range(2):
                    for j in range(4):
                        if self.grid[2,0] == self.grid[0,1] == "x":
                            self.grid[0,0] = "o" # corner + far side: pick close corner
                            self.reverse(i,j)
                            return 
                        self.rotate()
                    self.mirror()
                self.best_move() # else do best move
                
            else: # comp played corner in turn 1
                for i in range(2):
                    for j in range(4):
                        if self.grid[2,0] == "o" and self.grid[0,2] == "x":
                            self.grid[0,0] = "o" # mid and opposite corner: pick a corner
                            self.reverse(i,j)
                            return 
                        self.rotate()
                    self.mirror()
                self.best_move() # else do best move
            return
                
        
        if self.turn_count > 4:
            self.turn_count += 1
            self.best_move()
            return
    
                
        if self.turn_count == 0: # no symbols placed
            self.turn_count += 1
            if rd.random() > 0.5: # 50/50 pick mid or corner
                self.grid[1,1] = "o"
            else:
                i,j = rd.choice(corners)
                self.grid[i,j] = "o"
            return
    
        
        if self.turn_count == 2: # 2 symbols placed
            self.turn_count += 1
            if self.grid[1,1] == "o": # comp played mid in turn 0
                for i in range(2):
                    for j in range(4):
                        if self.grid[0,0] == "x":
                            self.grid[2,2] = "o" # corner: pick opposite corner
                            self.reverse(i,j)
                            return 
                        if self.grid[0,1] == "x":
                            self.grid[2,2] = "o" # side: pick far corner
                            self.reverse(i,j)
                            return 
                        self.rotate()
                    self.mirror()
                    
            else: # comp played corner in turn 0
                for i in range(2):
                    for j in range(4):
                        if self.grid[0,0] == "o" and self.grid[1,1] == "x":
                            self.grid[2,2] = "o" # mid: pick opposite corner
                            self.reverse(i,j)
                            return 
                        if self.grid[0,0] == "o" and self.grid[0,1] == "x":
                            self.grid[2,0] = "o" # close side: pick opposite corner
                            self.reverse(i,j)
                            return 
                        if self.grid[0,0] == "o" and self.grid[2,1] == "x":
                            self.grid[2,0]="o" # far side: pick opposite corner
                            self.reverse(i,j)
                            return 
                        if self.grid[0,0] == "o" and self.grid[0,2] == "x":
                            self.grid[2,0] = "o" # corner in same row: pick corner in other row
                            self.reverse(i,j)
                            return 
                        if self.grid[0,0] == "o" and self.grid[2,2] == "x":
                            self.grid[2,0] = "o" # opposite corner: pick corner in same row
                            self.reverse(i,j)
                            return 
                        self.rotate()
                    self.mirror()
            return
        
        if self.turn_count == 4:
            self.turn_count += 1
            
            if self.grid[1,1] == "o": # comp picked mid at some point
                for i in range(2):
                        for j in range(4):
                            if self.grid[0,0] == "o" and self.grid[2,2] == "x": 
                            # comp and player have opposite corners
                                if self.grid[1,0] == "x": # side: pick far corner
                                    self.grid[0,2] = "o"
                                    self.reverse(i,j)
                                    return 
                            self.rotate()
                        self.mirror()
                self.best_move() # else do best move
                
            else: # comp did not take mid
                for i in range(2):
                    for j in range(4):
                        if (self.grid[0,0] == self.grid[2,0] == "o" 
                        and self.grid[1,0] == "x"): 
                        # comp picked both corners and player picked side in a row
                            if self.grid[0,1] == "x": 
                            # player's 2nd symbol is close side: pick opposite corner
                                self.grid[2,2] = "o"
                                self.reverse(i,j)
                                return 
                            if self.grid[0,2] == "x": 
                            #player's 2nd symbol is corner: pick opposite corner
                                self.grid[2,2] = "o"
                                self.reverse(i,j)
                                return 
                        self.rotate()
                    self.mirror()
                self.best_move()
            return

    def move(self, pos, symbol):
        self.turn_count += 1
        self.grid[pos[0]][pos[1]] = symbol
        
    def restart(self):
        self.grid = np.array([["","",""], ["","",""], ["","",""]])
        self.turn_count = 0
        

def player_input(grid):
    x = True
    while x is True:
        num_box = int(input("Pick a box: "))-1 # takes player input
        if grid[num_box//3, num_box%3] == "":
            pos = (num_box//3, num_box%3) # applies it to grid
            x = False
        else:
            print("Invalid input. Pick a box: ")
    return pos
            
                    
def end_game(winner_symbol):
    if winner_symbol == "":
        print("It's a draw.")
    if winner_symbol == "x":
        print("Congratulations! You won.")
    if winner_symbol == "o":
        print("Computer won.")
        

def main():
    print("Welcome to Tic Tac Toe!")
    grid = Grid()
    grid.draw()
    
    if rd.random() > 0.5:
        print("I am going first.")
        grid.comp_move()
        grid.draw()
       
    while True:        
        pos = player_input(grid.grid)
        grid.move(pos, "x")
        grid.draw()
        winner_symbol = grid.check_winner()
        if grid.turn_count == 9 or winner_symbol != "":
            end_game(winner_symbol)
            break
        
        grid.comp_move()
        grid.draw()
        winner_symbol = grid.check_winner()
        if grid.turn_count == 9 or winner_symbol != "":
            end_game(winner_symbol)
            break
            
        
if __name__=='__main__':
    main()