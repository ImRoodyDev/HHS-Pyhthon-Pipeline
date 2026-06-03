# Standard library imports for argument parsing, CSV writing, math, randomness and timing
import argparse
import csv
import math
import random
import time
from dataclasses import dataclass
from pathlib import Path

# Always resolve data/model paths relative to this script, not the working directory
SCRIPT_DIR = Path(__file__).parent

# --- Screen and timing constants ---
WIDTH = 640
HEIGHT = 480
FPS = 60

# --- Player constants ---
PLAYER_WIDTH = 44
PLAYER_HEIGHT = 30
PLAYER_Y = HEIGHT - 58   # fixed Y position near the bottom of the screen
PLAYER_SPEED = 360       # pixels per second

# --- Stone constants ---
STONE_MIN_RADIUS = 14
STONE_MAX_RADIUS = 24
STONE_MIN_SPEED = 170    # pixels per second (slowest stone)
STONE_MAX_SPEED = 285    # pixels per second (fastest stone)
SPAWN_SECONDS = 0.55     # a new stone spawns every 0.55 seconds

# Feature names that the neural network uses as input (10 values, all normalised)
FEATURE_COLUMNS = [
    "player_x_norm",
    "player_velocity_norm",
    "stone_x_norm",
    "stone_y_norm",
    "stone_speed_norm",
    "dx_norm",
    "abs_dx_norm",
    "danger_left",
    "danger_center",
    "danger_right",
]

# Columns written to the training CSV (features + metadata + label)
CSV_COLUMNS = [
    "timestamp",
    "score",
    *FEATURE_COLUMNS,
    "action",
]


# --- Game objects ---

@dataclass
class Player:
    # The player starts horizontally centred and has no initial velocity
    x: float = WIDTH / 2
    velocity: float = 0

    @property
    def rect(self):
        # Return a pygame Rect for collision detection and drawing
        import pygame
        return pygame.Rect(
            int(self.x - PLAYER_WIDTH / 2),
            PLAYER_Y,
            PLAYER_WIDTH,
            PLAYER_HEIGHT,
        )

    def move(self, action, dt):
        # action: -1 = left, 0 = stay, 1 = right
        # Multiply by dt (seconds since last frame) to keep speed frame-rate independent
        self.velocity = action * PLAYER_SPEED
        self.x += self.velocity * dt
        # Clamp so the player cannot leave the screen
        min_x = PLAYER_WIDTH / 2
        max_x = WIDTH - PLAYER_WIDTH / 2
        self.x = max(min_x, min(max_x, self.x))


@dataclass
class Stone:
    x: float
    y: float
    radius: int
    speed: float  # falling speed in pixels per second

    @property
    def rect(self):
        # Bounding box around the circle for collision detection
        import pygame
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def update(self, dt):
        # Move the stone downward each frame
        self.y += self.speed * dt


# --- Training data logger ---

class TrainingLogger:
    def __init__(self, path):
        self.path = Path(path)
        # Create the output directory if it does not exist yet
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = self.path.open("a", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.file, fieldnames=CSV_COLUMNS)
        # Only write the header if the file is new/empty
        if self.path.stat().st_size == 0:
            self.writer.writeheader()

    def write(self, score, features, action):
        # Write one row per frame: timestamp, score, all features, and the action taken
        row = {
            "timestamp": time.time(),
            "score": score,
            **features,
            "action": action,
        }
        self.writer.writerow(row)

    def close(self):
        self.file.close()


# --- Feature engineering helpers ---

def normalize(value, minimum, maximum):
    # Scale a value to the range [0, 1]
    return (value - minimum) / (maximum - minimum)


def nearest_dangerous_stone(player, stones):
    # Only consider stones that are close enough to be a threat (within 80 px of the player row)
    candidates = [stone for stone in stones if stone.y + stone.radius < PLAYER_Y + 80]
    if not candidates:
        return None
    # Pick the stone with the least time-to-reach (distance / speed)
    return min(candidates, key=lambda stone: abs((PLAYER_Y - stone.y) / max(stone.speed, 1)))


