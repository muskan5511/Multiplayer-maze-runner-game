import random

class MazeManager:
    """Maze generator using Prim's with thin walls and multiple paths."""
    def __init__(self, rows, cols):
        self.rows = rows if rows % 2 == 1 else rows + 1  # ensure odd
        self.cols = cols if cols % 2 == 1 else cols + 1
        self.maze = [[1 for _ in range(self.cols)] for _ in range(self.rows)]
        self.generate_maze()

    def generate_maze(self):
        """Generate maze with multiple paths using Prim's algorithm."""
        start_x, start_y = 1, 1
        self.maze[start_y][start_x] = 0
        walls = []

        for dy, dx in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            ny, nx = start_y + dy, start_x + dx
            if 0 < ny < self.rows-1 and 0 < nx < self.cols-1:
                walls.append(((start_y, start_x), (ny, nx)))

        while walls:
            (y1, x1), (y2, x2) = walls.pop(random.randint(0, len(walls)-1))

            if self.maze[y2][x2] == 1:
                self.maze[y2][x2] = 0
                self.maze[(y1 + y2) // 2][(x1 + x2) // 2] = 0

                for dy, dx in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                    ny, nx = y2 + dy, x2 + dx
                    if 0 < ny < self.rows-1 and 0 < nx < self.cols-1:
                        if self.maze[ny][nx] == 1:
                            walls.append(((y2, x2), (ny, nx)))
