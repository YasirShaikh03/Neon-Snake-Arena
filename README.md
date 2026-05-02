# 🐍 Snake Game

A classic Snake game with a polished UI built using **Pygame**.

## Features
- ✅ 10 speed/difficulty levels (1 = Baby Snake → 10 = LEVIATHAN)
- ✅ Interactive difficulty slider in menu
- ✅ Golden food (rare) — worth +30 pts and grows snake x3
- ✅ Combo system — eat fast for score multipliers
- ✅ Obstacles / walls mode toggle
- ✅ Score popups, particles and glow effects
- ✅ High score tracking
- ✅ Pause, Retry, Menu screens

## Install

```bash
pip install pygame
```

## Run

```bash
python snake_game.py
```

## Controls

| Key          | Action          |
|--------------|-----------------|
| Arrow Keys / WASD | Move snake |
| P / ESC      | Pause           |
| R            | Retry (game over screen) |

## Scoring

| Action        | Points               |
|---------------|----------------------|
| Normal food   | +10 pts × combo      |
| Golden food 🌟 | +30 pts × combo     |
| Level bonus   | +level×2 per food   |
| x2 Combo      | Eat 2 foods quickly |
| x5 Max Combo  | Maximum multiplier  |

## Levels

| Level | Name         | Feel              |
|-------|--------------|-------------------|
| 1     | Baby Snake   | Super slow        |
| 5     | Viper        | Medium pace       |
| 10    | LEVIATHAN    | Extremely fast    |
