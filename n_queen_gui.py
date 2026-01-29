import sys
import random
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QSpinBox, QLabel, QMessageBox)
from PySide6.QtCore import Qt, QTimer, QPoint, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QFont, QDrag, QPixmap, QPainterPath


class ChessBoard(QWidget):
    """Chessboard widget with drag-and-drop queens"""
    
    queenPlaced = Signal(int, int)  # row, col
    queenRemoved = Signal(int, int)
    boardChanged = Signal()
    
    def __init__(self, n=8):
        super().__init__()
        self.n = n
        self.queens = []  # List of (row, col) tuples
        self.dragging_queen = None
        self.drag_start_pos = None
        self.drag_current_pos = None
        self.attacking_pairs = []  # List of pairs of attacking queens
        self.setMinimumSize(500, 500)
        self.setMouseTracking(True)
        
    def setN(self, n):
        """Update board size"""
        self.n = n
        self.queens = []
        self.attacking_pairs = []
        self.update()
        
    def placeQueen(self, row, col):
        """Place a queen at the given position"""
        if (row, col) not in self.queens:
            self.queens.append((row, col))
            self.detectAttacks()
            self.update()
            self.boardChanged.emit()
            
    def removeQueen(self, row, col):
        """Remove queen from position"""
        if (row, col) in self.queens:
            self.queens.remove((row, col))
            self.detectAttacks()
            self.update()
            self.boardChanged.emit()
            
    def clearQueens(self):
        """Clear all queens"""
        self.queens = []
        self.attacking_pairs = []
        self.update()
        self.boardChanged.emit()
        
    def randomPlaceQueens(self, count=None):
        """Randomly place queens on the board"""
        self.clearQueens()
        if count is None:
            count = self.n
        positions = [(r, c) for r in range(self.n) for c in range(self.n)]
        random.shuffle(positions)
        for i in range(min(count, len(positions))):
            self.placeQueen(positions[i][0], positions[i][1])
            
    def detectAttacks(self):
        """Detect all pairs of attacking queens"""
        self.attacking_pairs = []
        queens_list = list(self.queens)
        
        for i in range(len(queens_list)):
            for j in range(i + 1, len(queens_list)):
                q1 = queens_list[i]
                q2 = queens_list[j]
                
                # Check if queens attack each other
                if self.areAttacking(q1, q2):
                    self.attacking_pairs.append((q1, q2))
                    
    def areAttacking(self, q1, q2):
        """Check if two queens attack each other"""
        r1, c1 = q1
        r2, c2 = q2
        
        # Same row
        if r1 == r2:
            return True
        # Same column
        if c1 == c2:
            return True
        # Same diagonal
        if abs(r1 - r2) == abs(c1 - c2):
            return True
            
        return False
        
    def getSquareAt(self, pos):
        """Get board square coordinates from mouse position"""
        size = min(self.width(), self.height())
        square_size = size / self.n
        margin_x = (self.width() - size) / 2
        margin_y = (self.height() - size) / 2
        
        col = int((pos.x() - margin_x) / square_size)
        row = int((pos.y() - margin_y) / square_size)
        
        if 0 <= row < self.n and 0 <= col < self.n:
            return row, col
        return None
        
    def mousePressEvent(self, event):
        """Handle mouse press for dragging queens"""
        if event.button() == Qt.LeftButton:
            square = self.getSquareAt(event.position().toPoint())
            if square:
                row, col = square
                if (row, col) in self.queens:
                    self.dragging_queen = (row, col)
                    self.drag_start_pos = event.position().toPoint()
                    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if self.dragging_queen and event.buttons() & Qt.LeftButton:
            self.drag_current_pos = event.position().toPoint()
            self.update()  # Redraw with drag preview
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release to drop queen"""
        if self.dragging_queen and event.button() == Qt.LeftButton:
            square = self.getSquareAt(event.position().toPoint())
            if square:
                new_row, new_col = square
                old_row, old_col = self.dragging_queen
                
                # Remove from old position and place at new position
                if (new_row, new_col) != (old_row, old_col):
                    self.removeQueen(old_row, old_col)
                    self.placeQueen(new_row, new_col)
            else:
                # Dropped outside board, remove queen
                self.removeQueen(*self.dragging_queen)
                
            self.dragging_queen = None
            self.drag_start_pos = None
            self.drag_current_pos = None
            self.update()
            
    def paintEvent(self, event):
        """Draw the chessboard and queens"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        size = min(self.width(), self.height())
        square_size = size / self.n
        margin_x = (self.width() - size) / 2
        margin_y = (self.height() - size) / 2
        
        # Wooden color (light brown/tan)
        wooden_color = QColor(210, 180, 140)  # Tan color
        white_color = QColor(255, 255, 255)
        
        # Draw board squares
        for row in range(self.n):
            for col in range(self.n):
                x = margin_x + col * square_size
                y = margin_y + row * square_size
                
                # Alternate colors
                if (row + col) % 2 == 0:
                    painter.fillRect(int(x), int(y), int(square_size), int(square_size), white_color)
                else:
                    painter.fillRect(int(x), int(y), int(square_size), int(square_size), wooden_color)
        
        # Highlight attacking pairs with different colors
        attack_colors = [
            QColor(255, 100, 100, 180),  # Light red
            QColor(100, 150, 255, 180),  # Light blue
            QColor(255, 200, 100, 180),  # Light orange
            QColor(150, 255, 150, 180),  # Light green
            QColor(255, 150, 255, 180),  # Light magenta
            QColor(150, 255, 255, 180),  # Light cyan
        ]
        
        # Draw attack highlights
        for idx, (q1, q2) in enumerate(self.attacking_pairs):
            color = attack_colors[idx % len(attack_colors)]
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            
            # Highlight both squares
            for q in [q1, q2]:
                row, col = q
                x = margin_x + col * square_size
                y = margin_y + row * square_size
                painter.drawRect(int(x), int(y), int(square_size), int(square_size))
        
        # Draw queens
        font = QFont("Arial", int(square_size * 0.6))
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))  # Black outline
        
        for row, col in self.queens:
            # Draw queen at original position (even if dragging, show faded)
            x = margin_x + col * square_size + square_size / 2
            y = margin_y + row * square_size + square_size / 2
            
            # If this queen is being dragged, draw it faded
            if self.dragging_queen == (row, col):
                painter.setPen(QColor(0, 0, 0, 100))
                painter.setBrush(QColor(255, 255, 255, 100))
            else:
                painter.setPen(QColor(0, 0, 0))
                painter.setBrush(QColor(255, 255, 255))
                
            painter.drawText(int(x - square_size/2), int(y - square_size/2), 
                           int(square_size), int(square_size), 
                           Qt.AlignCenter, "♛")
        
        # Draw dragging queen at mouse position
        if self.dragging_queen and self.drag_start_pos:
            x = self.drag_start_pos.x()
            y = self.drag_start_pos.y()
            painter.setPen(QColor(0, 0, 0))
            painter.setBrush(QColor(255, 255, 255))
            painter.drawText(int(x - square_size/2), int(y - square_size/2), 
                           int(square_size), int(square_size), 
                           Qt.AlignCenter, "♛")


