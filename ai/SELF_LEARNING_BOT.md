# Self-Learning AI Bot — How to Make the Stalker Learn on Its Own

## Current State

The bot in `mask_dude_bot.py` uses **scripted AI**: hardcoded rules like "if gap ahead → jump", "if wall → wall jump", "if player visible → chase". This works but is rigid — the bot can't adapt to new map layouts or discover creative paths.

## Goal

Replace scripted rules with a bot that **learns by trial-and-error** how to move, jump, wall-slide, and chase the player across any map.

---

## Approach: Reinforcement Learning (RL)

RL is the natural fit — the bot is an **agent** in an **environment** (the map), taking **actions** and receiving **rewards**. Over time it learns which action sequences lead to high reward.

### The RL Loop

```
┌──────────┐   action    ┌────────────┐
│   Bot    │────────────▶│   Game     │
│ (agent)  │             │ (env)      │
│          │◀────────────│            │
└──────────┘  state+reward └────────────┘
```

---

## 1. Define the State (What the Bot "Sees")

Replace the current `can_see_player()` distance check with a **numeric observation vector** the neural network can consume:

| Observation | Example | Why |
|---|---|---|
| dx to player | -0.5..0.5 (normalized) | Chase direction |
| dy to player | -1.0..1.0 | Is player above/below |
| Distance to player | 0..1 | Urgency |
| On ground? | 0 or 1 | Can jump |
| Wall left/right? | 0, 0 | Can wall jump |
| Jump count | 0, 1, 2 | Can double jump |
| Gap ahead (L/R) | 0 or 1 | Don't fall |
| Wall ahead (L/R) | 0 or 1 | Need to jump over |
| Velocity x, y | -1..1 | Current momentum |

**Total: ~15 floats** — small enough for fast training, rich enough for smart behavior.

```python
def get_observation(self):
    """Return numeric state vector for the neural network."""
    dx = (self.target.rect.centerx - self.rect.centerx) / 600
    dy = (self.target.rect.centery - self.rect.centery) / 600
    dist = math.sqrt(dx*dx + dy*dy)
    return [
        dx, dy, dist,
        float(self.on_ground),
        float(self.on_wall_l), float(self.on_wall_r),
        float(self.jump_count) / 2,
        float(self.check_gap_ahead(1)), float(self.check_gap_ahead(-1)),
        float(self.check_wall_ahead(1)), float(self.check_wall_ahead(-1)),
        self.vx / BOT_SPEED, self.vy / 600
    ]
```

---

## 2. Define Actions (What the Bot "Does")

Replace the current `update_ai()` decision tree with **5 discrete actions**:

| Action | Effect |
|---|---|
| 0: Idle | `vx = 0` |
| 1: Move Left | `vx = -BOT_SPEED` |
| 2: Move Right | `vx = +BOT_SPEED` |
| 3: Jump | Call `self.jump()` |
| 4: Wall Jump | Call `self.jump()` (wall check is inside) |

The neural network outputs probabilities for each action. The bot picks one per frame.

---

## 3. Define the Reward (What the Bot "Wants")

This is the most critical design. The reward signal shapes all behavior:

```python
def compute_reward(self, prev_dist, caught_player, fell_off):
    reward = 0

    # ── Getting closer to player (primary chase signal) ──
    new_dist = self.distance_to_player()
    reward += (prev_dist - new_dist) * 2.0   # +reward for closing gap

    # ── Caught the player (big win) ──
    if caught_player:
        reward += 100.0

    # ── Fell off map (bad) ──
    if fell_off:
        reward -= 50.0

    # ── Small penalty for doing nothing ──
    if abs(self.vx) < 1 and not self.on_ground:
        reward -= 0.1   # discourage hovering

    return reward
```

**Key insight**: the bot learns to chase because closing distance = positive reward. It learns to jump gaps because falling = negative reward. No hardcoded rules needed.

---

## 4. The Learning Algorithm: PPO (Proximal Policy Optimization)

PPO is the standard choice for game AI — stable, sample-efficient, and well-supported.

### Architecture

```
Observation (15) → Dense(64, ReLU) → Dense(64, ReLU) → Action probs (5)
                                                             │
                                                         Value head (1)
```

A single small neural network (~5K parameters) that outputs:
- **Policy**: probability of each action
- **Value**: estimated future reward (for training stability)

