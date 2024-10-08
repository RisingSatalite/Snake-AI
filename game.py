import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)
#font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 20
SPEED = 40

class SnakeGameAI:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()


    def reset(self):
        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0


    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()


    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move
        self._move(action) # update the head
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_self_collison():
            game_over = True
            reward = -30
            return reward, game_over, self.score
        
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            if(len(self.snake) == 3):
                #penalty for sucide stragies
                game_over = True
                reward = -20
                return reward, game_over, self.score

            game_over = True
            reward = -10
            return reward, game_over, self.score

        # Amplify reward if eating food and not taking it about if about to eat
        if self.is_anywhere_near_food_2(2):
            reward = reward + 10
        elif self.is_anywhere_near_food():
            reward = reward + 5
        elif self.is_anywhere_near_food_2(10):
            reward = reward + 2

        if(self.is_near_wall()):
            reward -= 1
        #penatly for head being close to tail
        #if (self.is_near_tail()):
            #if(3 != len(self.snake)):
                #reward = reward - 3

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 60 # Increased from intial
            self._place_food()
        else:
            self.snake.pop()
        
        #if self.is_near_tail():
            #reward = reward - 5

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, self.score


    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False
    
    def is_self_collison(self, pt=None):
        # hits itself
        if pt is None:
            pt = self.head
        if pt in self.snake[1:]:
            return True
        
        return False
    
    def is_near_tail(self, pt=None):
        if pt is None:
            pt = self.head
        tail = self.snake[-1]
        if ((pt.x == tail.x + BLOCK_SIZE) or (pt.x == tail.x - BLOCK_SIZE) or (pt.x == tail.x)) and \
            ((pt.y == tail.y + BLOCK_SIZE) or (pt.y == tail.y - BLOCK_SIZE) or (pt.y == tail.y)):
            return True
        return False
    
    def is_near_wall(self, distance=BLOCK_SIZE):
        # Check proximity to left wall
        if self.head.x <= distance:
            return True
        # Check proximity to right wall
        if self.head.x >= (self.w - distance):
            return True
        # Check proximity to top wall
        if self.head.y <= distance:
            return True
        # Check proximity to bottom wall
        if self.head.y >= (self.h - distance):
            return True
        return False


    def is_near_food(self, pt=None):
        if pt is None:
            pt = self.head
        food = self.food
        if ((pt.x == food.x + BLOCK_SIZE) or (pt.x == food.x - BLOCK_SIZE) or (pt.x == food.x)) and \
            ((pt.y == food.y + BLOCK_SIZE) or (pt.y == food.y - BLOCK_SIZE) or (pt.y == food.y)):
            return True
        return False
    
    def is_near_food_2(self, lenght, pt=None):
        if pt is None:
            pt = self.head
        food = self.food
        true_lenght = BLOCK_SIZE * lenght
        if ((pt.x == food.x + true_lenght) or (pt.x == food.x - true_lenght) or (pt.x == food.x)) and \
            ((pt.y == food.y + true_lenght) or (pt.y == food.y - true_lenght) or (pt.y == food.y)):
            return True
        return False

    def is_anywhere_near_food(self, pt=None):
        if pt is None:
            pt = self.head
        food = self.food
        distance = ((pt.x - food.x) ** 2 + (pt.y - food.y) ** 2) ** 0.5
        return distance <= (3*BLOCK_SIZE)
    
    def is_anywhere_near_food_2(self, lenght, pt=None):
        if pt is None:
            pt = self.head
        food = self.food
        distance = ((pt.x - food.x) ** 2 + (pt.y - food.y) ** 2) ** 0.5
        return distance <= (lenght*BLOCK_SIZE)

    def _update_ui(self):
        self.display.fill(BLACK)

        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()


    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)