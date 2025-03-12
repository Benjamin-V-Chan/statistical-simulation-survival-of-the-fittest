import pygame
import random
import math
import numpy as np
from datetime import datetime

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# CONSTANTS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 64, 64)
GREEN = (64, 255, 64)
BLUE = (64, 64, 255)

#TODO Eventually make config dicts into jsons that i can extract from

# START CONFIG
SIMULATION_START_CONFIG = {
    "N_STARTING_BLOB": 30,
    "N_STARTING_FOOD": 50
}

# BLOB CONFIG
BLOB_CONFIG = {
    "BLOB_COLORS": [BLUE],
    "BLOB_MUTATION_CHANCE": 0.1,
    "BLOB_REPRODUCTION": {
        "required_energy": {
            "mean": 5000,
            "std_dev": 150,
            "min": 4500,
            "max": 5500
        },
        "mutation_chance": 0.1, # Will use base std_devs from base stat as the std_devs for the normal distribution
    },
    "BLOB_SIZE": {
        "mean": 20,
        "std_dev": 3,
        "min": 10,
        "max": 30
    },
    "BLOB_SPEED": {
        "mean": 2,
        "std_dev": 1,
        "min": 1,
        "max": 3
    },
    "BLOB_START_ENERGY": {
        "mean": 3000,
        "std_dev": 200,
        "min": 2000,
        "max": 4000
    }
}

# FOOD CONFIG
FOOD_CONFIG = {
    "FOOD_COLORS": [RED],
    "FOOD_SIZE": {
        "mean": 5,
        "std_dev": 1,
        "min": 1,
        "max": 10
    },
    "FOOD_ENERGY_TO_SIZE_MULTIPLIER": 6, # Energy food gives is calculated by area. after area calculation, this multiplier is applied to result as final energy value of food
    "FOOD_SPAWN_PER_FRAME_PROBABILITY_DENOMINATOR": 3
}

# ENVIRONMENT CONFIG
ENVIRONMENT_CONFIG = {
    None
    #TODO
}
    
FPS = 30

# Track all existing foods and blobs
foods = []
blobs = []


# HELPER FUNCTIONS

def get_radius_endpoint(x, y, radius, theta):
    '''Returns coordinates (x, y) of radius endpoint of a circle, based off center point cords (x, y), the radius distance, and theta (angle, in radians)'''
    return (x + radius * math.cos(theta), y + radius * math.sin(theta))

def get_distance(x1, y1, x2, y2):
    '''Returns distance between two sets of (x, y) coordinates'''
    return math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))

def get_theta(x1, y1, x2, y2): 
    '''Returns theta (in radians) that (x1, y1) needs to direct itself to point towards (x2, y2)'''
    return math.atan2(y2 - y1, x2 - x1)

def find_closest_obj(obj_a, list_of_objects):
    '''Returns closest obj to obj_a from a list of objs in list_of_objects, assuming all objs have x and y attributes'''
    
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

def collision(obj_a, obj_b):
    '''Returns True if circle objects, obj_a and obj_b, collide with one another, assuming they both have x, y, and size (radius) attributes'''
    distance = get_distance(obj_a.x, obj_a.y, obj_b.x, obj_b.y)
    if distance <= obj_a.size + obj_b.size:
        return True
    return False

def calculate_circle_area(radius):
    '''Returns circle area in same units as radius is in'''
    return math.pi * (radius ** 2)

def generate_normal_stat(mean, std_dev, min, max):
    '''Returns a random statistic based off predetermined normal distribution parameters as well as min and max value boundaries'''
    generated_stat = np.random.normal(mean, std_dev)
    while not (min < generated_stat < max):
        generated_stat = np.random.normal(mean, std_dev)
    return int(generated_stat)

def generate_normal_stat_with_dict(stat_dict):
    '''Returns a random statistic based off predetermined normal distribution parameters from a config dictionary. Config dictionary must have 'mean', 'std_dev', 'min', and 'max' keys.'''
    return generate_normal_stat(
        stat_dict['mean'],
        stat_dict['std_dev'],
        stat_dict['min'],
        stat_dict['max']
    )

def generate_blob(custom_blob_config=BLOB_CONFIG):
    '''Returns a Blob object of Class Blob based off (optional) dictionary config (else, defaults to global config, BLOB_CONFIG)'''

    blob_size = generate_normal_stat_with_dict(custom_blob_config["BLOB_SIZE"])
    
    return Blob(
        blob_id_tracker.issue_id(),
        random.choice(custom_blob_config["BLOB_COLORS"]), 
        random.randint(blob_size, SCREEN_WIDTH - blob_size),
        random.randint(blob_size, SCREEN_HEIGHT - blob_size),
        blob_size,
        generate_normal_stat_with_dict(custom_blob_config["BLOB_SPEED"]),
        generate_normal_stat_with_dict(custom_blob_config["BLOB_START_ENERGY"])
        )

def generate_food(custom_food_config=FOOD_CONFIG):
    '''Returns a Food object of Class Food based off (optional) dictionary config (else, defaults to global config, FOOD_CONFIG)'''

    food_size = generate_normal_stat_with_dict(custom_food_config["FOOD_SIZE"])

    return Food(
        food_id_tracker.issue_id(), 
        random.choice(custom_food_config["FOOD_COLORS"]),
        random.randint(food_size, SCREEN_WIDTH - food_size), 
        random.randint(food_size, SCREEN_HEIGHT - food_size),
        food_size
        )

