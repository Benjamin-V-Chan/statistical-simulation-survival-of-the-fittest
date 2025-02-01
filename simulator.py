import string
import pygame
import random
import math

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

N_STARTING_BLOBS = 1
STARTING_BLOB_IDS = list(string.ascii_letters) + list(string.digits)

DEFAULT_BLOB_COLOR = BLUE
DEFAULT_BLOB_SIZE = 10 # REFERS TO RADIUS
DEFAULT_BLOB_SPEED = 1
DEFAULT_BLOB_ENERGY = 100

N_STARTING_FOODS = 20
STARTING_FOOD_IDS = list(string.ascii_letters) + list(string.digits)

DEFAULT_FOOD_COLOR = RED
DEFAULT_FOOD_SIZE = 5 # REFERS TO RADIUS

FPS = 20
# HELPER FUNCTIONS

def get_radius_endpoint(x, y, radius, theta): # Finds cords (x, y) of radius endpoint of a circle, based off center point cords (x, y), the radius distance, and theta (angle, in radians)
    return (x + radius * math.cos(theta), y + radius * math.sin(theta))

def get_distance(x1, y1, x2, y2): # distance between both cords (x, y)
    return math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))

def get_theta(x1, y1, x2, y2): # find theta (in radians) that (x1, y1) needs to direct itself to point towards (x2, y2)
    return math.atan2(y2 - y1, x2 - x1)

def find_closest_obj(obj_a, list_of_objects): # obj_a and all objects within list_of_objects parameters are classes with x and y attributes
    
    if len(list_of_objects) <= 1:
        print("[WARNING] ONE OBJ LEFT: FIND_CLOSEST_OBJ")

    closest_obj = list_of_objects[0]
    closest_obj_distance = get_distance(obj_a.x, obj_a.y, closest_obj.x, closest_obj.y)

    for obj_b in list_of_objects[1:]: # avoid checking index 0 since that is already set for closest_obj
        distance = get_distance(obj_a.x, obj_a.y, obj_b.x, obj_b.y)
        if distance < closest_obj_distance: # new closest obj
            closest_obj_distance = distance
            closest_obj = obj_b

    return closest_obj

def collision(obj_a, obj_b): # Both parameters are classes with x, y, and size (radius) attributes
    distance = get_distance(obj_a.x, obj_a.y, obj_b.x, obj_b.y)
    if distance <= obj_a.size + obj_b.size:
        return True
    return False

def calculate_circle_area(radius):
    return math.pi * (radius ** 2)

class Food:
    def __init__(self, id, x, y, size, color):
        self.id = id
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

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

        if collision(self, closest_food): # WE ARE TOUCHING FOOD
            # means we are touching food
            # consume food and adjust hunger accordingly
            pass

        else: # WE ARE NOT TOUCHING FOOD
            theta = get_theta(self.x, self.y, closest_food.x, closest_food.y)
            self.move(theta, self.speed)

    def move(self, theta, speed):
        radius_endpoint_x, radius_endpoint_y = get_radius_endpoint(self.x, self.y, speed, theta)
        self.x += radius_endpoint_x
        self.y += radius_endpoint_y


    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

def main():
    if N_STARTING_BLOBS > len(STARTING_BLOB_IDS):
        print(f"[ERROR] INSUFFICIENT NUMBER OF STARTING IDS TO HANDLE NUMBER OF STARTING BLOBS AMOUNT. MUST BE BELOW {len(STARTING_BLOB_IDS)}")
        return

    blobs = []
    for i in range(N_STARTING_BLOBS):
        
        blob_id = STARTING_BLOB_IDS[i]
        blob = Blob(blob_id, 
                    DEFAULT_BLOB_COLOR, 
                    random.randint(DEFAULT_BLOB_SIZE, SCREEN_WIDTH - DEFAULT_BLOB_SIZE),
                    random.randint(DEFAULT_BLOB_SIZE, SCREEN_HEIGHT - DEFAULT_BLOB_SIZE),
                    DEFAULT_BLOB_SIZE,
                    DEFAULT_BLOB_SPEED,
                    10)

        blobs.append(blob)

    # will remain static food elements for now. will change over time
    foods = []
    for i in range(N_STARTING_FOODS):

        food_id = STARTING_FOOD_IDS[i]
        food = Food(food_id, 
                    DEFAULT_FOOD_COLOR, 
                    random.randint(DEFAULT_FOOD_SIZE, SCREEN_WIDTH - DEFAULT_FOOD_SIZE), 
                    random.randint(DEFAULT_FOOD_SIZE, SCREEN_HEIGHT - DEFAULT_FOOD_SIZE),
                    DEFAULT_FOOD_SIZE,
                    10)

        foods.append(food)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)

        for food in foods:
            food.draw()

        random.shuffle(blobs) # Shuffle to ensure fairness and equal chance for best order
        for blob in blobs:
            blob.draw()

        # TODO Add logic to store each game state for data purposes (time-based game state data so we can analyze trends over time and stuff)
            # Should be a DF containing each Blob's attributes (diffrentiated by its id attribute) as well as the time (aka generation/day) of that data snapshot
        
        pygame.display.flip()

    pygame.quit()

main()