def danger_for_action(player_x, stone, action):
    # Simulate where the player would be ~0.28 s in the future if it takes this action
    future_player_x = player_x + action * PLAYER_SPEED * 0.28
    future_player_x = max(PLAYER_WIDTH / 2, min(WIDTH - PLAYER_WIDTH / 2, future_player_x))
    horizontal_gap = abs(future_player_x - stone.x)
    # The stone is only dangerous if it is in the lower part of the screen
    close_to_player = stone.y > HEIGHT * 0.42
    # Return 1 if that action would put the player in the stone's path, 0 otherwise
    return int(close_to_player and horizontal_gap < (PLAYER_WIDTH / 2 + stone.radius + 10))


def extract_features(player, stones):
    # Build the 10-value normalised feature vector for the current frame
    stone = nearest_dangerous_stone(player, stones)

    if stone is None:
        # No dangerous stone: use neutral default values
        stone_x = WIDTH / 2
        stone_y = 0
        stone_speed = STONE_MIN_SPEED
        dx = 0
        danger_left = danger_center = danger_right = 0
    else:
        stone_x = stone.x
        stone_y = stone.y
        stone_speed = stone.speed
        dx = stone.x - player.x  # positive = stone is to the right
        danger_left   = danger_for_action(player.x, stone, -1)
        danger_center = danger_for_action(player.x, stone,  0)
        danger_right  = danger_for_action(player.x, stone,  1)

    features = {
        "player_x_norm":       normalize(player.x, 0, WIDTH),
        "player_velocity_norm": player.velocity / PLAYER_SPEED,
        "stone_x_norm":        normalize(stone_x, 0, WIDTH),
        "stone_y_norm":        normalize(stone_y, 0, HEIGHT),
        "stone_speed_norm":    normalize(stone_speed, STONE_MIN_SPEED, STONE_MAX_SPEED),
        "dx_norm":             dx / WIDTH,
        "abs_dx_norm":         abs(dx) / WIDTH,
        "danger_left":         danger_left,
        "danger_center":       danger_center,
        "danger_right":        danger_right,
    }
    return features


# --- Action sources ---

def human_action(keys):
    # Read keyboard input and return -1, 0 or 1
    import pygame
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        return -1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        return 1
    return 0


def heuristic_action(player, stones):
    # Simple rule: only dodge when the nearest stone is very close horizontally
    stone = nearest_dangerous_stone(player, stones)
    if stone is None or stone.y < HEIGHT * 0.35:
        return 0  # no threat yet, stay still
    if abs(stone.x - player.x) > PLAYER_WIDTH:
        return 0  # stone is far enough, no need to move
    # Move toward the edge that has more space
    if player.x < WIDTH / 2:
        return -1
    return 1


def load_ai(path):
    # Load a trained model saved with joblib.
    # Supports both a plain model and a dict bundle that also stores feature column names.
    import joblib
    bundle = joblib.load(path)
    if isinstance(bundle, dict):
        return bundle["model"], bundle.get("feature_columns", FEATURE_COLUMNS)
    return bundle, FEATURE_COLUMNS


def ai_action(model, feature_columns, features):
    # Build the input row in the correct column order and let the model predict an action
    values = [[features[column] for column in feature_columns]]
    try:
        # Use class probabilities and penalise "stay still" so the AI moves more aggressively.
        # Training data is usually dominated by action=0, which causes the model to freeze;
        # reducing its probability weight forces the AI to dodge sooner.
        proba = model.predict_proba(values)[0].copy()
        classes = list(model.classes_)
        if 0 in classes:
            proba[classes.index(0)] *= 0.40  # strongly discourage staying still
        return int(classes[int(proba.argmax())])
    except Exception:
        return int(model.predict(values)[0])


# --- Stone spawning ---

def spawn_stone(stones):
    # Add a new stone at a random X position just above the top of the screen
    stones.append(
        Stone(
            x=random.randint(STONE_MAX_RADIUS, WIDTH - STONE_MAX_RADIUS),
            y=-STONE_MAX_RADIUS,
            radius=random.randint(STONE_MIN_RADIUS, STONE_MAX_RADIUS),
            speed=random.uniform(STONE_MIN_SPEED, STONE_MAX_SPEED),
        )
    )


# --- Drawing ---

