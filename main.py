import pygame, sys, random
from maze_manager import MazeManager
from player import Player, activate_power_up, activate_trap
import scoreboard
scoreboard.init_db()


# Define colors
BLACK = (0, 0, 0)  # Maze background
WHITE = (255, 255, 255)  # Maze path
ORANGE = (255, 165, 0)  # Exit color
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)

# Maze dimensions
CELL_SIZE = 20
ROWS = 21
COLS = 21

HEADER_SIZE = 50
FOOTER_SIZE = 100

def draw_players(screen, players, current):
    """Draw all players normally first, then draw the current one bigger on top."""
    for p in players:
        if p != current:
            pygame.draw.circle(
                screen, p.color,
                (p.x * CELL_SIZE + CELL_SIZE // 2, p.y * CELL_SIZE + CELL_SIZE // 2 + HEADER_SIZE),
                CELL_SIZE // 2
            )
    # Highlight current by drawing it last with a bigger circle
    pygame.draw.circle(
        screen, current.color,
        (current.x * CELL_SIZE + CELL_SIZE // 2, current.y * CELL_SIZE + CELL_SIZE // 2 + HEADER_SIZE),
        CELL_SIZE // 2 + 5
    )

def show_scoreboard(screen, font, positions, scoreboard):
    """Display final positions on GUI instead of terminal prints."""
    positions_sorted = sorted(positions, key=lambda x: x[1])
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)
        title_surf = font.render("Final Scoreboard", True, WHITE)
        title_rect = title_surf.get_rect(center=(COLS * CELL_SIZE // 2, HEADER_SIZE // 2))
        screen.blit(title_surf, title_rect)

        y_offset = HEADER_SIZE + 40
        for i ,(p, pos) in positions_sorted:
            color = GOLD if pos == 1 else p.color
            label = "Winner" if i == 0 else ("Loser" if i == len(positions_sorted)-1 else f"Position {pos}")
            text = f"#{pos} - Player {p.id} | power-up: {p.power_up_count} | trap: {p.trap_count}"
            surf = font.render(text, True, color)
            rect = surf.get_rect(topleft=(50, y_offset))
            screen.blit(surf, rect)
            y_offset += 40
    
        pygame.display.flip()
        pygame.time.Clock().tick(30)

    pygame.quit()

def main():
    """Main game loop with turn-by-turn movement."""
    num = int(input("How many players (2-4)? "))
    num = max(2, min(4, num))  # clamp 2-4
    
    pygame.init()
    HEIGHT = HEADER_SIZE + ROWS * CELL_SIZE + FOOTER_SIZE
    WIDTH = COLS * CELL_SIZE
    screen = pygame.display.set_mode((COLS * CELL_SIZE, HEIGHT))
    pygame.display.set_caption("Turn Based Maze")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)  

    # Maze and Players
    maze = MazeManager(ROWS, COLS).maze
    
    start = (1, 1)  # All start here
    exit = (COLS-2, ROWS-2)  # Maze exit
    
    PLAYER_COLORS = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0)]

    players = [Player(i + 1, PLAYER_COLORS[i], start) for i in range(num)]

    # Loading images
    power_up_img = pygame.image.load("powerup.png")
    trap_img = pygame.image.load("trap.png")
    power_up_img = pygame.transform.scale(power_up_img, (CELL_SIZE, CELL_SIZE))
    trap_img = pygame.transform.scale(trap_img, (CELL_SIZE, CELL_SIZE))

    # Random power-up and trap positions
    power_ups = []
    traps = []

    for _ in range(10):
        x, y = random.randint(1, COLS-2), random.randint(1, ROWS-2)
        if maze[y][x] == 0 and (x, y) not in power_ups and (x, y) not in traps:
            power_ups.append((x, y))
    for _ in range(10):
        x, y = random.randint(1, COLS-2), random.randint(1, ROWS-2)
        if maze[y][x] == 0 and (x, y) not in power_ups and (x, y) not in traps:
            traps.append((x, y))

    # Turn control
    turn = 0
    positions = []
    start_time = pygame.time.get_ticks()
    time_slice = 10000  # 10 seconds in milliseconds

    running = True
    while running:
        clock.tick(10)
        current_time = pygame.time.get_ticks()
        if current_time - start_time > time_slice:
             # Time's up for this player
            turn = (turn + 1) % len(players)
            start_time = pygame.time.get_ticks()
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT] if event.type == pygame.KEYDOWN else 0:
                
                p = players[turn]
                
                dx, dy = 0, 0
                
                if event.key == pygame.K_UP:
                    dy = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1
                elif event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1

                if p.move(dx, dy, maze):
                    if (p.x, p.y) in power_ups:
                        activate_power_up({"id": p.id})
                        p.power_up_count += 1
                        power_ups.remove((p.x, p.y))
                        continue

                    elif (p.x, p.y) in traps:
                        activate_trap({"id": p.id})
                        p.trap_count += 1
                        traps.remove((p.x, p.y))
                        for i in range(4):
                          if maze[p.y - dy][p.x - dx] == 0:
                                   p.x -= dx
                                   p.y -= dy
                          else:
                                    break
                        

                        turn = (turn + 1) % len(players)
                       
                    elif (p.x, p.y) == exit:
                        winner_name = f"Player {p.id}" 
                        scoreboard.update_score(winner_name, 'win')
                        print(f"{winner_name} finished.")
                        positions.append((p, len(positions)+1))
                        players.remove(p)

                        if len(players) == 1:
                            loser = players[0]
                            positions.append((loser, len(positions)+1))
                            scoreboard.update_score(f"Player {loser.id}", 'loss')
                            players.remove(loser)
                            running = False
                        else:
                            if turn >= len(players):
                                turn = 0

                    else:
                        turn = (turn + 1) % len(players)
                        start_time = pygame.time.get_ticks()

        if not players:
            running = False
            break

        # Drawing
        screen.fill(BLACK)
        header = pygame.Rect(0, 0, COLS * CELL_SIZE, HEADER_SIZE)
        pygame.draw.rect(screen, BLACK, header)

        p = players[turn]
        header_surf = font.render(f"Player {p.id}'s Turn", True, WHITE)
        header_rect = header_surf.get_rect(center=(COLS * CELL_SIZE // 2, HEADER_SIZE // 2))
        screen.blit(header_surf, header_rect) 
 
        for y in range(ROWS):
            for x in range(COLS):
                color = WHITE if maze[y][x] == 0 else BLACK
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE + HEADER_SIZE, CELL_SIZE, CELL_SIZE))
         
        for (x, y) in power_ups:
            screen.blit(power_up_img, (x * CELL_SIZE, y * CELL_SIZE + HEADER_SIZE))
        
        for (x, y) in traps:
            screen.blit(trap_img, (x * CELL_SIZE, y * CELL_SIZE + HEADER_SIZE))

        draw_players(screen, players, p)

        pygame.draw.rect(screen, ORANGE, (exit[0] * CELL_SIZE, exit[1] * CELL_SIZE + HEADER_SIZE, CELL_SIZE, CELL_SIZE))

        for x in range(COLS):
            pygame.draw.line(screen, (50, 50, 50), 
                             (x * CELL_SIZE, HEADER_SIZE), 
                             (x * CELL_SIZE, HEADER_SIZE + ROWS * CELL_SIZE))
        for y in range(ROWS):
            pygame.draw.line(screen, (50, 50, 50), 
                             (0, HEADER_SIZE + y * CELL_SIZE), 
                             (COLS * CELL_SIZE, HEADER_SIZE + y * CELL_SIZE))
        
        footer = pygame.Rect(0, HEADER_SIZE + ROWS * CELL_SIZE, COLS * CELL_SIZE, FOOTER_SIZE)
        pygame.draw.rect(screen, GREEN, footer)
        footer_surf = font.render("Tip: Use arrow keys to move!", True, WHITE)
        footer_rect = footer_surf.get_rect(center=(COLS * CELL_SIZE // 2, HEADER_SIZE + ROWS * CELL_SIZE + FOOTER_SIZE // 2))
        screen.blit(footer_surf, footer_rect)

        pygame.display.flip()

    show_scoreboard(screen, font, positions, scoreboard)
    pygame.quit()


if __name__ == "__main__":
    main()
