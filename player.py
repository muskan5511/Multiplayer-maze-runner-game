import pygame, threading

# Semaphores for power-up and trap
power_up_semaphore = threading.Semaphore(1)
trap_semaphore = threading.Semaphore(1)

def activate_power_up(player):
    """Activate a power-up for a short while."""
    with power_up_semaphore:
        print(f"Player {player['id']} got a power-up.")
        threading.Event().wait(2)
        print(f"Player {player['id']} power-up finished.")
        
def activate_trap(player):
    """Activate a trap for a short while."""
    with trap_semaphore:
        print(f"Player {player['id']} fell into a trap.")
        threading.Event().wait(2)
        print(f"Player {player['id']} is free from trap now.")
    

class Player:
    """Represents a player in the game."""
    def __init__(self, id, color, start):
        self.id = id
        self.color = color
        self.x, self.y = start
        self.power_up_count = 0
        self.trap_count = 0

    def move(self, dx, dy, maze):
        """Move the player in the maze if path is clear."""
        new_x, new_y = self.x + dx, self.y + dy
        if maze[new_y][new_x] == 0:
            self.x = new_x
            self.y = new_y
            return True
        return False
