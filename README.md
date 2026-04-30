# Shadow Stalker

<div align="center">

![Python](https://img.shields.io/badge/Python-3.14%2B-blue?style=flat-square&logo=python)
![Pygame](https://img.shields.io/badge/Pygame-CE-2.5%2B-green?style=flat-square&logo=pygame)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

**A 2D Platformer with AI-Powered Chase Mechanics & Kids Mode**

![Game Banner](https://via.placeholder.com/800x200/1a1a2e/ffffff?text=Shadow+Stalker+-+2D+Platformer)

[Features](#-features) • [Installation](#-installation) • [Controls](#-controls) • [Screenshots](#-screenshots) • [Contributing](#-contributing)

</div>

---

## 🎮 About

**Shadow Stalker** is a fast-paced 2D platformer built with Pygame CE where you must outrun an AI bot that relentlessly pursues you across multiple themed maps. The bot uses advanced pathfinding and can perform the same movement abilities as the player — wall sliding, wall jumping, and double jumping.


## 👥 Contributors

- **Younes BASIR** 
- **[MOHAMED ZOUBAA](https://github.com/zoubaax)** 
- **WAJIH BEN EL ADEM** 
### The Chase

- **The Stalker** — An AI-controlled enemy that relentlessly pursues you across all maps
- **Multiple Maps** — Industrial Zone, Green Zone, Exclusion Zone, and Nature Adventure with unique challenges
- **Smooth Physics** — Wall slides, wall jumps, double jumps, and responsive controls
- **Parallax Backgrounds** — Immersive layered backgrounds that scroll with the camera
- **Kids Mode** — Educational puzzles and quizzes for younger players
- **Procedural Audio** — Synth sound effects and ambient music generated in real-time

---

## ✨ Features

### Player Mechanics
- **Movement** — Smooth left/right movement with acceleration
- **Jumping** — Single jump and double jump for reaching high platforms
- **Wall Sliding** — Slow your descent by sliding down walls
- **Wall Jumping** — Launch off walls to reach tricky areas
- **Coin Collection** — Collect coins across all maps for score
- **Health System** — Take damage from falling or hazards

### AI Bot (MaskDudeBot)
- **Chasing AI** — Tracks player position and pursues relentlessly
- **Pathfinding** — Navigates gaps, walls, and platforms intelligently
- **Same Abilities** — Can wall slide, wall jump, and double jump just like you
- **Multi-Map Persistence** — Follows you across map transitions
- **Game Over on Catch** — If the bot catches you, restart from the beginning

### Map System
- **Industrial Zone** — Dark, gritty industrial setting with conveyor belts and hazards
- **Green Zone** — Nature-themed with trees, fountains, and floating platforms
- **Exclusion Zone** — Restricted area with warning signs and dangerous terrain
- **Nature Adventure** — Outdoor adventure with waterfalls and natural obstacles
- **Smooth Transitions** — Fade-in/out effects between maps

### Game Modes
- **Normal Mode** — Classic platforming with the AI stalker
- **Kids Mode** — Educational experience with age-appropriate quizzes and puzzles
  - **Under 5** — Simple visual matching and basic counting
  - **5+** — Pattern recognition, shape puzzles, and logic games

### Menu System
- **Main Menu** — Pixel-art styled buttons with hover effects
- **User System** — Save progress and high scores per username
- **Leaderboard** — View top scores across all players
- **Victory Screen** — Celebration on completing all levels
- **Pause Menu** — Resume or quit during gameplay

### Audio System
- **Procedural Sound Effects** — Synth-generated UI clicks and interactions
- **Ambient Music** — Looped background music generated in real-time
- **No External Assets Required** — All audio created programmatically

### Database
- **SQLite Storage** — Persistent score tracking
- **High Scores** — Per-level and total score leaderboards
- **User Profiles** — Separate progress for each player

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher (tested on Python 3.14)
- Pygame CE 2.5 or higher
- NumPy (for procedural audio)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Shadow_stalker.git
cd Shadow_stalker
```

2. **Install dependencies**
```bash
pip install pygame-ce numpy
```

Or create a `requirements.txt` file:
```
pygame-ce>=2.5.0
numpy>=1.24.0
```

Then install:
```bash
pip install -r requirements.txt
```

3. **Run the game**
```bash
python core/game.py
```

---

## 🎯 Controls

| Action | Keys |
|--------|------|
| **Move Left** | `A` or `←` |
| **Move Right** | `D` or `→` |
| **Jump** | `Space`, `W`, or `↑` |
| **Double Jump** | Press Jump again while airborne |
| **Wall Slide** | Hold against a wall while falling |
| **Wall Jump** | Press Jump while sliding on a wall |
| **Restart** | `Space` (when game over) |
| **Quit** | `Escape` |

### Menu Controls

| Action | Keys |
|--------|------|
| **Navigate** | Arrow Keys / WASD |
| **Select** | Enter / Space / Click |
| **Back** | Escape / Back Button |

---

## 📸 Screenshots

### Gameplay
<div align="center">

![Gameplay Screenshot](https://via.placeholder.com/600x340/1a1a2e/ffffff?text=Gameplay+Screenshot)

*The Stalker in hot pursuit across the Industrial Zone*

</div>

### Map Editor
<div align="center">

![Map Editor](https://via.placeholder.com/600x340/1a1a2e/ffffff?text=Map+Editor+Interface)

*Visual level designer with tile palette and decoration tools*

</div>

---

## 📁 Project Structure

```
Shadow_stalker/
├── ai/
│   └── mask_dude_bot.py      # AI bot with chase logic
├── assets/
│   ├── MainCharacters/       # Player (VirtualGuy) and bot (MaskDude) sprites
│   ├── craftpix-net-314143-free-industrial-zone-tileset-pixel-art/
│   ├── craftpix-net-334660-free-green-zone-tileset-pixel-art/
│   ├── craftpix-net-311724-free-exclusion-zone-tileset-pixel-art/
│   └── craftpix-net-325828-free-nature-adventure-tileset-pixel-art/
├── core/
│   ├── game.py               # Core game loop and level loading
│   ├── menu.py               # Menu system with UI and leaderboard
│   ├── audio.py              # Procedural audio system
│   ├── quiz.py               # Quiz system for Kids Mode
│   └── database.py           # SQLite database for score tracking
├── editor/
│   └── map_editor.py         # Visual map editor
├── maps/
│   ├── industrial_zone_map.py
│   ├── green_zone_map.py
│   ├── exclusion_zone_map.py
│   └── nature_adventure_map.py
├── game_data.db              # SQLite database (auto-generated)
├── requirements.txt          # Python dependencies
├── LICENSE                   # MIT License
└── README.md                 # This file
```

---

## 🤖 AI Bot Details

The MaskDudeBot uses a combination of:
- **Line-of-sight detection** — Tracks player within detection range
- **Gap detection** — Jumps over gaps in the terrain
- **Wall detection** — Uses wall jumps when blocked
- **Double jump logic** — Uses second jump to reach higher platforms
- **Respawn system** — Reappears behind player when it falls

### Future: Self-Learning AI

See [`ai/SELF_LEARNING_BOT.md`](ai/SELF_LEARNING_BOT.md) for a guide on implementing reinforcement learning to make the bot teach itself how to chase using PPO (Proximal Policy Optimization).

---

## 🔧 Development

### Running Individual Maps

```bash
# Industrial Zone
python maps/industrial_zone_map.py

# Green Zone
python maps/green_zone_map.py

# Exclusion Zone
python maps/exclusion_zone_map.py

# Nature Adventure
python maps/nature_adventure_map.py
```

### Using the Map Editor

```bash
python editor/map_editor.py
```

---

## 📝 Roadmap

- [x] Kids Mode with educational quizzes and puzzles
- [x] SQLite database for persistent score tracking
- [x] Procedural audio system (no external audio files needed)
- [x] Menu system with leaderboard and user profiles
- [x] Pause menu during gameplay
- [x] Game over screen with dramatic effects
- [x] Smooth transition effects between maps
- [ ] Add more themed maps (Underground, Sky Temple)
- [ ] Implement power-ups (speed boost, shield)
- [ ] Add boss encounters
- [ ] Implement self-learning AI bot (RL)
- [ ] Add multiplayer mode
- [ ] More quiz content for Kids Mode
- [ ] Difficulty settings for the AI bot

---



## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Pygame** — The awesome Python game library
- **Craftpix** — For the exclusion zone tileset
- **OpenGameArt** — For additional assets

---

<div align="center">

**Made with ❤️ using Pygame**

[⬆ Back to Top](#shadow-stalker)

</div>
