import tkinter as tk
from tkinter import font, messagebox, simpledialog
from itertools import cycle
from typing import NamedTuple
import random


class Player(NamedTuple):
    label: str
    color: str


class Move(NamedTuple):
    row: int
    col: int
    label: str = ""


# Constants
BOARD_SIZE = 3
DEFAULT_PLAYERS = (
    Player(label="X", color="blue"),
    Player(label="O", color="green"),
)


# Tic-Tac-Toe game logic
class TicTacToeGame:
    def __init__(self, players=DEFAULT_PLAYERS, board_size=BOARD_SIZE, play_with_ai=False, difficulty="medium"):
        self._players = cycle(players)
        self.board_size = board_size
        self.play_with_ai = play_with_ai
        self.difficulty = difficulty
        self.current_player = next(self._players)
        self.winner_combo = []
        self._current_moves = []
        self._has_winner = False
        self._winning_combos = []
        self._setup_board()

    def _setup_board(self):
        self._current_moves = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._winning_combos = self._get_winning_combos()

    def _get_winning_combos(self):
        rows = [
            [(move.row, move.col) for move in row]
            for row in self._current_moves
        ]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]

    def toggle_player(self):
        self.current_player = next(self._players)

    def is_valid_move(self, move):
        row, col = move.row, move.col
        move_was_not_played = self._current_moves[row][col].label == ""
        no_winner = not self._has_winner
        return no_winner and move_was_not_played
    def process_move(self, move):
        row, col = move.row, move.col
        self._current_moves[row][col] = move
        for combo in self._winning_combos:
            results = set(self._current_moves[n][m].label for n, m in combo)
            is_win = (len(results) == 1) and ("" not in results)
            if is_win:
                self._has_winner = True
                self.winner_combo = combo  # Set the winning combination
                break


    def has_winner(self):
        return self._has_winner

    def is_tied(self):
        no_winner = not self._has_winner
        played_moves = (
            move.label for row in self._current_moves for move in row
        )
        return no_winner and all(played_moves)

    def reset_game(self):
        for row, row_content in enumerate(self._current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)
        self._has_winner = False
        self.winner_combo = []

    def get_ai_move_with_difficulty(self):
        if self.difficulty == "easy":
            return self._random_move()
        elif self.difficulty == "medium":
            return self._medium_move()
        else:
            return self._minimax_move()

    def _random_move(self):
        empty_cells = [
            move for row in self._current_moves for move in row if move.label == ""
        ]
        return random.choice(empty_cells) if empty_cells else None

    def _medium_move(self):
        winning_move = self._find_winning_move("O")
        blocking_move = self._find_winning_move("X")
        if winning_move:
            return winning_move
        if blocking_move:
            return blocking_move
        return self._random_move()

    def _find_winning_move(self, player_label):
        for combo in self._winning_combos:
            moves = [self._current_moves[n][m] for n, m in combo]
            labels = [move.label for move in moves]
            if labels.count(player_label) == self.board_size - 1 and "" in labels:
                empty_index = labels.index("")
                return moves[empty_index]
        return None

    def _minimax_move(self):
        best_score = float("-inf")
        best_move = None

        for row in range(self.board_size):
            for col in range(self.board_size):
                if self._current_moves[row][col].label == "":
                    self._current_moves[row][col] = Move(row, col, "O")
                    score = self._minimax(depth=0, is_maximizing=False)
                    self._current_moves[row][col] = Move(row, col)
                    if score > best_score:
                        best_score = score
                        best_move = Move(row, col, "O")
        return best_move

    def _minimax(self, depth, is_maximizing):
        if self.has_winner():
            return 1 if is_maximizing else -1
        elif self.is_tied():
            return 0

        if is_maximizing:
            best_score = float("-inf")
            for row in range(self.board_size):
                for col in range(self.board_size):
                    if self._current_moves[row][col].label == "":
                        self._current_moves[row][col] = Move(row, col, "O")
                        score = self._minimax(depth + 1, False)
                        self._current_moves[row][col] = Move(row, col)
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float("inf")
            for row in range(self.board_size):
                for col in range(self.board_size):
                    if self._current_moves[row][col].label == "":
                        self._current_moves[row][col] = Move(row, col, "X")
                        score = self._minimax(depth + 1, True)
                        self._current_moves[row][col] = Move(row, col)
                        best_score = min(score, best_score)
            return best_score


