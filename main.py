import pygame
import sys

# --- Configuration ---
WIDTH, HEIGHT = 800, 800
FPS = 60  # Frames Per Second

# Colors (R, G, B)
GRAY_ROAD = (40, 40, 40)
GREEN_GRASS = (34, 139, 34)
WHITE_MARKING = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE_CAR = (50, 100, 255)

# Lane Coordinates (Hardcoded for simplicity initially)
# We assume a road width of 100px.
# Vertical Road: x=350 to x=450
# Horizontal Road: y=350 to y=450

class TrafficLight:
    def __init__(self, x, y, lane_type):
        self.x = x
        self.y = y
        self.lane_type = lane_type # 'vertical' or 'horizontal'
        self.state = "RED"         # Initial state
        self.timer = 0

    def update(self):
        # AUTOMATIC TIMER: Switch every 180 frames (approx 3 seconds)
        self.timer += 1
        if self.timer > 180:
            self.state = "GREEN" if self.state == "RED" else "RED"
            self.timer = 0

    def draw(self, screen):
        # Choose color based on state
        color = RED if self.state == "RED" else GREEN
        # Draw the light as a circle
        pygame.draw.circle(screen, color, (self.x, self.y), 15)





class Car:
    def __init__(self, lane_direction):
        self.lane_direction = lane_direction 
        self.speed = 3
        self.length = 40  # Length of the car
        self.safe_distance = 60 # Minimum gap to keep
        
        # STOPPING DISTANCE VARIABLES
        if self.lane_direction == 'vertical':
            self.x = 375  
            self.y = -50  
            self.stop_line = 340
        elif self.lane_direction == 'horizontal':
            self.x = -50
            self.y = 375
            self.stop_line = 340
            
    def move(self, traffic_light, car_ahead):
        should_stop = False
        
        # --- CHECK 1: Traffic Light ---
        if traffic_light.state == "RED":
            if self.lane_direction == 'vertical':
                if self.y < self.stop_line and self.y > (self.stop_line - 50):
                    should_stop = True
            elif self.lane_direction == 'horizontal':
                if self.x < self.stop_line and self.x > (self.stop_line - 50):
                    should_stop = True

        # --- CHECK 2: Car Ahead (Collision Avoidance) ---
        if car_ahead:
            if self.lane_direction == 'vertical':
                distance = car_ahead.y - self.y
                if 0 < distance < self.safe_distance:
                    should_stop = True
            elif self.lane_direction == 'horizontal':
                distance = car_ahead.x - self.x
                if 0 < distance < self.safe_distance:
                    should_stop = True

        # --- MOVE ---
        if not should_stop:
            if self.lane_direction == 'vertical':
                self.y += self.speed
            elif self.lane_direction == 'horizontal':
                self.x += self.speed
            
    def draw(self, screen):
        # --- FIX: Determine dimensions based on direction ---
        if self.lane_direction == 'vertical':
            width = 20
            height = 40
        else: # horizontal
            width = 40
            height = 20
            
        pygame.draw.rect(screen, BLUE_CAR, (self.x, self.y, width, height))

        

class TrafficSimulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("UoM Smart Traffic Project - Sprint 5")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # --- TRAFFIC LIGHTS ---
        # Create two lights. 
        # Light 1 (Vertical) starts RED.
        # Light 2 (Horizontal) starts GREEN.
        self.light_vertical = TrafficLight(320, 320, 'vertical')
        self.light_vertical.state = "RED"
        
        self.light_horizontal = TrafficLight(450, 450, 'horizontal') 
        self.light_horizontal.state = "GREEN" # Opposite of vertical
        
        # --- CAR LISTS ---
        # Separate lists for collision logic
        self.vertical_cars = [] 
        self.horizontal_cars = []

        self.last_switch_time = 0
        self.min_switch_time = 200 # Frames (approx 3-4 seconds)
        
        # REMOVE self.spawn_timer if you want, or keep it for spawning
        self.spawn_timer = 0
        
       


    def draw_road(self):
        """Draws the background grass and the black roads."""
        self.screen.fill(GREEN_GRASS)

        # Vertical Road (Centered at X=400, width=100)
        pygame.draw.rect(self.screen, GRAY_ROAD, (350, 0, 100, HEIGHT))
        
        # Horizontal Road (Centered at Y=400, width=100)
        pygame.draw.rect(self.screen, GRAY_ROAD, (0, 350, WIDTH, 100))
        
        # Optional: Draw center lines (Yellow dashed lines)
        pygame.draw.line(self.screen, WHITE_MARKING, (400, 0), (400, HEIGHT), 2)
        pygame.draw.line(self.screen, WHITE_MARKING, (0, 400), (WIDTH, 400), 2)


    def get_queue_length(self, cars, lane_type):
        """Counts how many cars are waiting near the intersection."""
        count = 0
        for car in cars:
            # Check if car is stopped or moving very slowly
            # AND is close to the intersection (Stop Zone)
            
            is_stopped = car.speed == 0 or (hasattr(car, 'waiting') and car.waiting) 
            # Note: In our current simple physics, cars just stop moving. 
            # Let's check if they are near the stop line.
            
            if lane_type == 'vertical':
                if 250 < car.y < 340: # Between 250px and stop line
                    count += 1
            elif lane_type == 'horizontal':
                if 250 < car.x < 340:
                    count += 1
        return count
    


    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # --- 1. SMART TRAFFIC LOGIC ---
            # Increase the timer since last switch
            self.last_switch_time += 1
            
            # Count the queues
            v_count = self.get_queue_length(self.vertical_cars, 'vertical')
            h_count = self.get_queue_length(self.horizontal_cars, 'horizontal')
            
            # DEBUG: Print counts to console to see if it works
            # print(f"Vertical: {v_count} | Horizontal: {h_count}")

            # DECISION ALGORITHM:
            # Only switch if:
            # 1. We have waited long enough (Cool-down)
            # 2. The RED lane has significantly more cars than the GREEN lane
            
            if self.last_switch_time > self.min_switch_time:
                
                if self.light_vertical.state == "GREEN":
                    # If vertical is green but horizontal has a queue -> Switch
                    if h_count > v_count:
                        self.light_vertical.state = "RED"
                        self.light_horizontal.state = "GREEN"
                        self.last_switch_time = 0
                        
                elif self.light_vertical.state == "RED":
                    # If vertical is red but has a huge queue -> Switch
                    if v_count > h_count:
                        self.light_vertical.state = "GREEN"
                        self.light_horizontal.state = "RED"
                        self.last_switch_time = 0
                        

            # --- 2. SPAWNER (Randomly spawn in both lanes) ---
            self.spawn_timer += 1
            if self.spawn_timer > 60: # Spawn faster (every 1 second)
                import random
                if random.choice([True, False]):
                    self.vertical_cars.append(Car('vertical'))
                else:
                    self.horizontal_cars.append(Car('horizontal'))
                self.spawn_timer = 0

            # --- 3. MOVE VERTICAL CARS ---
            for i, car in enumerate(self.vertical_cars):
                car_ahead = self.vertical_cars[i-1] if i > 0 else None
                car.move(self.light_vertical, car_ahead)

            # --- 4. MOVE HORIZONTAL CARS ---
            for i, car in enumerate(self.horizontal_cars):
                car_ahead = self.horizontal_cars[i-1] if i > 0 else None
                car.move(self.light_horizontal, car_ahead)

            # --- 5. CLEANUP ---
            self.vertical_cars = [c for c in self.vertical_cars if c.y < HEIGHT]
            self.horizontal_cars = [c for c in self.horizontal_cars if c.x < WIDTH]
            
            # --- 6. DRAWING ---
            self.draw_road()
            
            self.light_vertical.draw(self.screen)
            self.light_horizontal.draw(self.screen)
            
            for car in self.vertical_cars: car.draw(self.screen)
            for car in self.horizontal_cars: car.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(FPS)


        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    sim = TrafficSimulation()
    sim.run()


