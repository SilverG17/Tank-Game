🛡️ Tank Battle: Chaos Maze (Physics Edition)

A high-octane, 2-player tactical shooter built with Python and Pygame. This project demonstrates core game programming principles, focusing on vector-based movement, AABB collision detection, and reflective ballistics.

🕹️ 1. Controls
The game supports two players on a single keyboard with independent turret and hull controls.

| Action          | Player 1 (Green)   | Player 2 (Red)        |
| --------------- | ------------------ | --------------------- |
| Tank Movement   | W, A, S, D         | Up, Down, Left, Right |
| Turret Rotation | Q, E               | K, L                  |
| Fire Weapon     | SPACE or F         | ENTER or M            |
| System          | ESC (Back to Menu) | R (Restart Mission)   |

🔬 2. Physics Implementation

A. Vector-Based Movement

Tanks move based on their current rotation angle $\\theta$. Instead of simple grid movement, we calculate continuous trajectory vectors.

Mathematical Formula:

&nbsp; velocity.x = speed \\times \\cos(\\theta)

&nbsp; velocity.y = speed \\times \\sin(\\theta)

Code Snippet:

\# Convert degrees to radians and offset by -90 to match sprite orientation

rad = math.radians(self.hull_angle - 90)

if keys\[self.controls\['up']]:

&nbsp; # Calculate movement vector using Cosine and Sine

&nbsp; move_vec = pygame.Vector2(math.cos(rad), math.sin(rad))

elif keys\[self.controls\['down']]:

&nbsp; move_vec = pygame.Vector2(-math.cos(rad), -math.sin(rad))

\# Apply delta time (dt) for frame-independent movement

new_pos = self.pos + move_vec \* (160 \* self.speed_boost) \* dt

B. Collision Detection (AABB)

To prevent tanks from passing through walls, we utilize Axis-Aligned Bounding Box (AABB) logic combined with hitbox inflation for smoother navigation.

Code Snippet:

def check_collision(self, next_pos, trees):

&nbsp; # Use .inflate() to create a smaller physics hitbox (-20px)

&nbsp; # This allows the tank to "graze" walls without getting stuck.

&nbsp; tank_rect = self.hull.get_rect(center=next_pos).inflate(-20, -20)

&nbsp; # Check collision with Indestructible Rock tiles ('B')

&nbsp; for gy in range(start_y, end_y):

&nbsp; for gx in range(start_x, end_x):

&nbsp; if self.level_map\[gy]\[gx] == 'B':

&nbsp; block_rect = pygame.Rect(gx \* TILE_SIZE, gy \* TILE_SIZE, TILE_SIZE, TILE_SIZE)

&nbsp; if tank_rect.colliderect(block_rect):

&nbsp; return False # Stop movement

&nbsp; return True

C. Ballistics \& Bouncing (Reflection)

Bullets reflect off walls based on the surface normal vector $\\vec{n}$.

The Reflection Formula:

V_new = V_old - 2(V_old ⋅ n) \* n

Where:

● V_old: Incoming velocity vector.

● n: The normal vector of the wall surface.

● V_new: Resulting reflection velocity vector.

✨ 3. Visual Effects (Particle System)

We implemented a dynamic Particle System to provide high-quality visual feedback for explosions and combat.

● Explosions: When a tank's health reaches 0, it triggers a ParticleSystem that spawns 50+ particles.

● Physics: Each particle is a physics object with a randomized velocity vector and a linear decay (fade-out) based on its lifetime.

🚀 4. Technical Features

● Dynamic Map Rendering: The arena is generated from a LEVEL_MAP (list of strings), making it easy to design new mazes.

● Destructible Environment: Trees ('T') act as obstacles that can be destroyed after 4 hits, updating the collision map in real-time.

● Power-up System: \* ⚡ SPEED: 1.8x movement multiplier.

○ 🛡️ SHIELD: Negates the next incoming damage.

○ 🔫 TRIPLE SHOT: Fires three bullets in a spread pattern.

🎨 5. Asset Sources

● Graphics: \* Tank Hulls/Guns: Top-down Tanks by Kenney.nl (CC0).

○ Tileset: Top-down Racing/Shooter grass and road tiles.

● Audio: \* fire.mp3, hit.mp3, coin.mp3 - Royalty-free arcade SFX.

○ explosion.mp3 - Custom synthesized explosion sound.

● Fonts: Impact (Titles), Consolas (Scores).

🛠️ 6. How to Run

Ensure you have Python 3.10+ and Pygame installed:

1.pip install pygame

2.python main.py
