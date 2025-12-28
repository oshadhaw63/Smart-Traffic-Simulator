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
                # Stop if approaching line AND haven't passed it
                if self.y < self.stop_line and self.y > (self.stop_line - 50):
                    should_stop = True
            elif self.lane_direction == 'horizontal':
                if self.x < self.stop_line and self.x > (self.stop_line - 50):
                    should_stop = True

        # --- CHECK 2: Car Ahead (Collision Avoidance) ---
        if car_ahead:
            if self.lane_direction == 'vertical':
                # Calculate distance to the car in front
                distance = car_ahead.y - self.y
                # If car is ahead (positive distance) AND too close -> STOP
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
        # Determine color (Visual debug: Red if stopped, Blue if moving)
        # For now, let's keep it blue
        pygame.draw.rect(screen, BLUE_CAR, (self.x, self.y, 20, 40))



class TrafficSimulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("UoM Smart Traffic Project - Sprint 4")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Components
        self.traffic_light = TrafficLight(320, 320, 'vertical') 
        
        # CHANGED: Use a list for cars
        self.cars = [] 
        self.spawn_timer = 0 # Timer to control how often cars appear
        

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

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # --- UPDATE LOGIC ---
            self.traffic_light.update()

            # 1. Spawner: Add a new car every 100 frames (approx 1.5 seconds)
            self.spawn_timer += 1
            if self.spawn_timer > 100:
                self.cars.append(Car('vertical'))
                self.spawn_timer = 0

            # 2. Move Cars
            for i, car in enumerate(self.cars):
                # Find the car ahead
                car_ahead = None
                if i > 0: # If not the first car, the one ahead is at index i-1
                    car_ahead = self.cars[i-1]
                
                car.move(self.traffic_light, car_ahead)

            # 3. Cleanup: Remove cars that have gone off screen (Memory Management)
            # (Simple check: if y > HEIGHT, remove it)
            self.cars = [car for car in self.cars if car.y < HEIGHT and car.x < WIDTH]
            
            # --- DRAWING ---
            self.draw_road()
            self.traffic_light.draw(self.screen)
            for car in self.cars:
                car.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(FPS)


        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    sim = TrafficSimulation()
    sim.run()



