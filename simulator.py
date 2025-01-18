import pygame
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# CONSTANTS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Blob:
    def __init__(self):
        # attributes per blob
        pass
        
    def search_for_food(self):
        # find nearest food
        # move closer to it
        # check if touching food (collision detection)
            # if touching food, consume food and adjust hunger accordingly

        pass

    def draw(self):
        # draw circle
        pass

def main():
    blobs = []
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