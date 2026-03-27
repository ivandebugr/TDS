import pygame
from Assets.game import Game
from Assets import button

# Define colors
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

# Screen dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Load images
# Button images
start_img = pygame.image.load('Assets/start_button.png') #Basically you need to have a folder in the same directory as the script. That folder should have that image after
exit_img = pygame.image.load('Assets/quit_button.png')
main_bg_img = pygame.image.load('Assets/main_menu_bg.png')
main_bg_img = pygame.transform.scale(main_bg_img, (int(main_bg_img.get_width()), int(main_bg_img.get_height())))

class ScreenFade():
    def __init__(self, direction, colour, speed, window_):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0
        self.window_ = window_

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed

        if self.direction == 1:  # Whole screen fade
            # Draw a full-screen transparent surface that becomes more opaque over time
            fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            fade_surface.fill(self.colour)
            fade_surface.set_alpha(self.fade_counter)  # Increase alpha based on fade_counter
            self.window_.blit(fade_surface, (0, 0))

        elif self.direction == 2:  # Vertical screen fade down
            # Draw a rectangle that grows vertically downward
            pygame.draw.rect(self.window_, self.colour, (0, 0, WINDOW_WIDTH, self.fade_counter))

        # Check if fade is complete
        if self.fade_counter >= 255:  # 255 is max alpha for full opacity
            fade_complete = True

        return fade_complete


def main():
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tower Defense Game")
    clock = pygame.time.Clock()
    
    pygame.mixer.music.load("Assets/Music/main_theme.wav")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(loops=-1, fade_ms=5000)

    intro_fade = ScreenFade(1, BLACK, 4, window)
    death_fade = ScreenFade(1, PINK, 4, window)

    # Flags for the game state
    start_game = False
    start_intro = False
    is_game_over = False
    death_fade_complete = False

    start_button = button.Button(WINDOW_WIDTH // 2 - 152.5, WINDOW_HEIGHT // 2 + 80, start_img, 1)
    exit_button = button.Button(WINDOW_WIDTH // 2 - 152.5, WINDOW_HEIGHT // 2 + 200, exit_img, 1)

    game = Game(window, WINDOW_WIDTH, WINDOW_HEIGHT)

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if start_game and not is_game_over:
                game.handle_event(event)

        # Menu logic
        if not start_game:
            window.blit(main_bg_img, (0, 0))
            if start_button.draw(window):
                start_game = True
                start_intro = True
            if exit_button.draw(window):
                running = False
        else:
            if start_intro:
                if intro_fade.fade():
                    start_intro = False
            elif is_game_over:
                if not death_fade_complete:
                    death_fade_complete = death_fade.fade()
                    delay_start_time = pygame.time.get_ticks()
                else:
                    # After 2 seconds, show Game Over screen
                    if pygame.time.get_ticks() - delay_start_time >= 2000:
                        # Draw "Game Over" text and restart/exit buttons
                        font = pygame.font.SysFont(None, 75)
                        text = font.render("Game Over!", True, WHITE)
                        wave_c = game.last_wave()
                        wave_text = font.render(f"You've survived {wave_c} waves!", True, WHITE)
                        window.fill(BLACK)
                        window.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT // 2 - text.get_height() // 2 - 80))
                        window.blit(wave_text, (WINDOW_WIDTH // 2 - text.get_width() // 2 - 170, WINDOW_HEIGHT // 2 - text.get_height() // 2))
                        
                        restart_button = button.Button(WINDOW_WIDTH // 2 - 152.5, WINDOW_HEIGHT // 2 + 80, start_img, 1)
                        exit_button = button.Button(WINDOW_WIDTH // 2 - 152.5, WINDOW_HEIGHT // 2 + 200, exit_img, 1)
                        
                        if restart_button.draw(window):
                            start_game = False
                            is_game_over = False
                            death_fade_complete = False
                            game = Game(window, WINDOW_WIDTH, WINDOW_HEIGHT)  # Reinitialize the game
                        if exit_button.draw(window):
                            running = False
            else:
                # Normal game logic
                game.update()

                if game.is_over(): 
                    is_game_over = True

                game.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

main()