def draw_game(screen, font, player, stones, score, mode, game_over):
    import pygame

    # Dark background
    screen.fill((18, 22, 30))

    # Subtle grid lines (visual only — the AI does not use pixel data)
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, (25, 31, 42), (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, (25, 31, 42), (0, y), (WIDTH, y), 1)

    # Draw player as a blue rectangle with a lighter border
    pygame.draw.rect(screen, (95, 180, 255), player.rect, border_radius=4)
    pygame.draw.rect(screen, (178, 225, 255), player.rect, 2, border_radius=4)

    # Draw each stone as a red circle with a small highlight dot
    for stone in stones:
        pygame.draw.circle(screen, (220, 90, 80), (int(stone.x), int(stone.y)), stone.radius)
        pygame.draw.circle(screen, (255, 170, 130), (int(stone.x - 4), int(stone.y - 5)), max(3, stone.radius // 4))

    # HUD: current mode and score
    text = font.render(f"Mode: {mode}   Score: {score}", True, (235, 240, 245))
    screen.blit(text, (16, 14))

    # Controls hint
    if mode == "human":
        help_text = "A/D or arrows = move | Q = quit | data is logged while you play"
    elif mode == "ai":
        help_text = "AI controls the player | Space = restart | Q = quit"
    else:
        help_text = "Heuristic demo | Space = restart | Q = quit"
    screen.blit(font.render(help_text, True, (180, 190, 200)), (16, 38))

    # Game-over overlay
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 145))
        screen.blit(overlay, (0, 0))
        title = font.render("Game Over", True, (255, 235, 235))
        sub = font.render("Press Space to restart or Q to quit", True, (245, 245, 245))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 28))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 8))


# --- Main game loop ---

def run_game(args):
    import pygame

    # Initialise pygame and create the window
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Practicum 4 - AI Stone Dodger")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    # Only create a logger in human mode (we only want to record human gameplay)
    logger = TrainingLogger(args.record) if args.mode == "human" else None
    model = None
    feature_columns = FEATURE_COLUMNS
    if args.mode == "ai":
        # Load the trained model and its expected feature column order
        model, feature_columns = load_ai(args.model)

    def reset():
        # Return a fresh game state: new player, empty stone list, score 0
        return Player(), [], 0, 0.0, False

    player, stones, score, spawn_timer, game_over = reset()
    running = True

    try:
        while running:
            # dt = time in seconds since the last frame (keeps physics frame-rate independent)
            dt = clock.tick(FPS) / 1000

            # Handle window close and key events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    if event.key == pygame.K_SPACE and game_over:
                        player, stones, score, spawn_timer, game_over = reset()

            keys = pygame.key.get_pressed()
            # Build the feature vector for this frame (used by AI and logger)
            features = extract_features(player, stones)

            # Decide the action for this frame based on the active mode
            if game_over:
                action = 0  # freeze on game over
            elif args.mode == "human":
                action = human_action(keys)
            elif args.mode == "ai":
                action = ai_action(model, feature_columns, features)
            else:
                action = heuristic_action(player, stones)

            if not game_over:
                # Move the player
                player.move(action, dt)

                # Save this frame to the training CSV (human mode only)
                if logger is not None:
                    logger.write(score, features, action)

                # Spawn a new stone when the timer expires
                spawn_timer += dt
                if spawn_timer >= SPAWN_SECONDS:
                    spawn_timer = 0
                    spawn_stone(stones)

                # Move all stones downward
                for stone in stones:
                    stone.update(dt)

                # Remove stones that have left the screen and add their count to the score
                before = len(stones)
                stones = [stone for stone in stones if stone.y - stone.radius <= HEIGHT]
                score += before - len(stones)

                # Check if any remaining stone collides with the player
                for stone in stones:
                    if player.rect.colliderect(stone.rect):
                        game_over = True
                        break

            # Render everything and push to the display
            draw_game(screen, font, player, stones, score, args.mode, game_over)
            pygame.display.flip()
    finally:
        # Always close the logger and quit pygame cleanly, even on error
        if logger is not None:
            logger.close()
        pygame.quit()


# --- CLI argument parsing ---

def parse_args():
    parser = argparse.ArgumentParser(description="AI Stone Dodger - Practicum 4")
    parser.add_argument(
        "--mode",
        choices=["human", "ai", "heuristic"],
        default="human",
        help="human records training data, ai uses a trained model, heuristic is a simple rule-based demo",
    )
    # Default paths are relative to the script so data always lands in the right folder
    parser.add_argument("--record", default=str(SCRIPT_DIR / "data" / "training_data.csv"), help="CSV file for human training data")
    parser.add_argument("--model", default=str(SCRIPT_DIR / "models" / "best_model.joblib"), help="Trained model for AI mode")
    return parser.parse_args()


if __name__ == "__main__":
    run_game(parse_args())
