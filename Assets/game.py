import pygame
import math

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

class Enemy:
    def __init__(self, x, y, path):
        self.x = x
        self.y = y
        self.path = path
        self.index = 0
        self.pos = self.path[self.index]
        self.current_point = 0  # Start at the first point in the path
        self.speed = 0.5  # Default speed (adjust this for faster/slower enemies)
        self.radius = 10  # Size of the enemy
        self.health = 70
        self.sprite = pygame.image.load("Assets/enemy.png").convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (20, 20))  # Resize the sprite to fit the enemy
        self.width = self.sprite.get_width()  # Set width from the sprite size
        self.height = self.sprite.get_height()  # Set height from the sprite size

        self.oscillation_time = 0  # Keeps track of the sway animation

        # Death animation variables
        self.is_dying = False
        self.fade_opacity = 255  # Start fully opaque
        
    def move(self):
        # If dying, stop movement
        if self.is_dying:
            return False

        # Check if we are not at the last point
        if self.current_point < len(self.path):
            target_x, target_y = self.path[self.current_point]
            direction_x = target_x - self.x
            direction_y = target_y - self.y
            distance = (direction_x**2 + direction_y**2) ** 0.5

            if distance > self.speed:
                # Move towards the next point
                self.x += (direction_x / distance) * self.speed
                self.y += (direction_y / distance) * self.speed
            else:
                # Snap to the target point and move to the next one
                self.x, self.y = target_x, target_y
                self.current_point += 1

        # Check if we've reached the final point
        if self.current_point >= len(self.path):
            return True  # Signal that this enemy has reached the end
        return False
    
    def draw(self, screen):
        """Draw the enemy on the screen with a sway effect."""
        if self.is_dying:
            # Tint the sprite red and apply fading effect
            red_tint = self.sprite.copy()
            red_tint.fill((255, 0, 0, self.fade_opacity), special_flags=pygame.BLEND_RGBA_MULT)
            rect = red_tint.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(red_tint, rect.topleft)
        else:
            # Regular oscillating movement
            self.oscillation_time += 0.09  # Increment time for oscillation
            sway_angle = math.sin(self.oscillation_time) * 25  # Oscillate between -30 and 30 degrees

            # Rotate the sprite
            rotated_sprite = pygame.transform.rotate(self.sprite, sway_angle)
            rect = rotated_sprite.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated_sprite, rect.topleft)

    def update(self):
        """Update the enemy (called in each game loop)."""
        if self.is_dying:
            # Reduce opacity gradually
            self.fade_opacity -= 5  # Adjust the value to control fade speed
            if self.fade_opacity <= 0:
                return "dead"  # Signal the enemy is ready to be removed
        elif self.health > 0:
            self.move()
        else:
            self.is_dying = True  # Trigger death animation


