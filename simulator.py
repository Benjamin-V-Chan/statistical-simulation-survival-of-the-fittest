import string
import pygame
import random
import numpy as np

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# CONSTANTS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 64, 64)
GREEN = (64, 255, 64)
BLUE = (64, 64, 255)

N_STARTING_BLOBS = 30

STARTING_BLOB_IDS = list(string.ascii_letters) + list(string.digits)

DEFAULT_BLOB_COLOR = RED
DEFAULT_BLOB_SIZE = 15 # REFERS TO RADIUS
DEFAULT_BLOB_SPEED = 10
DEFAULT_BLOB_HUNGER = 100

N_STARTING_FOODS = 10

class Food:
    # TODO Create Food Class
        # Should have x, y, size, color, and potentially id attributes
    pass


class Blob:
    def __init__(self, id, color, x, y, size, speed, hunger):
        self.id = id
        self.color = color
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.hunger = hunger # 1-100, decreases a bit every day. If reaches 0, blob dies

    def food_action(self, foods):

        closest_food = find_closest_obj(self, foods) # Find closest food obj out of list of food objects

        if collision(self, closest_food):
            # means we are touching food
            # consume food and adjust hunger accordingly
            pass

        else:
            angle = find_angle(self.x, self.y, closest_food.x, closest_food.y)
            # iteratively check each food cord
                # use pythagoreom theorem to calculate distance
                # find lowest distance
            # move closer to it by using angles/slope
            # check if touching food (collision detection)
                # if touching food, consume food and adjust hunger accordingly

        pass

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

def main():
    if N_STARTING_BLOBS > len(STARTING_BLOB_IDS):
        print(f"[ERROR] INSUFFICIENT NUMBER OF STARTING IDS TO HANDLE NUMBER OF STARTING BLOBS AMOUNT. MUST BE BELOW {len(STARTING_BLOB_IDS)}")
        return

    blobs = []
    for i in range(N_STARTING_BLOBS):
        
        blob_id = STARTING_BLOB_IDS[i]
        blob = Blob(blob_id, RED, 
        random.randint(DEFAULT_BLOB_SIZE, SCREEN_WIDTH - DEFAULT_BLOB_SIZE), 
        random.randint(DEFAULT_BLOB_SIZE, SCREEN_HEIGHT - DEFAULT_BLOB_SIZE),
        DEFAULT_BLOB_SIZE,
        DEFAULT_BLOB_SPEED,
        10)

        blobs.append(blob)

    # will remain static food elements for now. will change over time
    foods = []
    for _ in range(N_STARTING_FOODS):

        # TODO Food class generation logic

        pass

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)

        random.shuffle(blobs) # Shuffle to ensure fairness and equal chance for best order
        for blob in blobs:
            blob.draw()

        pygame.display.flip()

    pygame.quit()

main()