class IDTracker:
    def __init__(self):
        self.current_id = 0
        self.issued_ids = set()
        
    def issue_id(self):
        self.current_id += 1
        self.issued_ids.add(self.current_id)
        return self.current_id

food_id_tracker = IDTracker()
blob_id_tracker = IDTracker()

class Food:
    def __init__(self, id, color, x, y, size):
        self.id = id
        self.x = x
        self.y = y
        self.size = size
        self.color = color

        # energy_value calculation (just calculates area of food then scales down by 10 and rounds)
        self.energy_value = round(FOOD_CONFIG["FOOD_ENERGY_TO_SIZE_MULTIPLIER"] * math.pi * (size ** 2))

    def print_stats(self):
        print(f'''

        ====== FOOD STATS ======
        id: {self.id}
        color: {self.color}
        x: {self.x}
        y: {self.y}
        size: {self.size}
        ========================

        ''')

    def retrieve_stats(self):
        return {
            'id': {self.id},
            'color': {self.color},
            'x': {self.x},
            'y': {self.y},
            'size': {self.size}
        }

    def __eq__(self, other):
        if isinstance(other, Food):
            return self.id == other.id
        return False

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

class Blob:
    def __init__(self, id, color, x, y, size, speed, energy):
        self.id = id
        self.color = color
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.energy = energy
        self.actions = []

    def food_action(self, foods):
        
        closest_food = find_closest_obj(self, foods) # Find closest food obj out of list of food objects

        if collision(self, closest_food): # WE ARE TOUCHING FOOD
            self.energy += closest_food.energy_value # consume food and get energy
            foods.remove(closest_food) # remove food from ecosystem

            self.actions.append("consume food")

        else: # WE ARE NOT TOUCHING FOOD
            theta = get_theta(self.x, self.y, closest_food.x, closest_food.y)
            self.move(theta)
            self.use_energy_for_movement()

    def move(self, theta):
        radius_endpoint_x, radius_endpoint_y = get_radius_endpoint(self.x, self.y, self.speed, theta)
        self.x = radius_endpoint_x
        self.y = radius_endpoint_y

        self.actions.append("move")

    def use_energy_for_movement(self):
        area_size = calculate_circle_area(self.size)

        # calculate energy use based off area_size * speed scaled down to 10 and rounded
        energy_used = round(area_size * self.speed / 200)
        self.energy -= energy_used
        self.actions.append("move energy")

    def use_constant_energy(self): # energy used constantly, no matter what
        area_size = calculate_circle_area(self.size)

        # calculate energy use based off area_size scaled down to 10 and rounded
        energy_used = round(area_size / 200)
        self.energy -= energy_used

        self.actions.append("constant energy")

    def reproduce(self):
        # duplicate blob
        # apply BLOB_CONFIG mutation chance
        # use generate normal stat to "reproduce" with a mutation
        # create new blob and append to main list
        
    def print_stats(self, show_actions=True):
        actions = "'show_actions' TURNED OFF"
        if show_actions:
            actions = self.actions

        print(f'''

        ====== BLOB STATS ======
        id: {self.id}
        color: {self.color}
        x: {self.x}
        y: {self.y}
        size: {self.size}
        speed: {self.speed}
        energy: {self.energy}
        actions: {actions}
        ========================

        ''')
        
    def retrieve_stats(self):
        return {
            'id': {self.id},
            'color': {self.color},
            'x': {self.x},
            'y': {self.y},
            'size': {self.size},
            'speed': {self.speed},
            'energy': {self.energy},
            'actions': {self.actions}
        }

    def __eq__(self, other):
        if isinstance(other, Blob):
            return self.id == other.id
        return False
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

def main():

    # will remain static food elements for now. will change over time
    for _ in range(SIMULATION_START_CONFIG["N_STARTING_FOOD"]): # Food Creation
        foods.append(generate_food())

    for _ in range(SIMULATION_START_CONFIG["N_STARTING_BLOB"]): # Blob Creation        
        blobs.append(generate_blob())
        
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)

        # CHANCE OF FOOD SPAWNING
        if random.randint(1, FOOD_CONFIG["FOOD_SPAWN_PER_FRAME_PROBABILITY_DENOMINATOR"]) == 1:
            foods.append(generate_food())

        for food in foods:
            food.draw()
        
        random.shuffle(blobs) # Shuffle to ensure fairness and equal chance for best order
        for blob in blobs:
            blob.use_constant_energy()
            blob.food_action(foods)
            if blob.energy <= 0: # Blob no longer has energy, so it will perish
                blobs.remove(blob)
                blob.color = WHITE # Change color to show it will die
            elif blob.energy >= blob.required_reproduction_energy:
                blob.reproduce()
            # blob.print_stats(show_actions=False)
            blob.draw()

        # TODO Add logic to store each game state for data purposes (time-based game state data so we can analyze trends over time and stuff)
            # Should be a DF containing each Blob's attributes (diffrentiated by its id attribute) as well as the time (aka generation/day) of that data snapshot
        
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()

main()