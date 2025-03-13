import pygame
import random
import math
import csv
import numpy as np
from datetime import datetime

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

# CONSTANTS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 64, 64)
GREEN = (64, 255, 64)
BLUE = (64, 64, 255)

LIVE_STATS_DISPLAY = True
NUM_OFFSPRINGS = 0
NUM_MUTATIONS = 0
statistics_log = []  # List to store simulation statistics over time

#TODO Eventually make config dicts into jsons that i can extract from

# START CONFIG
SIMULATION_START_CONFIG = {
    "N_STARTING_BLOB": 10,
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
        "excess_energy_required": 300, # Extra energy required on top of required_energy for blob to reproduce. Ensures Blob doesn't immediately die after reproduction.
        "mutation_chance": 0.05, # Will use base std_devs from base stat as the std_devs for the normal distribution
        "offspring_amount": {
            "mean": 1,
            "std_dev": 0.5,
            "min": 1,
            "max": 3
        }
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
        "min": 3,
        "max": 7
    },
    "FOOD_ENERGY_TO_SIZE_MULTIPLIER": 6, # Energy food gives is calculated by area. after area calculation, this multiplier is applied to result as final energy value of food
    "FOOD_SPAWN_CHANCE_PER_FRAME": 0.6
}

# ENVIRONMENT CONFIG
ENVIRONMENT_CONFIG = {
    None
    #TODO
}
    
FPS = 120

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
    while not (min <= generated_stat <= max):
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

def mutate_attribute(value, attribute_dict):
    """
    Applies mutation to an attribute based on a probability.
    If mutation occurs, generates a new value within the defined range.
    """
    global NUM_MUTATIONS
    if random.random() < BLOB_CONFIG["BLOB_REPRODUCTION"]["mutation_chance"]:
        NUM_MUTATIONS += 1
        return generate_normal_stat_with_dict(attribute_dict)
    return value

