from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QGridLayout, QVBoxLayout, QMessageBox, QInputDialog, QAction
)
from PyQt5.QtCore import Qt

from game import TicTacToeGame, Move


class TicTacToeWindow(QMainWindow):
    """PyQt5 interface for the Tic-Tac-Toe game."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tic-Tac-Toe (PyQt)")
        self.game = TicTacToeGame()
        self.scores = {"X": 0, "O": 0}
        self._create_ui()

    def _create_ui(self):
        self.status_label = QLabel(f"{self.game.current_player.label}'s Turn")
        self.score_label = QLabel(self._score_text())

        central = QWidget()
        self.setCentralWidget(central)
        vbox = QVBoxLayout(central)
        vbox.addWidget(self.status_label, alignment=Qt.AlignCenter)
        vbox.addWidget(self.score_label, alignment=Qt.AlignCenter)

        self.grid_layout = QGridLayout()
        vbox.addLayout(self.grid_layout)
        self.buttons = {}
        for row in range(self.game.board_size):
            for col in range(self.game.board_size):
                button = QPushButton("")
                button.setFixedSize(80, 80)
                button.setStyleSheet("font-size: 24px;")
                button.clicked.connect(lambda _, r=row, c=col: self.cell_clicked(r, c))
                self.grid_layout.addWidget(button, row, col)
                self.buttons[(row, col)] = button

        self._create_menu()

    def _create_menu(self):
        menu = self.menuBar().addMenu("Game")

        two_player_action = QAction("Two Player", self)
        two_player_action.triggered.connect(self.start_two_player)
        ai_action = QAction("Play with AI", self)
        ai_action.triggered.connect(self.choose_difficulty)
        reset_action = QAction("Reset Board", self)
        reset_action.triggered.connect(self.reset_board)

        menu.addAction(two_player_action)
        menu.addAction(ai_action)
        menu.addSeparator()
        menu.addAction(reset_action)

    def cell_clicked(self, row, col):
        if self.game.has_winner() or self.game.is_tied():
            return
        move = self.game._current_moves[row][col]
        if not self.game.is_valid_move(move):
            return

        play_move = Move(row, col, self.game.current_player.label)
        self.game.process_move(play_move)
        self._update_board()

        if self.game.has_winner():
            winner = self.game.current_player.label
            self.scores[winner] += 1
            self.status_label.setText(f"{winner} wins!")
            QMessageBox.information(self, "Game Over", f"{winner} wins!")
        elif self.game.is_tied():
            self.status_label.setText("It's a tie!")
            QMessageBox.information(self, "Game Over", "It's a tie!")
        else:
            self.game.toggle_player()
            self.status_label.setText(f"{self.game.current_player.label}'s Turn")
            if self.game.play_with_ai and self.game.current_player.label == "O":
                self.ai_move()

    def ai_move(self):
        ai_move = self.game.get_ai_move_with_difficulty()
        if not ai_move:
            return
        self.game.process_move(ai_move)
        self._update_board()
        if self.game.has_winner():
            winner = self.game.current_player.label
            self.scores[winner] += 1
            self.status_label.setText(f"{winner} wins!")
            QMessageBox.information(self, "Game Over", f"{winner} wins!")
        elif self.game.is_tied():
            self.status_label.setText("It's a tie!")
            QMessageBox.information(self, "Game Over", "It's a tie!")
        else:
            self.game.toggle_player()
            self.status_label.setText(f"{self.game.current_player.label}'s Turn")

    def _update_board(self):
        for row in range(self.game.board_size):
            for col in range(self.game.board_size):
                move = self.game._current_moves[row][col]
                self.buttons[(row, col)].setText(move.label)
        self.score_label.setText(self._score_text())

    def _score_text(self):
        return f"Score - X: {self.scores['X']}  O: {self.scores['O']}"

    def reset_board(self):
        self.game.reset_game()
        for button in self.buttons.values():
            button.setText("")
        self.status_label.setText(f"{self.game.current_player.label}'s Turn")
        self.score_label.setText(self._score_text())

    def start_two_player(self):
        self.game = TicTacToeGame(play_with_ai=False, difficulty=self.game.difficulty)
        self.reset_board()

    def choose_difficulty(self):
        difficulty, ok = QInputDialog.getItem(
            self,
            "Choose Difficulty",
            "Select difficulty:",
            ["easy", "medium", "hard"],
            1,
            False,
        )
        if ok:
            self.game = TicTacToeGame(play_with_ai=True, difficulty=difficulty)
            self.reset_board()


def main():
    app = QApplication([])
    window = TicTacToeWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
