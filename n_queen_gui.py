import sys
import random
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QSpinBox, QLabel, QSlider)
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
        self.guides_enabled = False
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
                    
    def setGuidesEnabled(self, enabled):
        """Toggle guide highlights (possible-move shading)"""
        self.guides_enabled = bool(enabled)
        self.update()
        
    def getThreatenedSquares(self, queen):
        """Get all squares a queen can attack (row, col, diagonals)"""
        r, c = queen
        squares = set()
        for i in range(self.n):
            squares.add((i, c))  # Same column
        for j in range(self.n):
            squares.add((r, j))  # Same row
        for k in range(1, self.n):
            for dr, dc in [(k, k), (k, -k), (-k, k), (-k, -k)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.n and 0 <= nc < self.n:
                    squares.add((nr, nc))
        squares.discard((r, c))  # Exclude queen's own square
        return squares
        
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
                    self.drag_current_pos = event.position().toPoint()
                    
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
        
        # Guides mode: shade possible-move squares for each queen (different color per queen)
        # Clash mode: highlight attacking pairs (mutually exclusive with guides)
        if self.guides_enabled:
            guide_colors = [
                QColor(255, 180, 180, 150),  # Light coral
                QColor(180, 220, 180, 150),  # Light mint
                QColor(220, 210, 150, 150),  # Light gold
                QColor(200, 180, 220, 150),  # Light lavender
                QColor(180, 210, 255, 150),  # Light sky blue
                QColor(255, 220, 180, 150),  # Light peach
                QColor(200, 255, 220, 150),  # Light seafoam
                QColor(255, 200, 255, 150),  # Light pink
                QColor(180, 255, 255, 150),  # Light cyan
                QColor(255, 255, 180, 150),  # Light yellow
            ]
            # Track which square is shaded by which queen (last queen wins for overlaps)
            square_color = {}
            for idx, queen in enumerate(self.queens):
                color = guide_colors[idx % len(guide_colors)]
                for sq in self.getThreatenedSquares(queen):
                    square_color[sq] = color
            for (row, col), color in square_color.items():
                x = margin_x + col * square_size
                y = margin_y + row * square_size
                painter.fillRect(int(x), int(y), int(square_size), int(square_size), color)
        else:
            # Single clash color - avoids brown when 3+ queens overlap
            clash_color = QColor(255, 120, 120, 160)  # Light coral red
            clash_squares = set()
            for q1, q2 in self.attacking_pairs:
                clash_squares.add(q1)
                clash_squares.add(q2)
            for row, col in clash_squares:
                x = margin_x + col * square_size
                y = margin_y + row * square_size
                painter.fillRect(int(x), int(y), int(square_size), int(square_size), clash_color)
        
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
        if self.dragging_queen and self.drag_current_pos:
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
        
        self.make_puzzle_btn = QPushButton("Make Puzzle")
        self.make_puzzle_btn.clicked.connect(self.onMakePuzzle)
        
        # Guides slider (0=off, 1=on)
        guides_label = QLabel("Guides:")
        self.guides_slider = QSlider(Qt.Horizontal)
        self.guides_slider.setMinimum(0)
        self.guides_slider.setMaximum(1)
        self.guides_slider.setValue(0)
        self.guides_slider.setFixedWidth(60)
        self.guides_slider.setTickPosition(QSlider.TicksBelow)
        self.guides_slider.setTickInterval(1)
        self.guides_slider.valueChanged.connect(self.onGuidesChanged)
        
        control_layout.addWidget(n_label)
        control_layout.addWidget(self.n_spinbox)
        control_layout.addWidget(guides_label)
        control_layout.addWidget(self.guides_slider)
        control_layout.addStretch()
        control_layout.addWidget(self.make_puzzle_btn)
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
            
    def onMakePuzzle(self):
        """Handle Make Puzzle button - randomly place queens"""
        self.board.randomPlaceQueens()
        self.status_label.setText("Puzzle created - Drag queens to solve")
        
    def onGuidesChanged(self, value):
        """Handle guides slider - 0=off, 1=on"""
        self.board.setGuidesEnabled(value == 1)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
