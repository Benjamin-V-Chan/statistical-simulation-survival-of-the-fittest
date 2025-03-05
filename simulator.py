import string
import pygame
import random
import math

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

# BLOB CONFIG
BLOB_CONFIG = {
    "N_STARTING_BLOBS": 10,
    
}

# FOOD CONFIG


# ENVIRONMENT CONFIG
ENVIRONMENT_CONFIG = {
    
}


N_STARTING_BLOBS = 10
STARTING_BLOB_IDS = list(string.ascii_letters) + list(string.digits) + list(string.ascii_letters) + list(string.digits)

DEFAULT_BLOB_COLOR = BLUE
DEFAULT_BLOB_SIZE = 10 # REFERS TO RADIUS
DEFAULT_BLOB_SPEED = 1
DEFAULT_BLOB_ENERGY = 1000

N_STARTING_FOODS = 50
STARTING_FOOD_IDS = list(string.ascii_letters) + list(string.digits) + list(string.ascii_letters) + list(string.digits)

DEFAULT_FOOD_COLOR = RED
DEFAULT_FOOD_SIZE = 5 # REFERS TO RADIUS

DEFAULT_FOOD_MULTIPLIER = 4
ONE_OUT_OF_CHANCE_OF_FOOD_SPAWNING_PER_FRAME = 30

FPS = 30

# GLOBAL VARIABLES

# Track assigned IDs
used_food_ids = set()
used_blob_ids = set()

# Track all existing foods and blobs
foods = []
blobs = []


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

class IDTracker:
    def __init__(self):
        self.current_id = 0
        self.issued_ids = set()
        
    def issue_id(self):
        self.current_id += 1
        self.issued_ids.add(self.current_id)
        return self.current_id

class Food:
    def __init__(self, id, color, x, y, size):
        self.id = id
        self.x = x
        self.y = y
        self.size = size
        self.color = color

        # energy_value calculation (just calculates area of food then scales down by 10 and rounds)
        self.energy_value = round(DEFAULT_FOOD_MULTIPLIER * math.pi * (size ** 2))

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
            used_food_ids.remove(closest_food.id)
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

    def __eq__(self, other):
        if isinstance(other, Blob):
            return self.id == other.id
        return False
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

def main():
    
    id_tracker = IDTracker()

    # will remain static food elements for now. will change over time
    for i in range(N_STARTING_FOODS):

        # Ensure a unique food_id is assigned
        available_ids = [id for id in STARTING_FOOD_IDS if id not in used_food_ids]
        
        if available_ids:  # Ensure IDs are available before proceeding
            food_id = random.choice(available_ids)  # Select a unique ID
            used_food_ids.add(food_id)  # Mark it as used
            
            food = Food(food_id, 
                        DEFAULT_FOOD_COLOR, 
                        random.randint(DEFAULT_FOOD_SIZE, SCREEN_WIDTH - DEFAULT_FOOD_SIZE), 
                        random.randint(DEFAULT_FOOD_SIZE, SCREEN_HEIGHT - DEFAULT_FOOD_SIZE),
                        DEFAULT_FOOD_SIZE)

            foods.append(food)
        else:
            print("[WARNING] No more unique food IDs available!")

    if N_STARTING_BLOBS > len(STARTING_BLOB_IDS):
        print(f"[ERROR] INSUFFICIENT NUMBER OF STARTING IDS TO HANDLE NUMBER OF STARTING BLOBS AMOUNT. MUST BE BELOW {len(STARTING_BLOB_IDS)}")
        return

    for i in range(N_STARTING_BLOBS):

        # Ensure a unique food_id is assigned
        available_ids = [id for id in STARTING_BLOB_IDS if id not in used_blob_ids]
        
        if available_ids:  # Ensure IDs are available before proceeding
            blob_id = random.choice(available_ids)  # Select a unique ID
            used_blob_ids.add(blob_id)  # Mark it as used

            blob_id = STARTING_BLOB_IDS[i]
            blob = Blob(blob_id, 
                        DEFAULT_BLOB_COLOR, 
                        random.randint(DEFAULT_BLOB_SIZE, SCREEN_WIDTH - DEFAULT_BLOB_SIZE),
                        random.randint(DEFAULT_BLOB_SIZE, SCREEN_HEIGHT - DEFAULT_BLOB_SIZE),
                        DEFAULT_BLOB_SIZE,
                        DEFAULT_BLOB_SPEED,
                        DEFAULT_BLOB_ENERGY)

            blobs.append(blob)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)

        # CHANCE OF FOOD SPAWNING
        if random.randint(1, ONE_OUT_OF_CHANCE_OF_FOOD_SPAWNING_PER_FRAME) == 1:
            # Ensure a unique food_id is assigned
            available_ids = [id for id in STARTING_FOOD_IDS if id not in used_food_ids]
            
            if available_ids:  # Ensure IDs are available before proceeding
                food_id = random.choice(available_ids)  # Select a unique ID
                used_food_ids.add(food_id)  # Mark it as used
                
                food = Food(food_id, 
                            DEFAULT_FOOD_COLOR, 
                            random.randint(DEFAULT_FOOD_SIZE, SCREEN_WIDTH - DEFAULT_FOOD_SIZE), 
                            random.randint(DEFAULT_FOOD_SIZE, SCREEN_HEIGHT - DEFAULT_FOOD_SIZE),
                            DEFAULT_FOOD_SIZE)

                foods.append(food)
            else:
                print("[WARNING] No more unique food IDs available!")

        for food in foods:
            food.draw()
        
        random.shuffle(blobs) # Shuffle to ensure fairness and equal chance for best order
        for blob in blobs:
            blob.use_constant_energy()
            blob.food_action(foods)
            if blob.energy <= 0: # Blob no longer has energy, so it will perish
                blobs.remove(blob)
                blob.color = WHITE # Change color to show it will die
            # blob.print_stats(show_actions=False)
            blob.draw()

        # TODO Add logic to store each game state for data purposes (time-based game state data so we can analyze trends over time and stuff)
            # Should be a DF containing each Blob's attributes (diffrentiated by its id attribute) as well as the time (aka generation/day) of that data snapshot
        
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()

main()