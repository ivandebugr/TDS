# Tower Defense Game

A 2D tower defense game built with Python and Pygame.

## Gameplay

Enemies follow a set path across the map. Place turrets to shoot them down before they reach the end. Survive as many waves as possible.

- Enemies move along a predefined path and fade out when killed
- Turrets automatically target and shoot nearby enemies
- Waves get progressively harder
- The game ends when enemies break through — your wave count is your score

## Turret Types

- **Default Turret** — standard range and fire rate
- **Advanced Turret** — upgraded stats
- **Golden Turret** — highest tier

## Controls

- Click to place turrets on the map
- Start/Quit buttons on the main menu
- Restart or exit from the Game Over screen

## Requirements

- Python 3.x
- Pygame

Install Pygame:
```bash
pip install pygame
```

## Running the Game

```bash
python main.py
```

## Project Structure

```
TDS/
├── main.py               # Entry point, main menu, game loop
└── Assets/
    ├── game.py           # Game logic, enemies, turrets, waves
    ├── button.py         # UI button component
    ├── Music/            # Background music
    ├── Sounds/           # Sound effects
    └── *.png             # Sprites and backgrounds
```
