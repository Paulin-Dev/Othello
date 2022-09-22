from tkinter import *

class Gui:

    def __init__(self, width: int = 500, height: int = 500, player1: str = "Player 1", player2: str = "Player 2") -> None:

        self.width = width
        self.height = height

        self.part_x = (self.width-6)/8
        self.part_y = (self.height-6)/8

        self.create_window()
        self.add_text()
        self.create_grid()

        self.game = Game(player1, player2)

        self.update_text()

        try:
            self.win.mainloop()
        except KeyboardInterrupt:
            exit()

    def create_window(self) -> None:
        self.win = Tk()
        self.win.title("Othello")
        self.win.geometry(f"{self.width}x{self.height+20}")
        self.win.resizable(False, False)

    def add_text(self) -> None:
        self.label = Label(self.win, text="")
        self.label.grid(row=0, column=0)

    def update_text(self) -> None:
        for player in self.game.players:
            if player.id == self.game.current_player:
                self.label["text"] = f"It's {player.nickname}'s turn"

    def create_grid(self) -> None:
        self.canvas = Canvas(self.win, width=self.width, height=self.height)

        for i in range(8):
            for j in range(8):
                self.canvas.create_rectangle(j*self.part_x+2, i*self.part_y+2, (j+1)*self.part_x+2, (i+1)*self.part_y+2, fill="#347438")
        
        for i in range(8):
            for j in range(8):
                if i == 3 and j == 3 or i == 4 and j == 4:
                    self.canvas.create_oval(j*self.part_x+5, i*self.part_y+5, (j+1)*self.part_x-2, (i+1)*self.part_y-2, fill="#E8F4F0", outline="#347438")
                elif i == 3 and j == 4 or i == 4 and j == 3:
                    self.canvas.create_oval(j*self.part_x+5, i*self.part_y+5, (j+1)*self.part_x-2, (i+1)*self.part_y-2, fill="#2A2E31", outline="#347438")
                else:
                    self.canvas.create_oval(j*self.part_x+5, i*self.part_y+5, (j+1)*self.part_x-2, (i+1)*self.part_y-2, fill="#347438", outline="#347438")

        self.canvas.grid(row=1, column=0)
        self.canvas.bind("<Button-1>", self.change_color)


    def change_color(self, event: object) -> None:
        pos = self.get_row_col(event.x, event.y)
        enemies = self.game.get_enemies(pos)
        if self.game.get_value(pos) is None and enemies[1]:

            if self.game.current_player == 1:
                self.canvas.itemconfig(self.get_circle(self.get_row_col(event.x, event.y)), fill="#2A2E31")
                
            elif self.game.current_player == -1:
                self.canvas.itemconfig(self.get_circle(self.get_row_col(event.x, event.y)), fill="#E8F4F0")
                
            self.game.set_value(pos, self.game.current_player)

            for enemy in enemies[1]:
                if enemies[0] == 1:
                    self.canvas.itemconfig(self.get_circle(enemy), fill="#2A2E31")
                elif enemies[0] == -1:
                    self.canvas.itemconfig(self.get_circle(enemy), fill="#E8F4F0")
                
                self.game.set_value((enemy[0], enemy[1]), self.game.current_player)

            end = self.game.check_game_over()
            if end is not None:
                for player in self.game.players:
                    if player.id == 1:
                        nick1 = player.nickname
                    elif player.id == -1:
                        nick2 = player.nickname
                self.canvas.create_text(
                    self.width/2,
                    self.height/2,
                    text=f"{nick1} (Black) : {end[0]} points\n{nick2} (White) : {end[1]} points",
                    justify="center",
                    fill="red"
                )
            else:
                self.game.next_player()
                self.update_text()

            return None
        

        if self.game.cannot_play() and self.game.check_game_over() is None:
            for player in self.game.players:
                if player.id == self.game.current_player:
                    print(f"{player.nickname} can't play, player changeover")
                    self.game.next_player()

    def get_circle(self, pos: tuple[int, int]) -> int:
        return (pos[1]+8*pos[0])+65

    def get_row_col(self, x: int, y: int) -> tuple[int, int]:
        column = 0
        row = 0
        for i in range(8):
            if x - i*self.part_x > 0:
                column = i
            if y - i*self.part_y > 0:
                row = i
        return row, column


class Game:

    def __init__(self, p1: str, p2: str) -> None:
        self.create_grid()
        self.create_players(p1, p2)
        self.current_player = 1
        # black : 1, white : -1

    def create_grid(self) -> None:
        self.grid = []
        for i in range(8):
            self.grid.append([])
            for j in range(8):
                self.grid[i].append([])
                if i == 3 and j == 3 or i == 4 and j == 4:
                    self.grid[i][j] = -1
                elif i == 3 and j == 4 or i == 4 and j == 3:
                    self.grid[i][j] = 1
                else:
                    self.grid[i][j] = None

    def get_value(self, pos: tuple[int, int]) -> None or int:
        return self.grid[pos[0]][pos[1]]

    def set_value(self, pos: tuple[int, int], value: int) -> None:
        self.grid[pos[0]][pos[1]] = value

    def create_players(self, p1: str, p2: str) -> None:
        self.players = [Player(1, p1), Player(-1, p2)]

    def next_player(self) -> None:
        self.current_player *= -1

    def get_enemies(self, pos: tuple[int, int]) -> tuple[int, list]:
        enemies = []
        for i in range(3):
            for j in range(3):
                x, y = pos[0]-1+i, pos[1]-1+j
                if (x, y) != pos and 0 <= x <= 7 and 0 <= y <= 7:
                    if self.grid[x][y] == self.current_player * -1:
                        enemies_to_ally = self.check_ally(pos, (x, y))
                        if enemies_to_ally:
                            for enemy in enemies_to_ally:
                                enemies.append(enemy)

        return self.current_player, enemies

    def check_ally(self, current: tuple[int, int], enemy: tuple[int, int]) -> list:
        enemies = []
        for i in range(2, 8):
            x, y = current[0]+(enemy[0]-current[0])*i, current[1]+(enemy[1]-current[1])*i
            if 0 <= x <= 7 and 0 <= y <= 7:
                if self.grid[x][y] == self.current_player * -1:
                    enemies.append((x, y))
                elif self.grid[x][y] == self.current_player:
                    enemies.append(enemy)  
                    return enemies
                else:
                    return []

            else:
                return []

    def check_game_over(self) -> None or tuple[int, int]:
        
        for l in self.grid:
            for value in l:
                if value is None:
                    return None

        return self.count()

    def count(self) -> tuple[int, int]:
        p1 = 0
        p2 = 0
        for l in self.grid:
            for value in l:
                if value == 1:
                    p1 += 1
                elif value == -1:
                    p2 += 1
        return p1, p2

    def cannot_play(self) -> bool:
        for x in range(8):
            for y in range(8):
                if self.grid[x][y] is None:
                    if self.get_enemies((x, y)):
                        return False
        return True


class Player:

    def __init__(self, player_id: int, nickname: str) -> None:
        self.id = player_id
        self.nickname = nickname


if __name__ == "__main__":
    Gui(700, 700, "Bob", "Olivia")
