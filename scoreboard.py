import sqlite3

def init_db():
    """Create players table if not exists."""
    conn = sqlite3.connect('game.sqlite')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            name TEXT PRIMARY KEY,
            wins INTEGER,
            losses INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def update_score(player_name, result):
    """Add win or loss to a player's record."""
    conn = sqlite3.connect('game.sqlite')
    c = conn.cursor()
    c.execute('SELECT * FROM players WHERE name = ?', (player_name,))
    row = c.fetchone()
    if row:
        wins, losses = row[1], row[2]
        if result == 'win':
            wins += 1
        else:
            losses += 1
        c.execute('UPDATE players SET wins = ?, losses = ? WHERE name = ?', (wins, losses, player_name))
    else:
        wins = 1 if result == 'win' else 0
        losses = 1 if result == 'loss' else 0
        c.execute('INSERT INTO players (name, wins, losses) VALUES (?, ?, ?)', (player_name, wins, losses))
    conn.commit()
    conn.close()


def get_stats(player_name):
    """Retrieve a player's win-loss record."""
    conn = sqlite3.connect('game.sqlite')
    c = conn.cursor()
    c.execute('SELECT wins, losses FROM players WHERE name = ?', (player_name,))
    row = c.fetchone()
    conn.close()
    return row if row else (0, 0)


def show_scoreboard():
    """Retrieve the whole scoreboard."""
    conn = sqlite3.connect('game.sqlite')
    c = conn.cursor()
    c.execute('SELECT * FROM players')
    rows = c.fetchall()
    conn.close()
    return rows