### Libraries

| Library | Pros | Install |
|---|---|---|
| **Stable-Baselines3** | Easiest, well-documented | `pip install stable-baselines3` |
| **CleanRL** | Single-file implementations, educational | `pip install cleanrl` |
| **torch (raw)** | Full control, no magic | `pip install torch` |

---

## 5. Training Loop (How It Actually Learns)

```python
import gymnasium as gym
from stable_baselines3 import PPO

# 1. Wrap your game as a Gymnasium environment
class ShadowStalkerEnv(gym.Env):
    def __init__(self):
        self.action_space = gym.spaces.Discrete(5)   # 5 actions
        self.observation_space = gym.spaces.Box(
            low=-1, high=1, shape=(13,), dtype=float
        )
        # Create bot + map here

    def reset(self):
        # Reset bot and player to spawn positions
        return self.bot.get_observation(), {}

    def step(self, action):
        prev_dist = self.bot.distance_to_player()
        self.bot.apply_action(action)       # execute chosen action
        self.bot.update(dt, map_height)      # physics tick

        obs = self.bot.get_observation()
        caught = self.bot.rect.colliderect(self.player.rect)
        fell = self.bot.rect.y > map_height
        reward = self.compute_reward(prev_dist, caught, fell)

        done = caught or fell
        return obs, reward, done, False, {}

# 2. Train
env = ShadowStalkerEnv()
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=500_000)   # ~10 min on CPU

# 3. Save & use
model.save("stalker_bot")
```

---

## 6. Training Strategy (Making It Work in Practice)

### Phase 1: Single Map, No Player Movement
- Player stands still at a fixed position
- Bot learns: walk → jump gaps → reach target
- ~100K steps

### Phase 2: Single Map, Moving Player
- Player moves with simple AI (random walk)
- Bot learns to track and chase
- ~200K steps

### Phase 3: Multiple Maps
- Randomly switch maps each episode
- Bot generalizes across layouts
- ~200K steps

### Phase 4: Self-Play
- Player controlled by a second trained agent that tries to ESCAPE
- Both improve together (adversarial training)
- Ongoing

---

## 7. Integration with Current Codebase

### What to keep from `mask_dude_bot.py`
- **Physics** (`update()`, `get_collisions()`, `jump()`, wall slide) — the neural network controls WHEN to call these, not HOW they work
- **Observation helpers** (`check_gap_ahead`, `check_wall_ahead`, `can_see_player`) — repurpose as sensor inputs

### What to replace
- `update_ai()` — the entire scripted decision tree → replaced by neural network inference
- `ai_state`, `patrol_direction`, `search_timer` — no longer needed

### Minimal change to `MaskDudeBot`:

```python
class MaskDudeBot:
    def __init__(self, ...):
        # ... existing physics code unchanged ...
        self.model = None  # loaded PPO model

    def load_brain(self, model_path):
        from stable_baselines3 import PPO
        self.model = PPO.load(model_path)

    def update_ai(self, dt):
        if self.model is None:
            return  # fall back to scripted AI or do nothing

        obs = self.get_observation()
        action, _ = self.model.predict(obs, deterministic=True)

        # Map action index to behavior
        if action == 0:   self.vx = 0
        elif action == 1: self.vx = -BOT_SPEED; self.facing_right = False
        elif action == 2: self.vx =  BOT_SPEED; self.facing_right = True
        elif action == 3: self.jump()
        elif action == 4: self.jump()  # wall jump handled inside jump()
```

---

## 8. Quick-Start Checklist

- [ ] `pip install gymnasium stable-baselines3`
- [ ] Create `ShadowStalkerEnv` (gym wrapper around existing game)
- [ ] Add `get_observation()` and `compute_reward()` to `MaskDudeBot`
- [ ] Train with `PPO.learn(500_000)`
- [ ] Save model, load in `MaskDudeBot.load_brain()`
- [ ] Replace `update_ai()` with neural network inference
- [ ] Iterate on reward shaping until behavior is smooth

---

## TL;DR

| Now | Future |
|---|---|
| Hardcoded if/else rules | Neural network learns by playing |
| Can't adapt to new maps | Generalizes across layouts |
| Fixed behavior | Improves with more training |
| `update_ai()` decides | `model.predict(obs)` decides |
| ~50 lines of rules | ~5K parameter network learned from experience |
