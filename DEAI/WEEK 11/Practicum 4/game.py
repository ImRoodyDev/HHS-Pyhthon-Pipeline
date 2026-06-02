import argparse
import csv
import math
import random
import time
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


WIDTH = 640
HEIGHT = 480
FPS = 60

PLAYER_WIDTH = 44
PLAYER_HEIGHT = 30
PLAYER_Y = HEIGHT - 58
PLAYER_SPEED = 360

STONE_MIN_RADIUS = 14
STONE_MAX_RADIUS = 24
STONE_MIN_SPEED = 170
STONE_MAX_SPEED = 285
SPAWN_SECONDS = 0.55

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

CSV_COLUMNS = [
    "timestamp",
    "score",
    *FEATURE_COLUMNS,
    "action",
]


@dataclass
class Player:
    x: float = WIDTH / 2
    velocity: float = 0

    @property
    def rect(self):
        import pygame

        return pygame.Rect(
            int(self.x - PLAYER_WIDTH / 2),
            PLAYER_Y,
            PLAYER_WIDTH,
            PLAYER_HEIGHT,
        )

    def move(self, action, dt):
        self.velocity = action * PLAYER_SPEED
        self.x += self.velocity * dt
        min_x = PLAYER_WIDTH / 2
        max_x = WIDTH - PLAYER_WIDTH / 2
        self.x = max(min_x, min(max_x, self.x))


@dataclass
class Stone:
    x: float
    y: float
    radius: int
    speed: float

    @property
    def rect(self):
        import pygame

        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def update(self, dt):
        self.y += self.speed * dt


class TrainingLogger:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = self.path.open("a", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.file, fieldnames=CSV_COLUMNS)

        if self.path.stat().st_size == 0:
            self.writer.writeheader()

    def write(self, score, features, action):
        row = {
            "timestamp": time.time(),
            "score": score,
            **features,
            "action": action,
        }
        self.writer.writerow(row)

    def close(self):
        self.file.close()


def normalize(value, minimum, maximum):
    return (value - minimum) / (maximum - minimum)


def nearest_dangerous_stone(player, stones):
    candidates = [stone for stone in stones if stone.y + stone.radius < PLAYER_Y + 80]
    if not candidates:
        return None

    return min(candidates, key=lambda stone: abs((PLAYER_Y - stone.y) / max(stone.speed, 1)))


def danger_for_action(player_x, stone, action):
    future_player_x = player_x + action * PLAYER_SPEED * 0.28
    future_player_x = max(PLAYER_WIDTH / 2, min(WIDTH - PLAYER_WIDTH / 2, future_player_x))
    horizontal_gap = abs(future_player_x - stone.x)
    close_to_player = stone.y > HEIGHT * 0.42
    return int(close_to_player and horizontal_gap < (PLAYER_WIDTH / 2 + stone.radius + 10))


def extract_features(player, stones):
    stone = nearest_dangerous_stone(player, stones)

    if stone is None:
        stone_x = WIDTH / 2
        stone_y = 0
        stone_speed = STONE_MIN_SPEED
        dx = 0
        danger_left = 0
        danger_center = 0
        danger_right = 0
    else:
        stone_x = stone.x
        stone_y = stone.y
        stone_speed = stone.speed
        dx = stone.x - player.x
        danger_left = danger_for_action(player.x, stone, -1)
        danger_center = danger_for_action(player.x, stone, 0)
        danger_right = danger_for_action(player.x, stone, 1)

    features = {
        "player_x_norm": normalize(player.x, 0, WIDTH),
        "player_velocity_norm": player.velocity / PLAYER_SPEED,
        "stone_x_norm": normalize(stone_x, 0, WIDTH),
        "stone_y_norm": normalize(stone_y, 0, HEIGHT),
        "stone_speed_norm": normalize(stone_speed, STONE_MIN_SPEED, STONE_MAX_SPEED),
        "dx_norm": dx / WIDTH,
        "abs_dx_norm": abs(dx) / WIDTH,
        "danger_left": danger_left,
        "danger_center": danger_center,
        "danger_right": danger_right,
    }

    return features


def human_action(keys):
    import pygame

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        return -1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        return 1
    return 0


def heuristic_action(player, stones):
    stone = nearest_dangerous_stone(player, stones)
    if stone is None or stone.y < HEIGHT * 0.35:
        return 0

    if abs(stone.x - player.x) > PLAYER_WIDTH:
        return 0

    if player.x < WIDTH / 2:
        return -1
    return 1