# Tic-Tac-Toe board with enhanced interface
class TicTacToeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tic-Tac-Toe")
        self.geometry("300x500")
        self.configure(bg="lightblue")

        self.play_with_ai = False
        self.difficulty = "medium"
        self.game = None

        self.create_start_screen()

    def create_start_screen(self):
        # Clear any existing widgets in the window
        for widget in self.winfo_children():
            widget.destroy()

        # Display the game title
        tk.Label(
            self,
            text="Welcome to Tic-Tac-Toe!",
            font=font.Font(size=12, weight="bold"),
            bg="lightblue",
        ).pack(pady=20)

        # Button for playing against AI
        tk.Button(
            self,
            text="Play with AI",
            font=font.Font(size=14),
            command=self.choose_difficulty,
        ).pack(pady=10)

        # Button for playing with a friend (2-player mode)
        tk.Button(
            self,
            text="Play with a Friend",
            font=font.Font(size=14),
            command=self.start_two_player_game,
        ).pack(pady=10)

        # Add a Reset Button that restarts the game
        tk.Button(
            self,
            text="Reset Game",
            font=font.Font(size=14),
            command=self.reset_game,
            bg="lightgray"
        ).pack(pady=10)

    def choose_difficulty(self):
        difficulty = simpledialog.askstring(
            "Choose Difficulty", "Enter difficulty (easy, medium, hard):"
        )
        if difficulty and difficulty.lower() in {"easy", "medium", "hard"}:
            self.play_with_ai = True
            self.difficulty = difficulty.lower()
            self.start_game()
        else:
            messagebox.showerror("Invalid Input", "Please choose a valid difficulty!")

    def start_two_player_game(self):
        self.play_with_ai = False
        self.start_game()

    def start_game(self):
        self.game = TicTacToeGame(play_with_ai=self.play_with_ai, difficulty=self.difficulty)
        TicTacToeBoard(self, self.game).pack(expand=True, fill="both")

    def reset_game(self):
        # When reset is clicked, the start screen is reloaded, clearing the board
        self.game = None
        self.create_start_screen()



class TicTacToeBoard(tk.Frame):
    def __init__(self, master, game):
        super().__init__(master, bg="white")
        self.master = master
        self._cells = {}
        self._game = game

        self._create_board_display()
        self._create_board_grid()

    def _create_board_display(self):
        display_frame = tk.Frame(self, bg="white")
        display_frame.pack(fill=tk.X)
        self.display = tk.Label(
            master=display_frame,
            text=f"{self._game.current_player.label}'s Turn",
            font=font.Font(size=18, weight="bold"),
            bg="white",
        )
        self.display.pack()

    def _create_board_grid(self):
        canvas = tk.Canvas(self, bg="white")
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        grid_frame = tk.Frame(canvas, bg="white")

        grid_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=grid_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._cells = {}
        for row in range(self._game.board_size):
            for col in range(self._game.board_size):
                button = tk.Button(
                    master=grid_frame,
                    text="",
                    font=font.Font(size=24, weight="bold"),  # Adjust font size for smaller cells
                    fg="black",
                    width=2,
                    height=1,
                    command=lambda row=row, col=col: self.cell_clicked(row, col),
                    relief="solid",
                    borderwidth=2
                )
                button.grid(row=row, column=col, padx=5, pady=5)
                self._cells[(row, col)] = button

    def cell_clicked(self, row, col):
        if self._game.has_winner() or self._game.is_tied():
            return  # Prevent further moves after the game ends

        if self._game.is_valid_move(self._game._current_moves[row][col]):
            move = Move(row, col, self._game.current_player.label)
            self._game.process_move(move)
            self._update_board()

            if self._game.has_winner():
                self.display.configure(text=f"{self._game.current_player.label} Wins!")
                self._highlight_winning_combo()
                self.update()
                self.after(100, lambda: None)  # Add a small delay
                return
            elif self._game.is_tied():
                self.display.configure(text="It's a tie!")
                self.update()
                self.after(100, lambda: None)  # Add a small delay
                return

            self._game.toggle_player()
            self._update_turn_display()

            if self._game.play_with_ai and self._game.current_player.label == "O":
                self._ai_move()

    def _update_board(self):
        for row in range(self._game.board_size):
            for col in range(self._game.board_size):
                move = self._game._current_moves[row][col]
                self._cells[(row, col)].config(text=move.label, fg=self._get_player_color(move.label))

    def _update_turn_display(self):
        self.display.config(text=f"{self._game.current_player.label}'s Turn")

    def _highlight_winning_combo(self):
        # Highlight the cells that are part of the winning combination
        for row, col in self._game.winner_combo:
            self._cells[(row, col)].config(bg="yellow")

    def _ai_move(self):
        ai_move = self._game.get_ai_move_with_difficulty()
        if ai_move:
            self._game.process_move(ai_move)
            self._update_board()
            if self._game.has_winner():
                self.display.config(text="AI Wins!")
                self._highlight_winning_combo()
                return  # Add this line to prevent further actions
            elif self._game.is_tied():
                self.display.config(text="It's a tie!")
                return  # Add this line to prevent further actions
            self._game.toggle_player()
            self._update_turn_display()

    def _get_player_color(self, player_label):
        if player_label == "X":
            return "blue"
        elif player_label == "O":
            return "green"
        return "black"
    
    def reset_game(self):
        self._game.reset_game()
        self._update_board()
        self._update_turn_display()
        self.display.config(text=f"{self._game.current_player.label}'s Turn")
        for button in self._cells.values():
            button.config(bg="white")

    def quit_game(self):
        self.master.quit()




if __name__ == "__main__":
    app = TicTacToeApp()
    app.mainloop()