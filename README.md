# Shadow Stalker

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.5%2B-green?style=flat-square&logo=pygame)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

**A 2D Platformer with AI-Powered Chase Mechanics**

![Game Banner](https://via.placeholder.com/800x200/1a1a2e/ffffff?text=Shadow+Stalker+-+2D+Platformer)

[Features](#-features) • [Installation](#-installation) • [Controls](#-controls) • [Screenshots](#-screenshots) • [Contributing](#-contributing)

</div>

---

## 🎮 About

**Shadow Stalker** is a fast-paced 2D platformer built with Pygame where you must outrun an AI bot that relentlessly pursues you across multiple themed maps. The bot uses advanced pathfinding and can perform the same movement abilities as the player — wall sliding, wall jumping, and double jumping.

### The Chase

- **The Stalker** — An AI-controlled enemy that learns your patterns and adapts
- **Multiple Maps** — Industrial Zone, Green Zone, and Exclusion Zone with unique challenges
- **Smooth Physics** — Wall slides, wall jumps, double jumps, and responsive controls
- **Parallax Backgrounds** — Immersive layered backgrounds that scroll with the camera

---

## ✨ Features

### Player Mechanics
- **Movement** — Smooth left/right movement with acceleration
- **Jumping** — Single jump and double jump for reaching high platforms
- **Wall Sliding** — Slow your descent by sliding down walls
- **Wall Jumping** — Launch off walls to reach tricky areas
- **Coin Collection** — Collect coins across all maps for score

### AI Bot (MaskDudeBot)
- **Chasing AI** — Tracks player position and pursues relentlessly
- **Pathfinding** — Navigates gaps, walls, and platforms intelligently
- **Same Abilities** — Can wall slide, wall jump, and double jump just like you
- **Respawn Logic** — Always returns when it falls, keeping the chase alive
- **Multi-Map Persistence** — Follows you across map transitions

### Map System
- **Industrial Zone** — Dark, gritty industrial setting with conveyor belts and hazards
- **Green Zone** — Nature-themed with trees, fountains, and floating platforms
- **Exclusion Zone** — Restricted area with warning signs and dangerous terrain
- **Smooth Transitions** — Seamless movement between connected maps

### Map Editor
- **Visual Level Designer** — Drag-and-drop tile placement
- **Decoration System** — Place trees, rocks, and environmental objects
- **Export to JSON** — Save and load custom maps
- **Real-time Preview** — See your changes instantly

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Pygame 2.5 or higher

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Shadow_stalker.git
cd Shadow_stalker
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install pygame
```

3. **Run the game**
```bash
python merged_game.py
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

### Map Editor Controls

| Action | Keys |
|--------|------|
| **Place Tile/Object** | Left Click |
| **Remove Tile/Object** | Right Click |
| **Pan Camera** | Middle Mouse Drag |
| **Scroll Tiles** | Mouse Wheel |
| **Zoom In/Out** | `+` / `-` |
| **Toggle Mode** | `T` (Tile/Decoration) |
| **Toggle Grid** | `G` |
| **Save Map** | `S` |
| **Load Map** | `L` |
| **Reset View** | `R` |
| **Quick Select** | `1-9` (common tiles) |
| **Quit** | `Escape` |

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
│   ├── mask_dude_bot.py      # AI bot with chase logic
│   └── SELF_LEARNING_BOT.md  # Guide for RL-based AI
├── assets/
│   ├── MainCharacters/       # Player and bot sprites
│   ├── Environment/          # Tiles and backgrounds
│   └── Items/                # Coins and collectibles
├── core/
│   └── game.py               # Core game loop and level loading
├── editor/
│   └── map_editor.py         # Visual map editor
├── maps/
│   ├── industrial_zone_map.py
│   ├── green_zone_map.py
│   └── exclusion_zone_map.py
├── utils/                    # Utility functions
├── docs/                     # Documentation
├── merged_game.py            # Main game entry point
├── requirements.txt          # Python dependencies
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
```

### Using the Map Editor

```bash
python editor/map_editor.py
```

---

## 📝 Roadmap

- [ ] Add more themed maps (Underground, Sky Temple)
- [ ] Implement power-ups (speed boost, shield)
- [ ] Add boss encounters
- [ ] Implement self-learning AI bot (RL)
- [ ] Add multiplayer mode
- [ ] Level progression system
- [ ] Sound effects and music
- [ ] Leaderboards

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