class Tower:
    def __init__(self, x, y, damage, range, cooldown, sprite_path):
        self.x = x
        self.y = y
        self.range = range  # Attack range
        self.damage = damage  # Damage per shot
        self.cooldown = cooldown  # Time between shots
        self.timer = 0  # Timer for cooldown
        self.target = None  # Current target enemy
        self.angle = 0  # Current angle of the turret
        self.rotation_speed = 5  # How fast the turret rotates (degrees per frame)

        # Load and resize the turret sprite
        self.sprite = pygame.image.load(sprite_path).convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (50, 50))
        self.original_sprite = self.sprite  # Keep original for rotation
        
        # Shoot sound effect
        self.shoot_sound_ = pygame.mixer.Sound("Assets/Sounds/shoot_sfx.wav")
        self.shoot_sound_.set_volume(0.4)

    def update(self, enemies, bullets):
        # Find a target within range
        self.target = None
        for enemy in enemies:
            dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
            if dist <= self.range:
                self.target = enemy
                break

        # Smoothly rotate towards the target
        if self.target:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            target_angle = math.degrees(math.atan2(-dy, dx)) - 90  # Desired angle (inverted Y-axis)

            # Smoothly interpolate the angle
            angle_diff = (target_angle - self.angle) % 360  # Difference in angle
            if angle_diff > 180:
                angle_diff -= 360  # Ensure the shortest rotation direction

            # Apply rotation speed limit
            if abs(angle_diff) > self.rotation_speed:
                self.angle += self.rotation_speed * (1 if angle_diff > 0 else -1)
            else:
                self.angle = target_angle  # Snap to the target angle when close enough

            # Normalize angle to keep it within 0-360 degrees
            self.angle %= 360

            # Shoot if the cooldown allows
            self.timer += 1
            if self.timer >= self.cooldown:
                self.timer = 0
                # Play the shoot sound
                self.shoot_sound_.play()
                self.shoot(bullets)

    def shoot(self, bullets):
        """Shoot a bullet towards the target."""
        if self.target:
            # Calculate direction to the target
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.sqrt(dx**2 + dy**2)

            # Normalize to get the direction
            bullet_dx = (dx / distance)
            bullet_dy = (dy / distance)

            # Spawn a new bullet
            bullet = Bullet(self.x, self.y, bullet_dx, bullet_dy, self.damage)
            bullets.append(bullet)

    def draw(self, screen):
        # Rotate the sprite based on the current angle
        rotated_sprite = pygame.transform.rotate(self.original_sprite, self.angle)
        rect = rotated_sprite.get_rect(center=(self.x, self.y))
        screen.blit(rotated_sprite, rect.topleft)

class TurretType1(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range = 100
        self.fire_rate = 30  # Shoots every 30 frames
        self.damage = 10
        self.sprite = pygame.image.load("Assets/DefaultTurret/turret_d_fire_0.png").convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (50, 50))


class TurretType2(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range = 150
        self.fire_rate = 50  # Slower shooting but longer range
        self.damage = 20
        self.sprite = pygame.image.load("Assets/AdvancedTurret/turret_a_fire_0.png").convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (50, 50))


class TurretType3(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range = 75
        self.fire_rate = 10  # Fast shooting, short range
        self.damage = 5
        self.sprite = pygame.image.load("Assets/GoldenTurret/turret_g_fire_0.png").convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (50, 50))

class Bullet:
    def __init__(self, x, y, dx, dy, damage):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.active = True  # Track if the bullet is still active
        self.sprite = pygame.image.load("Assets/Bullet.png").convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (20, 20))
        self.width = self.sprite.get_width()  # Set bullet width from sprite
        self.height = self.sprite.get_height()  # Set bullet height from sprite

    def collides_with(self, enemy):
        """Check if this bullet collides with the given enemy."""
        return (
            self.x < enemy.x + enemy.width and
            self.x + self.width > enemy.x and
            self.y < enemy.y + enemy.height and
            self.y + self.height > enemy.y
        )
    
    def update(self):
        """Update bullet position and check for collisions."""
        self.x += self.dx * 10
        self.y += self.dy * 10

        # Deactivate bullet if it goes out of bounds
        if self.x < 0 or self.x > 800 or self.y < 0 or self.y > 600:
            self.active = False
            
    def draw(self, screen):
        """Draw bullet on the screen."""
        if self.active:
            screen.blit(self.sprite, (int(self.x), int(self.y)))

