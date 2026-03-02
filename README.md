# 🛡️ Tank Battle: Chaos Maze (Physics Edition)

A high-intensity **2-player tactical shooter** built with **Python** and **Pygame**.
This project focuses on implementing real-time game physics including:

- Vector-based movement
- AABB collision detection
- Reflective ballistics
- Particle-based visual effects

---

## 🎮 1. Controls

The game supports two players on a single keyboard with **independent hull and turret rotation**.

| Action          | Player 1 (Green) | Player 2 (Red)        |
| --------------- | ---------------- | --------------------- |
| Tank Movement   | `W A S D`        | `↑ ↓ ← →`             |
| Turret Rotation | `Q / E`          | `K / L`               |
| Fire Weapon     | `SPACE` or `F`   | `ENTER` or `M`        |
| System Controls | `ESC` (Menu)     | `R` (Restart Mission) |

---

## 🔬 2. Physics System

### A. Vector-Based Movement

Instead of grid-based movement, tanks move using continuous vectors derived from their current rotation angle ( \theta ).

### Mathematical Model

```
velocity.x = speed × cos(θ)
velocity.y = speed × sin(θ)
```

### Implementation

```python
# Convert degrees to radians and offset by -90° to match sprite orientation
rad = math.radians(self.hull_angle - 90)

if keys[self.controls['up']]:
    move_vec = pygame.Vector2(math.cos(rad), math.sin(rad))
elif keys[self.controls['down']]:
    move_vec = pygame.Vector2(-math.cos(rad), -math.sin(rad))

# Frame-independent movement using delta time (dt)
new_pos = self.pos + move_vec * (160 * self.speed_boost) * dt
```

✔ Ensures smooth 360° rotation
✔ Maintains consistent speed across different frame rates

---

### B. Collision Detection (AABB)

To prevent tanks from passing through walls, the game uses **Axis-Aligned Bounding Box (AABB)** collision detection.

A slightly reduced hitbox is used to improve gameplay smoothness.

```python
def check_collision(self, next_pos, trees):
    # Create smaller physics hitbox for smoother wall interaction
    tank_rect = self.hull.get_rect(center=next_pos).inflate(-20, -20)

    for gy in range(start_y, end_y):
        for gx in range(start_x, end_x):
            if self.level_map[gy][gx] == 'B':
                block_rect = pygame.Rect(
                    gx * TILE_SIZE,
                    gy * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )

                if tank_rect.colliderect(block_rect):
                    return False  # Block movement
    return True
```

✔ Prevents wall clipping
✔ Allows controlled “grazing” against obstacles

---

### C. Ballistics & Reflection Physics

Bullets reflect off solid surfaces using the **vector reflection formula**:

```
V_new = V_old − 2(V_old · n) n
```

Where:

- `V_old` = incoming velocity vector
- `n` = surface normal vector
- `V_new` = reflected velocity

✔ Enables realistic bounce mechanics
✔ Adds tactical depth to gameplay

---

## ✨ 3. Particle System

A lightweight physics-based particle engine enhances visual feedback.

### Explosion Effects

- Triggered when tank HP reaches zero
- Spawns 50+ dynamic particles

### Particle Behavior

- Randomized velocity vectors
- Linear alpha decay over lifetime
- Independent physics updates

Result: Responsive and satisfying combat visuals.

---

## 🚀 4. Core Features

### 🗺️ Dynamic Map Rendering

Maps are generated from a `LEVEL_MAP` (list of strings), enabling fast maze creation and customization.

Example:

```
B = Rock (Indestructible)
T = Tree (Destructible)
```

---

### 🌲 Destructible Environment

- Trees (`'T'`) require 4 hits to destroy
- Collision map updates in real time

---

### ⚡ Power-Up System

| Power-Up       | Effect                              |
| -------------- | ----------------------------------- |
| ⚡ SPEED       | 1.8× movement multiplier            |
| 🛡️ SHIELD      | Negates next incoming damage        |
| 🔫 TRIPLE SHOT | Fires 3 bullets in a spread pattern |

---

## 🎨 5. Assets & Credits

### Graphics

- Tank Hulls & Guns: Top-down Tanks by **Kenney.nl** (CC0)
- Tileset: Top-down racing/shooter grass & road tiles

### Audio

- `fire.mp3`, `hit.mp3`, `coin.mp3` — Royalty-free arcade SFX
- `explosion.mp3` — Custom synthesized effect

### Fonts

- Impact (Titles)
- Consolas (UI & Scores)

---

## 🛠️ 6. Installation & Running

### Requirements

- Python 3.10+
- Pygame

### Install Dependencies

```bash
pip install pygame
```

### Run the Game

```bash
python main.py
```

---

## 📚 Learning Objectives

This project demonstrates:

- Vector mathematics in game physics
- Collision detection systems
- Frame-rate independent motion
- Real-time particle simulation
- Modular game state architecture