def load_ai(path):
    import joblib

    bundle = joblib.load(path)
    if isinstance(bundle, dict):
        return bundle["model"], bundle.get("feature_columns", FEATURE_COLUMNS)
    return bundle, FEATURE_COLUMNS


def ai_action(model, feature_columns, features):
    values = [[features[column] for column in feature_columns]]
    prediction = model.predict(values)[0]
    return int(prediction)


def spawn_stone(stones):
    stones.append(
        Stone(
            x=random.randint(STONE_MAX_RADIUS, WIDTH - STONE_MAX_RADIUS),
            y=-STONE_MAX_RADIUS,
            radius=random.randint(STONE_MIN_RADIUS, STONE_MAX_RADIUS),
            speed=random.uniform(STONE_MIN_SPEED, STONE_MAX_SPEED),
        )
    )


def draw_game(screen, font, player, stones, score, mode, game_over):
    import pygame

    screen.fill((18, 22, 30))

    # Low-cost visual layer: pretty enough, but the AI uses the simple state vector.
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, (25, 31, 42), (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, (25, 31, 42), (0, y), (WIDTH, y), 1)

    pygame.draw.rect(screen, (95, 180, 255), player.rect, border_radius=4)
    pygame.draw.rect(screen, (178, 225, 255), player.rect, 2, border_radius=4)

    for stone in stones:
        pygame.draw.circle(screen, (220, 90, 80), (int(stone.x), int(stone.y)), stone.radius)
        pygame.draw.circle(screen, (255, 170, 130), (int(stone.x - 4), int(stone.y - 5)), max(3, stone.radius // 4))

    text = font.render(f"Mode: {mode}   Score: {score}", True, (235, 240, 245))
    screen.blit(text, (16, 14))

    if mode == "human":
        help_text = "A/D or arrows = move | Q = quit | data is logged while you play"
    elif mode == "ai":
        help_text = "AI controls the player | Space = restart | Q = quit"
    else:
        help_text = "Heuristic demo | Space = restart | Q = quit"
    screen.blit(font.render(help_text, True, (180, 190, 200)), (16, 38))

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 145))
        screen.blit(overlay, (0, 0))
        title = font.render("Game Over", True, (255, 235, 235))
        sub = font.render("Press Space to restart or Q to quit", True, (245, 245, 245))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 28))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 8))


def run_game(args):
    import pygame

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Practicum 4 - AI Stone Dodger")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    logger = TrainingLogger(args.record) if args.mode == "human" else None
    model = None
    feature_columns = FEATURE_COLUMNS
    if args.mode == "ai":
        model, feature_columns = load_ai(args.model)

    def reset():
        return Player(), [], 0, 0.0, False

    player, stones, score, spawn_timer, game_over = reset()
    running = True

    try:
        while running:
            dt = clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    if event.key == pygame.K_SPACE and game_over:
                        player, stones, score, spawn_timer, game_over = reset()

            keys = pygame.key.get_pressed()
            features = extract_features(player, stones)

            if game_over:
                action = 0
            elif args.mode == "human":
                action = human_action(keys)
            elif args.mode == "ai":
                action = ai_action(model, feature_columns, features)
            else:
                action = heuristic_action(player, stones)

            if not game_over:
                player.move(action, dt)
                if logger is not None:
                    logger.write(score, features, action)

                spawn_timer += dt
                if spawn_timer >= SPAWN_SECONDS:
                    spawn_timer = 0
                    spawn_stone(stones)

                for stone in stones:
                    stone.update(dt)

                before = len(stones)
                stones = [stone for stone in stones if stone.y - stone.radius <= HEIGHT]
                score += before - len(stones)

                for stone in stones:
                    if player.rect.colliderect(stone.rect):
                        game_over = True
                        break

            draw_game(screen, font, player, stones, score, args.mode, game_over)
            pygame.display.flip()
    finally:
        if logger is not None:
            logger.close()
        pygame.quit()


def parse_args():
    parser = argparse.ArgumentParser(description="AI Stone Dodger - Practicum 4")
    parser.add_argument(
        "--mode",
        choices=["human", "ai", "heuristic"],
        default="human",
        help="human records training data, ai uses a trained model, heuristic is a simple rule-based demo",
    )
    parser.add_argument("--record", default=str(SCRIPT_DIR / "data" / "training_data.csv"), help="CSV file for human training data")
    parser.add_argument("--model", default=str(SCRIPT_DIR / "models" / "best_model.joblib"), help="Trained model for AI mode")
    return parser.parse_args()


if __name__ == "__main__":
    run_game(parse_args())