def generate_blob(custom_blob_config=BLOB_CONFIG, parent_blob=None):
    """
    Generates a new Blob. If a parent_blob is provided, it inherits traits with possible mutations.
    """
    blob_size = generate_normal_stat_with_dict(custom_blob_config["BLOB_SIZE"])
    
    if parent_blob:
        # Copy attributes from parent and apply mutations
        offspring_attributes = {
            "size": mutate_attribute(parent_blob.size, BLOB_CONFIG["BLOB_SIZE"]),
            "speed": mutate_attribute(parent_blob.speed, BLOB_CONFIG["BLOB_SPEED"]),
            "required_reproduction_energy": mutate_attribute(parent_blob.required_reproduction_energy, 
                                                             BLOB_CONFIG["BLOB_REPRODUCTION"]["required_energy"]),
            "offspring_amount": mutate_attribute(parent_blob.offspring_amount, BLOB_CONFIG["BLOB_REPRODUCTION"]["offspring_amount"]),
            "energy": BLOB_CONFIG["BLOB_START_ENERGY"]["mean"],  # Reset energy for new blobs
        }
        
    else:
        # Normal new blob generation
        offspring_attributes = {
            "size": blob_size,
            "speed": generate_normal_stat_with_dict(custom_blob_config["BLOB_SPEED"]),
            "required_reproduction_energy": generate_normal_stat_with_dict(custom_blob_config["BLOB_REPRODUCTION"]["required_energy"]),
            "offspring_amount": generate_normal_stat_with_dict(custom_blob_config["BLOB_REPRODUCTION"]["offspring_amount"]),
            "energy": generate_normal_stat_with_dict(custom_blob_config["BLOB_START_ENERGY"])
        }

    return Blob(
        blob_id_tracker.issue_id(),
        random.choice(custom_blob_config["BLOB_COLORS"]),
        random.randint(blob_size, SCREEN_WIDTH - blob_size),
        random.randint(blob_size, SCREEN_HEIGHT - blob_size),
        offspring_attributes["required_reproduction_energy"],
        offspring_attributes["offspring_amount"],
        offspring_attributes["size"],
        offspring_attributes["speed"],
        offspring_attributes["energy"]
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

def average_attribute(entities, attribute):
    return sum(getattr(obj, attribute) for obj in entities) / len(entities) if entities else 0

def max_attribute(entities, attribute):
    return max(getattr(obj, attribute) for obj in entities) if entities else None

def min_attribute(entities, attribute):
    return min(getattr(obj, attribute) for obj in entities) if entities else None

def render_dict_as_text(surface, stats_dict, font, color, x, y, line_spacing=5, rounding=1):
    """Render a dictionary as text on the pygame screen."""
    
    y_offset = 0
    
    for key, value in stats_dict.items():
        stat_text = f"{key}: {round(value, rounding)}"
        text_surface = font.render(stat_text, True, color)
        surface.blit(text_surface, (x + 10, y + y_offset))
        y_offset += font.get_height() + line_spacing
            
def save_statistics_to_csv():
    """Saves the logged simulation statistics to a CSV file."""
    filename = f"data/simulation_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=statistics_log[0].keys())
        writer.writeheader()
        writer.writerows(statistics_log)
    print(f"Simulation statistics saved to {filename}")
        
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
    def __init__(self, id, color, x, y, required_reproduction_energy, offspring_amount, size, speed, energy):
        self.id = id
        self.color = color
        self.x = x
        self.y = y
        self.required_reproduction_energy = required_reproduction_energy
        self.offspring_amount = offspring_amount
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
        """
        Handles reproduction by generating offspring blobs with possible mutations.
        The parent blob loses the required reproduction energy.
        """
        self.energy -= self.required_reproduction_energy
        
        global NUM_OFFSPRINGS

        offspring_list = []
        for _ in range(self.offspring_amount):
            NUM_OFFSPRINGS += 1
            offspring_list.append(generate_blob(parent_blob=self))

        return offspring_list

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
        
    frame_count = 0
    
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)

        # CHANCE OF FOOD SPAWNING
        if random.random() < FOOD_CONFIG["FOOD_SPAWN_CHANCE_PER_FRAME"]:
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
            
            elif blob.energy >= blob.required_reproduction_energy + BLOB_CONFIG["BLOB_REPRODUCTION"]["excess_energy_required"]:
                offspring = blob.reproduce()
                blobs.extend(offspring)
                
            # blob.print_stats(show_actions=False)
            blob.draw()

        # TODO Add logic to store each game state for data purposes (time-based game state data so we can analyze trends over time and stuff)
            # Should be a DF containing each Blob's attributes (diffrentiated by its id attribute) as well as the time (aka generation/day) of that data snapshot
            
        statistics = {
            "frame": frame_count,
            "blob_count": len(blobs),
            "blob_avg_speed": average_attribute(blobs, "speed"),
            "blob_min_speed": min_attribute(blobs, "speed"),
            "blob_max_speed": max_attribute(blobs, "speed"),
            "blob_avg_size": average_attribute(blobs, "size"),
            "blob_min_size": min_attribute(blobs, "size"),
            "blob_max_size": max_attribute(blobs, "size"),
            "blob_avg_energy": average_attribute(blobs, "energy"),
            "blob_min_energy": min_attribute(blobs, "energy"),
            "blob_max_energy": max_attribute(blobs, "energy"),
            "food_count": len(foods),
            "num_offsprings": NUM_OFFSPRINGS,
            "num_mutations": NUM_MUTATIONS
        }

        statistics_log.append(statistics)

        if LIVE_STATS_DISPLAY:
            render_dict_as_text(screen, statistics, font, WHITE, 0, 350)
    
        pygame.display.flip()
        clock.tick(FPS)
        frame_count += 1

    pygame.quit()
    save_statistics_to_csv()  # Save data when exiting

main()