class NQueenSolver:
    """N-Queen solver with step-by-step animation support"""
    
    def __init__(self, n, board_widget, speed=6):
        self.n = n
        self.board = board_widget
        self.speed = speed  # 1-10, where 10 is instant
        self.solution_steps = []
        self.current_step = 0
        self.solving = False
        
    def solve(self, callback=None):
        """Solve N-Queen problem with backtracking"""
        self.solution_steps = []
        self.current_step = 0
        self.solving = True
        
        def backtrack(row, queens):
            if row == self.n:
                # Found a solution
                self.solution_steps.append(list(queens))
                return True
                
            for col in range(self.n):
                # Check if placing queen at (row, col) is valid
                valid = True
                for r, c in queens:
                    if c == col or abs(r - row) == abs(c - col):
                        valid = False
                        break
                        
                if valid:
                    queens.append((row, col))
                    self.solution_steps.append(list(queens))
                    
                    if backtrack(row + 1, queens):
                        return True
                        
                    queens.pop()
                    self.solution_steps.append(list(queens))
                    
            return False
            
        backtrack(0, [])
        self.animateSolution(callback)
        
    def animateSolution(self, callback=None):
        """Animate the solution steps"""
        if not self.solution_steps:
            if callback:
                callback(False)
            return
            
        delay_ms = int((10 - self.speed) * 100)  # Speed 6 = 400ms delay
        
        def showStep(step_idx):
            if step_idx < len(self.solution_steps):
                self.board.clearQueens()
                for queen in self.solution_steps[step_idx]:
                    self.board.placeQueen(queen[0], queen[1])
                    
                if step_idx < len(self.solution_steps) - 1:
                    QTimer.singleShot(delay_ms, lambda: showStep(step_idx + 1))
                else:
                    self.solving = False
                    if callback:
                        callback(True)
            else:
                self.solving = False
                if callback:
                    callback(True)
                    
        showStep(0)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("N-Queen Problem Solver")
        self.setGeometry(100, 100, 800, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Control panel
        control_layout = QHBoxLayout()
        
        # N selector
        n_label = QLabel("N:")
        self.n_spinbox = QSpinBox()
        self.n_spinbox.setMinimum(6)
        self.n_spinbox.setMaximum(15)
        self.n_spinbox.setValue(8)
        self.n_spinbox.valueChanged.connect(self.onNChanged)
        
        # Buttons
        self.solve_btn = QPushButton("Solve")
        self.solve_btn.clicked.connect(self.onSolve)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.onReset)
        
        control_layout.addWidget(n_label)
        control_layout.addWidget(self.n_spinbox)
        control_layout.addStretch()
        control_layout.addWidget(self.reset_btn)
        control_layout.addWidget(self.solve_btn)
        
        # Chessboard
        self.board = ChessBoard(n=8)
        self.solver = None
        
        # Add to main layout
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.board)
        
        # Status label
        self.status_label = QLabel("Manual Mode - Drag queens to place them")
        main_layout.addWidget(self.status_label)
        
    def onNChanged(self, n):
        """Handle N value change"""
        self.board.setN(n)
        self.status_label.setText(f"Board size changed to {n}x{n}")
        
    def onSolve(self):
        """Handle solve button click"""
        if self.solver and self.solver.solving:
            return
            
        self.status_label.setText("Solving...")
        self.solve_btn.setEnabled(False)
        
        self.solver = NQueenSolver(self.board.n, self.board, speed=6)
        self.solver.solve(callback=self.onSolveComplete)
        
    def onSolveComplete(self, success):
        """Handle solve completion"""
        self.solve_btn.setEnabled(True)
        if success:
            self.status_label.setText("Solution found!")
        else:
            self.status_label.setText("No solution found")
            
    def onReset(self):
        """Handle reset button click"""
        self.board.randomPlaceQueens()
        self.status_label.setText("Queens randomly placed - Manual Mode")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
