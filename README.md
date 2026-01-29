# N-Queen Problem Solver GUI

A PySide6-based graphical application for solving and visualizing the classic N-Queen problem with interactive drag-and-drop functionality.

## Features

- **Interactive Chessboard**: Visual board with white and wooden-colored squares
- **Drag & Drop**: Manually place and move queens by dragging them
- **Auto-Detection**: Automatically highlights attacking queen pairs with color-coded indicators
- **Animated Solver**: Step-by-step backtracking algorithm visualization (speed: 6/10)
- **Customizable Board Size**: Adjust N from 6 to 15 (default: 8)
- **Random Placement**: Reset button randomly places queens for experimentation

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python n_queen_gui.py
```

### Manual Mode
- Click and drag queens to move them around the board
- Attacking queens are automatically highlighted with different colors for each pair
- Place queens manually to explore solutions

### Solve Mode
- Click the **Solve** button to automatically find a solution
- Watch the animated backtracking algorithm place queens step by step
- The solver uses a recursive backtracking approach

## Implementation Details

### Architecture
The application is built using **PySide6** (Qt for Python) and consists of three main components:

1. **ChessBoard Widget**: Custom QWidget that handles:
   - Board rendering with alternating white/wooden squares
   - Queen placement and drag-and-drop mechanics
   - Real-time attack detection using row, column, and diagonal checks
   - Color-coded highlighting for attacking pairs

2. **NQueenSolver Class**: Implements the backtracking algorithm:
   - Recursive depth-first search
   - Generates solution steps for animation
   - Configurable animation speed (currently set to 6/10)

3. **MainWindow**: Application window managing:
   - UI controls (N selector, Solve/Reset buttons)
   - Board-solver coordination
   - Status updates

### Key Algorithms
- **Attack Detection**: O(n²) pairwise comparison checking same row, column, or diagonal
- **Backtracking Solver**: Classic recursive approach that places queens row by row, backtracking when conflicts occur

### Visual Design
- Light color scheme with white (#FFFFFF) and wooden tan (#D2B48C) squares
- White queens (♛) with black outlines for visibility
- Semi-transparent attack highlights using multiple colors to distinguish different attacking pairs

## Future Improvements

The solver algorithm will be enhanced in future versions with:
- Additional solving algorithms (genetic algorithms, constraint satisfaction, etc.)
- Performance optimizations for larger board sizes
- Solution counting and enumeration features
- Export/import functionality for board states

## Requirements

- Python 3.7+
- PySide6 >= 6.5.0