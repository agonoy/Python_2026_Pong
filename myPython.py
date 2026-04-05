import pygame
import sys
import random
import math
from array import array

# Initialize Pygame
pygame.init()

# Initialize audio for sound effects when available
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
    AUDIO_AVAILABLE = True
except pygame.error:
    AUDIO_AVAILABLE = False


def create_tone(frequency, duration, volume=0.35, sample_rate=44100):
    """Create a simple sine-wave sound effect."""
    if not AUDIO_AVAILABLE:
        return None
    sample_count = int(sample_rate * duration)
    samples = array("h")
    amplitude = int(32767 * volume)
    for index in range(sample_count):
        value = int(amplitude * math.sin(2 * math.pi * frequency * index / sample_rate))
        samples.append(value)
    return pygame.mixer.Sound(buffer=samples.tobytes())


PADDLE_HIT_SOUND = create_tone(740, 0.08, 0.30)
WALL_BOUNCE_SOUND = create_tone(520, 0.06, 0.25)
SCORE_SOUND = create_tone(220, 0.18, 0.35)
WIN_SOUND = create_tone(880, 0.35, 0.40)

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_GREEN = (0, 255, 0)
NEON_ORANGE = (255, 165, 0)
NEON_PINK = (255, 20, 147)
DARK_BLUE = (25, 25, 112)

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🎮 PONG GAME 🎮")

# Clock for FPS
clock = pygame.time.Clock()
FPS = 60

# Paddle properties
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 120
PADDLE_SPEED = 6

# Ball properties
BALL_SIZE = 15
BALL_SPEED_X = 6
BALL_SPEED_Y = 6
MAX_BOUNCE_ANGLE = 60

# Font for score and text
font_large = pygame.font.Font(None, 74)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)


class Paddle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((PADDLE_WIDTH, PADDLE_HEIGHT))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.color = color
        self.speed = 0

    def move_up(self):
        if self.rect.y > 0:
            self.rect.y -= PADDLE_SPEED

    def move_down(self):
        if self.rect.y < SCREEN_HEIGHT - PADDLE_HEIGHT:
            self.rect.y += PADDLE_SPEED

    def ai_move(self, ball_y):
        """Simple AI opponent"""
        paddle_center = self.rect.y + PADDLE_HEIGHT // 2
        if paddle_center < ball_y - 35:
            self.move_down()
        elif paddle_center > ball_y + 35:
            self.move_up()

    def update(self):
        pass

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        # Add glow effect
        pygame.draw.rect(surface, self.color, self.rect, 3)


class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((BALL_SIZE, BALL_SIZE))
        self.image.fill(NEON_GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = BALL_SPEED_X * random.choice([-1, 1])
        self.speed_y = BALL_SPEED_Y * random.choice([-1, 1])

    def reset(self):
        """Reset ball to center"""
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = BALL_SPEED_X * random.choice([-1, 1])
        self.speed_y = BALL_SPEED_Y * random.choice([-1, 1])

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Bounce off top and bottom
        bounced = False
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speed_y *= -1
            self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - BALL_SIZE))
            bounced = True

        return bounced

    def draw(self, surface):
        pygame.draw.circle(surface, NEON_GREEN, self.rect.center, BALL_SIZE // 2)
        pygame.draw.circle(surface, WHITE, self.rect.center, BALL_SIZE // 2, 2)


class Game:
    def __init__(self):
        self.player1 = Paddle(30, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, NEON_CYAN)
        self.player2 = Paddle(SCREEN_WIDTH - 45, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, NEON_MAGENTA)
        self.ball = Ball()
        self.score1 = 0
        self.score2 = 0
        self.running = True
        self.game_over = False
        self.win_sound_played = False

    def play_sound(self, sound):
        if sound is not None:
            sound.play()

    def reset_game(self):
        self.__init__()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.game_over:
                    self.reset_game()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player2.move_up()
        if keys[pygame.K_s]:
            self.player2.move_down()

    def update(self):
        bounced = self.ball.update()
        self.player1.ai_move(self.ball.rect.centery)

        # Collision with paddles
        if self.ball.rect.colliderect(self.player1.rect) and self.ball.speed_x < 0:
            self.ball.speed_x *= -1.05
            self.ball.rect.left = self.player1.rect.right
            # Add spin based on where the ball hits the paddle
            hit_pos = (self.ball.rect.centery - self.player1.rect.centery) / PADDLE_HEIGHT
            self.ball.speed_y += hit_pos * 4
            self.play_sound(PADDLE_HIT_SOUND)

        if self.ball.rect.colliderect(self.player2.rect) and self.ball.speed_x > 0:
            self.ball.speed_x *= -1.05
            self.ball.rect.right = self.player2.rect.left
            # Add spin based on where the ball hits the paddle
            hit_pos = (self.ball.rect.centery - self.player2.rect.centery) / PADDLE_HEIGHT
            self.ball.speed_y += hit_pos * 4
            self.play_sound(PADDLE_HIT_SOUND)

        if bounced:
            self.play_sound(WALL_BOUNCE_SOUND)

        # Check if ball goes out of bounds (scoring)
        if self.ball.rect.left < 0:
            self.score2 += 1
            self.play_sound(SCORE_SOUND)
            self.ball.reset()
        if self.ball.rect.right > SCREEN_WIDTH:
            self.score1 += 1
            self.play_sound(SCORE_SOUND)
            self.ball.reset()

        # Check win condition
        if self.score1 >= 11 or self.score2 >= 11:
            self.game_over = True
            if not self.win_sound_played:
                self.play_sound(WIN_SOUND)
                self.win_sound_played = True

    def draw(self):
        screen.fill(DARK_BLUE)

        # Draw center line (dashed)
        for y in range(0, SCREEN_HEIGHT, 20):
            pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, y), (SCREEN_WIDTH // 2, y + 10), 2)

        # Draw paddles
        self.player1.draw(screen)
        self.player2.draw(screen)

        # Draw ball
        self.ball.draw(screen)

        # Draw scores
        score_text = font_large.render(f"{self.score1}  -  {self.score2}", True, NEON_ORANGE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(score_text, score_rect)

        # Draw player labels
        player1_text = font_small.render("AI", True, NEON_CYAN)
        screen.blit(player1_text, (50, 30))
        player2_text = font_small.render("YOU (W/S)", True, NEON_MAGENTA)
        screen.blit(player2_text, (SCREEN_WIDTH - 150, 30))

        if self.game_over:
            winner = "AI WINS!" if self.score1 > self.score2 else "YOU WIN!"
            winner_text = font_large.render(winner, True, NEON_PINK)
            winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(winner_text, winner_rect)

            restart_text = font_medium.render("Press SPACE to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
            screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.handle_input()
            self.update()
            self.draw()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
