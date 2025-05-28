import pygame
import random

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 200

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Tetrimino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # J
    [[1, 1, 1], [0, 0, 1]],  # L
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, BLUE, ORANGE, GREEN, RED]

class Tetrimino:
    def __init__(self):
        self.shape_idx = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_idx]
        self.color = SHAPE_COLORS[self.shape_idx]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0
        
    def rotate(self):
        # Rotate the shape 90 degrees clockwise
        rows = len(self.shape)
        cols = len(self.shape[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        
        for r in range(rows):
            for c in range(cols):
                rotated[c][rows - 1 - r] = self.shape[r][c]
                
        return rotated

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.big_font = pygame.font.SysFont('Arial', 48)
        
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetrimino()
        self.next_piece = Tetrimino()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5  # seconds
        self.fall_time = 0
        
    def draw_grid(self):
        # Draw the game grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, GRAY, 
                                [x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE], 1)
                if self.grid[y][x] > 0:
                    pygame.draw.rect(self.screen, SHAPE_COLORS[self.grid[y][x] - 1],
                                    [x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE])
    
    def draw_piece(self, piece, offset_x=0, offset_y=0):
        # Draw the current or next piece
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, piece.color,
                                    [(piece.x + x + offset_x) * GRID_SIZE,
                                     (piece.y + y + offset_y) * GRID_SIZE,
                                     GRID_SIZE, GRID_SIZE])
                    pygame.draw.rect(self.screen, WHITE,
                                    [(piece.x + x + offset_x) * GRID_SIZE,
                                     (piece.y + y + offset_y) * GRID_SIZE,
                                     GRID_SIZE, GRID_SIZE], 1)
    
    def draw_sidebar(self):
        # Draw the sidebar with score, level, next piece, etc.
        pygame.draw.rect(self.screen, BLACK, [GRID_WIDTH * GRID_SIZE, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT])
        
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, [GRID_WIDTH * GRID_SIZE + 20, 20])
        
        # Level
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, [GRID_WIDTH * GRID_SIZE + 20, 60])
        
        # Lines
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, [GRID_WIDTH * GRID_SIZE + 20, 100])
        
        # Next piece
        next_text = self.font.render("Next:", True, WHITE)
        self.screen.blit(next_text, [GRID_WIDTH * GRID_SIZE + 20, 140])
        
        # Draw next piece preview (centered in the sidebar)
        next_x = GRID_WIDTH + (SIDEBAR_WIDTH // 2) // GRID_SIZE - len(self.next_piece.shape[0]) // 2
        self.draw_piece(self.next_piece, next_x, 6)
    
    def draw_game_over(self):
        # Draw game over screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.big_font.render("GAME OVER", True, WHITE)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(game_over_text, text_rect)
        
        restart_text = self.font.render("Press R to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        self.screen.blit(restart_text, restart_rect)
    
    def valid_position(self, piece, x_offset=0, y_offset=0):
        # Check if piece is in valid position
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + x_offset
                    new_y = piece.y + y + y_offset
                    
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or 
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return False
        return True
    
    def lock_piece(self):
        # Lock the current piece in place
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.shape_idx + 1
        
        # Check for completed lines
        self.clear_lines()
        
        # Get next piece
        self.current_piece = self.next_piece
        self.next_piece = Tetrimino()
        
        # Check if game over
        if not self.valid_position(self.current_piece):
            self.game_over = True
    
    def clear_lines(self):
        # Clear completed lines and calculate score
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                lines_to_clear.append(y)
        
        # Score calculation
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += (len(lines_to_clear) ** 2) * 100 * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)
            
            # Remove lines and move above lines down
            for line in sorted(lines_to_clear):
                for y in range(line, 0, -1):
                    self.grid[y] = self.grid[y-1][:]
                self.grid[0] = [0 for _ in range(GRID_WIDTH)]
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if not self.game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if self.valid_position(self.current_piece, -1):
                            self.current_piece.x -= 1
                    elif event.key == pygame.K_RIGHT:
                        if self.valid_position(self.current_piece, 1):
                            self.current_piece.x += 1
                    elif event.key == pygame.K_DOWN:
                        if self.valid_position(self.current_piece, 0, 1):
                            self.current_piece.y += 1
                    elif event.key == pygame.K_UP:
                        rotated = self.current_piece.rotate()
                        old_shape = self.current_piece.shape
                        self.current_piece.shape = rotated
                        if not self.valid_position(self.current_piece):
                            self.current_piece.shape = old_shape
                    elif event.key == pygame.K_SPACE:
                        # Hard drop
                        while self.valid_position(self.current_piece, 0, 1):
                            self.current_piece.y += 1
                            self.score += 2  # Small bonus for hard drop
                        self.lock_piece()
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.__init__()  # Restart game
        
        return True
    
    def update(self, dt):
        if self.game_over:
            return
        
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if self.valid_position(self.current_piece, 0, 1):
                self.current_piece.y += 1
            else:
                self.lock_piece()
    
    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()
        self.draw_piece(self.current_piece)
        self.draw_sidebar()
        
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def run(self):
        running = True
        last_time = pygame.time.get_ticks()
        
        while running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0  # Convert to seconds
            last_time = current_time
            
            running = self.handle_events()
            self.update(dt)
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()