class Game:
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Game state variables
        self.path = [(350, 0),(350, 50), (150, 50), (150, 150), (300, 150), (300, 300), (400, 300),(400, 370),(801, 370)]
        self.objects = []  # List to hold all game objects
        self.enemies = []
        self.towers = []
        self.bullets = []
        self.resources = 2423
        self.lives = 10

        # Wave system
        self.wave = 1
        self.enemies_to_spawn = 17  # Initial enemies per wave
        self.enemies_spawned = 0
        self.enemy_spawn_timer = 60  # Time between enemy spawns
        self.enemy_timer = 0  # Timer to control spawning
        self.enemy_hp = 500  # Base HP for enemies
        self.enemy_speed = 0.25 # Base speed for enemies
        self.money_per_enemy = 2  # Money gained for each enemy defeated
        self.boss_reward_multiplier = 2  # Boss reward multiplier

        #Hit sound effect
        self.hit_sound = pygame.mixer.Sound("Assets/Sounds/hit.wav")
        self.hit_sound.set_volume(0.15)
        
        self.finish_sound = pygame.mixer.Sound("Assets/Sounds/finish_hurt.wav")
        self.finish_sound.set_volume(0.15)

        # Store and turret data
        self.store_height = 100  # Height of the store at the bottom
        self.selected_turret = None  # Currently selected turret type
        self.turret_prices = [25, 150, 1000]  # Prices for each turret type
        self.turret_sprites = [
            pygame.image.load("Assets/DefaultTurret/turret_d_fire_0.png").convert_alpha(),
            pygame.image.load("Assets/AdvancedTurret/turret_a_fire_0.png").convert_alpha(),
            pygame.transform.scale(pygame.image.load("Assets/GoldenTurret/turret_g_fire_0.png").convert_alpha(), (50, 50))
        ]
        self.turret_sprites = [pygame.transform.scale(sprite, (50, 50)) for sprite in self.turret_sprites]

        # Load the sprite for valid turret placement spots
        self.placement_spot_sprite = pygame.image.load("Assets/turret_location.png").convert_alpha()
        self.placement_spot_sprite = pygame.transform.scale(self.placement_spot_sprite, (40, 40))

        # Tower placement spots (manually defined)
        self.valid_tower_spots = [
            (100, 100),
            (225, 100),
            (200, 200),
            (400, 100),
            (350, 250),
            (500, 300),
            (500, 450),
            (330, 370),
        ]
        self.spot_radius = 20  # Radius for valid placement spots

        # Font for UI
        self.font = pygame.font.SysFont(None, 36)

        # Load background image
        self.background_image = pygame.image.load("Assets/background.png").convert()
        self.background_image = pygame.transform.scale(self.background_image, (400, 300))

        # Load path sprite and resize to 4x4
        self.path_sprite = pygame.image.load("Assets/path.png").convert_alpha()
        self.path_sprite = pygame.transform.scale(self.path_sprite, (40, 40))

    def start_wave(self):
        """Start a new wave and reset enemy parameters."""
        self.enemies_spawned = 0  # Reset the spawn count
        self.enemy_timer = 0  # Reset spawn timer
        if self.wave % 5 == 0:  # Boss wave
            self.enemies_to_spawn = 1
            self.enemy_hp = 2 * (30 + 20 * self.wave)  # Boss has higher HP
            self.enemy_speed = 0.1 + 0.05 * self.wave * 1.5  # Slightly faster
            self.money_per_enemy *= self.boss_reward_multiplier
        else:  # Regular wave
            self.enemies_to_spawn = int(5 + self.wave * 1.5)  # Enemies increase
            self.enemy_hp = 30 + 2.5 * self.wave  # Scale health
            self.enemy_speed = 0.1 + 0.05 * self.wave  # Scale speed
            self.money_per_enemy = 2 + self.wave  # Scale rewards

    def handle_event(self, event):
        """Handle player interactions (e.g., placing towers)."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            # Check if a turret is clicked in the store
            if y >= self.screen_height - self.store_height:
                button_width = 50
                padding = 20
                total_button_width = len(self.turret_sprites) * button_width + (len(self.turret_sprites) - 1) * padding
                start_x = (self.screen_width - total_button_width) // 2
                sprite_y = self.screen_height - self.store_height + 15

                for i, sprite in enumerate(self.turret_sprites):
                    sprite_x = start_x + i * (button_width + padding)
                    if sprite_x <= x <= sprite_x + button_width and sprite_y <= y <= sprite_y + button_width:
                        if self.resources >= self.turret_prices[i]:
                            turret_types = ["Default", "Advanced", "Golden"]
                            self.selected_turret = turret_types[i]
                            return

            # Check if the click is on a valid tower placement spot (left-click to place turret)
            for spot in self.valid_tower_spots:
                dist = ((x - spot[0]) ** 2 + (y - spot[1]) ** 2) ** 0.5
                if dist <= self.spot_radius and self.resources >= 10:  # Cost to place a tower
                    if self.selected_turret:  # Check if a turret is selected in the store
                        # Create the selected tower type
                        if self.selected_turret == "Default":
                            tower = Tower(spot[0], spot[1], damage=15, range=200, cooldown=50, sprite_path="Assets/DefaultTurret/turret_d_fire_0.png")
                            self.resources -= 25
                        elif self.selected_turret == "Advanced":
                            tower = Tower(spot[0], spot[1], damage=30, range=200, cooldown=20, sprite_path="Assets/AdvancedTurret/turret_a_fire_0.png")
                            self.resources -= 150
                        elif self.selected_turret == "Golden":
                            tower = Tower(spot[0], spot[1], damage=50, range=250, cooldown=10, sprite_path="Assets/GoldenTurret/turret_g_fire_0.png")
                            self.resources -= 1000
                        # Place the tower and deduct resources
                        self.towers.append(tower)
                        self.objects.append(tower)  # Add to the global object list
                        self.selected_turret = None  # Deselect the turret after placement
                        return  # Exit after placing one tower

            # Right-click to cancel turret selection
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.selected_turret = None

                # Check if the right-click is on an existing turret to delete it
                for tower in self.towers:
                    dist = ((x - tower.x) ** 2 + (y - tower.y) ** 2) ** 0.5
                    if dist <= self.spot_radius:  # Check if the right-click is within range of the turret
                        self.towers.remove(tower)
                        self.objects.remove(tower)  # Also remove from the global object list
                        self.resources += 5  # Refund a portion of the cost (e.g., 50% of the turret cost)
                        return  # Exit after deleting one turret

        # Right-click to cancel turret selection
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.selected_turret = None
   
    def update(self):
        """Update the game state."""
        # Spawn enemies periodically
        if self.enemies_spawned < self.enemies_to_spawn and self.enemy_timer == 0:
            if self.wave % 5 == 0:  # Boss wave
                enemy = Enemy(self.path[0][0], self.path[0][1], self.path)
                enemy.health = self.enemy_hp
                enemy.speed = self.enemy_speed
            else:
                enemy = Enemy(self.path[0][0], self.path[0][1], self.path)
                enemy.health = self.enemy_hp
                enemy.speed = self.enemy_speed

            self.enemies.append(enemy)
            self.objects.append(enemy)
            self.enemies_spawned += 1
            self.enemy_timer = self.enemy_spawn_timer
        elif self.enemy_timer > 0:
            self.enemy_timer -= 1


        # Update all objects (towers and enemies)
        for obj in self.objects:
            if isinstance(obj, Tower):
                obj.update(self.enemies, self.bullets)  # Pass the global bullet list
            else:
                obj.update()  # Update other objects (e.g., enemies)
                
        for enemy in self.enemies[:]:
            enemy.update()  # Pass the enemies list to the enemy's update method
            # Additional game logic (e.g., checking win conditions, updating game state)


        # Update bullets and check for collisions with enemies
        for bullet in self.bullets:
            bullet.update()  # Update bullet position based on its speed

            for enemy in self.enemies:
                if bullet.collides_with(enemy):  # Check if the bullet collides with the enemy
                    enemy.health -= bullet.damage
                    self.hit_sound.play()
                    bullet.active = False  # Deactivate the bullet upon collision
                    if enemy.health <= 0:  # Check if the enemy is killed
                        self.resources += self.money_per_enemy  # Add reward for killing the enemy
                        break  # Exit loop after a collision, as the bullet can only hit one enemy at a time
                    
        # Remove inactive bullets from the list
        self.bullets = [bullet for bullet in self.bullets if bullet.active]

        # Remove enemies that reach the end or are fully faded
        enemies_to_remove = []  # Temporary list to hold enemies to remove
        for enemy in self.enemies:
            if enemy.move():  # Enemy reached the end of the path
                self.lives -= 1
                self.finish_sound.play()
                enemies_to_remove.append(enemy)
            elif enemy.update() == "dead":  # Check if the enemy is fully faded out
                enemies_to_remove.append(enemy)

        # Now, actually remove the enemies from the list
        for enemy in enemies_to_remove:
            if enemy in self.objects:  # Ensure the enemy is in self.objects
                self.objects.remove(enemy)  # Remove the enemy from the objects list
            self.enemies.remove(enemy)  # Remove the enemy from the enemies list

        # Check if wave is cleared
        if not self.enemies and self.enemies_spawned == self.enemies_to_spawn:
            self.wave += 1
            self.start_wave()

    def is_over(self):
        return self.lives <= 0  # Game is over when health is 0 or less
    
    def last_wave(self):
        return self.wave

    def draw(self):
        """Render all objects and UI."""
        # Draw the background
        for x in range(0, self.screen_width, self.background_image.get_width()):
            for y in range(0, self.screen_height, self.background_image.get_height()):
                self.screen.blit(self.background_image, (x, y))

        # Draw path
        for i in range(len(self.path) - 1):
            start = self.path[i]
            end = self.path[i + 1]
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            distance = math.sqrt(dx ** 2 + dy ** 2)
            steps = int(distance / 4)
            for j in range(steps + 1):
                x = start[0] + (dx / steps) * j
                y = start[1] + (dy / steps) * j
                self.screen.blit(self.path_sprite, (x - self.path_sprite.get_width() / 2, y - self.path_sprite.get_height() / 2))

        # Draw valid turret placement spots using the sprite
        for spot in self.valid_tower_spots:
            spot_x = spot[0] - self.placement_spot_sprite.get_width() // 2
            spot_y = spot[1] - self.placement_spot_sprite.get_height() // 2
            self.screen.blit(self.placement_spot_sprite, (spot_x, spot_y))

        # Draw all objects
        for obj in self.objects:
            obj.draw(self.screen)

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)

        # Draw UI
        money_text = self.font.render(f"Money: ${self.resources}", True, BLACK)
        self.screen.blit(money_text, (10, self.screen_height - self.store_height - 30))

        lives_text = self.font.render(f"Lives: {self.lives}", True, BLACK)
        self.screen.blit(lives_text, (10, self.screen_height - self.store_height - 60))

        wave_text = self.font.render(f"Wave: {self.wave}", True, BLACK)
        self.screen.blit(wave_text, (self.screen_width - 150, 10))

        # Draw the store
        pygame.draw.rect(self.screen, (200, 200, 200), (0, self.screen_height - self.store_height, self.screen_width, self.store_height))

        # Center the turret buttons in the store
        button_width = 50
        padding = 20  # Padding between buttons
        total_button_width = len(self.turret_sprites) * button_width + (len(self.turret_sprites) - 1) * padding
        start_x = (self.screen_width - total_button_width) // 2  # Correct start_x calculation
        y = self.screen_height - self.store_height + 15  # Y position for buttons

        for i, sprite in enumerate(self.turret_sprites):
            x = start_x + i * (button_width + padding)  # Consistent horizontal spacing
            self.screen.blit(sprite, (x, y))

            # Draw turret prices below the turret
            price_text = self.font.render(f"${self.turret_prices[i]}", True, BLACK)
            self.screen.blit(price_text, (x, y + button_width + 5))
            
        # Draw selected turret following the cursor
        if self.selected_turret is not None:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Map the turret type to its index
            turret_index = {"Default": 0, "Advanced": 1, "Golden": 2}
            # Ensure selected_turret is valid
            if self.selected_turret in turret_index:
                sprite_index = turret_index[self.selected_turret]
                sprite = self.turret_sprites[sprite_index]
                self.screen.blit(sprite, (mouse_x - sprite.get_width() // 2, mouse_y - sprite.get_height() // 2))