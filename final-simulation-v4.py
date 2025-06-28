import random
import time
import threading
import pygame
import sys
import os

pygame.init()
# --- Signal and GUI Setup ---
noOfSignals = 4
signalCoods = [(530,230),(810,230),(810,570),(530,570)]
signalTimerCoods = [(530,210),(810,210),(810,550),(530,550)]

pygame.init()
screenWidth = 1400
screenHeight = 800
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Traffic Signal Simulation")

def safe_load_image(path):
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        return pygame.image.load(path)
    except (pygame.error, FileNotFoundError) as e:
        print(f"Warning: Could not load image '{path}': {e}")
        # Create a placeholder surface if image is missing
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        surf.fill((200, 0, 0, 128))
        return surf

# Ensure required directories exist to avoid errors if images are missing
os.makedirs('images/signals', exist_ok=True)
os.makedirs('images/right', exist_ok=True)
os.makedirs('images/left', exist_ok=True)
os.makedirs('images/up', exist_ok=True)
os.makedirs('images/down', exist_ok=True)

background = safe_load_image('images/mod_int.png')
redSignal = safe_load_image('images/signals/red.png')
yellowSignal = safe_load_image('images/signals/yellow.png')
greenSignal = safe_load_image('images/signals/green.png')
font = pygame.font.Font(None, 30)

# --- Traffic Signal State ---
allocation_time = [0] * noOfSignals
waiting_times = [0] * noOfSignals
inflowCounts = [0] * noOfSignals
currentGreen = 0
last_decrement_time = time.time()

# --- Signal State Machine ---
signal_states = ['red'] * noOfSignals  # 'red', 'yellow', 'green'
signal_timers = [0] * noOfSignals      # seconds left in current state
YELLOW_TIME = 3

# --- Vehicle Simulation Setup ---
carTime = 2
bikeTime = 2
rickshawTime = 2
busTime = 2
truckTime = 2

x = {'right':[0,0,0], 'down':[755,727,697], 'left':[1400,1400,1400], 'up':[602,627,657]}
y = {'right':[348,370,398], 'down':[0,0,0], 'left':[498,466,436], 'up':[800,800,800]}
vehicles = {'right': {0:[], 1:[], 2:[], 'crossed':0}, 'down': {0:[], 1:[], 2:[], 'crossed':0}, 'left': {0:[], 1:[], 2:[], 'crossed':0}, 'up': {0:[], 1:[], 2:[], 'crossed':0}}
vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'rickshaw', 4:'bike'}
directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}
stops = {'right': [580,580,580], 'down': [320,320,320], 'left': [810,810,810], 'up': [545,545,545]}
mid = {'right': {'x':705, 'y':445}, 'down': {'x':695, 'y':450}, 'left': {'x':695, 'y':425}, 'up': {'x':695, 'y':400}}
rotationAngle = 3
speeds = {'car':2.25, 'bus':2.25, 'truck':2.25, 'rickshaw':2.25, 'bike':2.25}
gap = 15
gap2 = 15
simulation = pygame.sprite.Group()

# --- Inflow and Outflow Lines (near spawn and near stop line) ---
inflowLines = {
    'right': 180,   # near spawn (x increases)
    'down': 50,    # near spawn (y increases)
    'left': 1250,  # near spawn (x decreases)
    'up': 750      # near spawn (y decreases)
}
outflowLines = {
    'right': stopLines['right'] - 5,  # just before stop line
    'down': stopLines['down'] - 5,
    'left': stopLines['left'] -1,
    'up': stopLines['up'] -1
}

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.will_turn = will_turn  # Store will_turn for future use
        # Ensure lane index is valid for the direction
        if lane < 0 or lane >= len(x[direction]):
            raise ValueError(f"Invalid lane index {lane} for direction '{direction}'")
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        path = "images/" + direction + "/" + vehicleClass + ".png"
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"File not found: {path}")
            self.originalImage = pygame.image.load(path)
            self.currentImage = pygame.image.load(path)
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load vehicle image '{path}': {e}")
            self.originalImage = pygame.Surface((40, 20), pygame.SRCALPHA)
            self.originalImage.fill((255, 0, 0, 128))
            self.currentImage = self.originalImage.copy()
        self.has_entered_on_green = False
        self.passed_inflow = False
        self.passed_outflow = False
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        if direction=='right':
            if self.index > 0 and len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0:
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].currentImage.get_rect().width - gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif direction=='left':
            if self.index > 0 and len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0:
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].currentImage.get_rect().width + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] += temp
            stops[direction][lane] += temp
        elif direction=='down':
            if self.index > 0 and len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0:
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].currentImage.get_rect().height - gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif direction=='up':
            if self.index > 0 and len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0:
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].currentImage.get_rect().height + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] += temp
            stops[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.currentImage, (self.x, self.y))

    def move(self):
        can_move = (signal_states[self.direction_number] == 'green')

        # --- Inflow/Outflow logic ---
        if self.direction == 'right':
            if not self.passed_inflow and self.x >= inflowLines['right']:
                inflowCounts[self.direction_number] += 1
                self.passed_inflow = True
            if self.passed_inflow and not self.passed_outflow and self.x >= outflowLines['right']:
                inflowCounts[self.direction_number] = max(0, inflowCounts[self.direction_number] - 1)
                self.passed_outflow = True
        elif self.direction == 'down':
            if not self.passed_inflow and self.y >= inflowLines['down']:
                inflowCounts[self.direction_number] += 1
                self.passed_inflow = True
            if self.passed_inflow and not self.passed_outflow and self.y >= outflowLines['down']:
                inflowCounts[self.direction_number] = max(0, inflowCounts[self.direction_number] - 1)
                self.passed_outflow = True
        elif self.direction == 'left':
            if not self.passed_inflow and self.x <= inflowLines['left']:
                inflowCounts[self.direction_number] += 1
                self.passed_inflow = True
            if self.passed_inflow and not self.passed_outflow and self.x <= outflowLines['left']:
                inflowCounts[self.direction_number] = max(0, inflowCounts[self.direction_number] - 1)
                self.passed_outflow = True
        elif self.direction == 'up':
            if not self.passed_inflow and self.y <= inflowLines['up']:
                inflowCounts[self.direction_number] += 1
                self.passed_inflow = True
            if self.passed_inflow and not self.passed_outflow and self.y <= outflowLines['up']:
                inflowCounts[self.direction_number] = max(0, inflowCounts[self.direction_number] - 1)
                self.passed_outflow = True

        # --- Movement logic ---
        lane_vehicles = vehicles[self.direction][self.lane]
        vehicle_ahead = lane_vehicles[self.index - 1] if self.index > 0 else None

        if self.direction == 'right':
            stop_line = stopLines[self.direction]
            vehicle_end = self.x + self.currentImage.get_rect().width

            can_advance = True
            # Check gap with vehicle ahead
            if vehicle_ahead:
                if not vehicle_ahead.crossed:
                    min_x = vehicle_ahead.x - vehicle_ahead.currentImage.get_rect().width - gap
                    if vehicle_end + self.speed > min_x:
                        can_advance = False
                else:
                    min_x = vehicle_ahead.x - gap
                    if vehicle_end + self.speed > min_x:
                        can_advance = False

            # If first vehicle (no vehicle ahead), only check stop line and signal
            if not vehicle_ahead:
                if self.crossed == 0:
                    if not can_move and vehicle_end + self.speed > stop_line:
                        can_advance = False

            # Prevent crossing stop line on red
            if self.crossed == 0 and vehicle_ahead:
                next_pos = vehicle_end + self.speed
                if not can_move and next_pos > stop_line:
                    can_advance = False

            # Move logic
            if self.crossed == 0 and can_move and can_advance:
                self.x += self.speed
            elif self.crossed == 0 and not can_move and can_advance and vehicle_end + self.speed <= stop_line:
                self.x += self.speed
            elif self.crossed == 1 and can_advance:
                self.x += self.speed

            if self.crossed == 0 and vehicle_end >= stop_line:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if can_move:
                    self.has_entered_on_green = True

        elif self.direction == 'down':
            stop_line = stopLines[self.direction]
            vehicle_end = self.y + self.currentImage.get_rect().height

            can_advance = True
            if vehicle_ahead:
                if not vehicle_ahead.crossed:
                    min_y = vehicle_ahead.y - vehicle_ahead.currentImage.get_rect().height - gap
                    if vehicle_end + self.speed > min_y:
                        can_advance = False
                else:
                    min_y = vehicle_ahead.y - gap
                    if vehicle_end + self.speed > min_y:
                        can_advance = False

            if not vehicle_ahead:
                if self.crossed == 0:
                    if not can_move and vehicle_end + self.speed > stop_line:
                        can_advance = False

            if self.crossed == 0 and vehicle_ahead:
                next_pos = vehicle_end + self.speed
                if not can_move and next_pos > stop_line:
                    can_advance = False

            if self.crossed == 0 and can_move and can_advance:
                self.y += self.speed
            elif self.crossed == 0 and not can_move and can_advance and vehicle_end + self.speed <= stop_line:
                self.y += self.speed
            elif self.crossed == 1 and can_advance:
                self.y += self.speed

            if self.crossed == 0 and vehicle_end >= stop_line:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if can_move:
                    self.has_entered_on_green = True

        elif self.direction == 'left':
            stop_line = stopLines[self.direction]
            vehicle_front = self.x

            can_advance = True
            if vehicle_ahead:
                if not vehicle_ahead.crossed:
                    min_x = vehicle_ahead.x + vehicle_ahead.currentImage.get_rect().width + gap
                    if vehicle_front - self.speed < min_x:
                        can_advance = False
                else:
                    min_x = vehicle_ahead.x + gap
                    if vehicle_front - self.speed < min_x:
                        can_advance = False

            if not vehicle_ahead:
                if self.crossed == 0:
                    if not can_move and vehicle_front - self.speed < stop_line:
                        can_advance = False

            if self.crossed == 0 and vehicle_ahead:
                next_pos = vehicle_front - self.speed
                if not can_move and next_pos < stop_line:
                    can_advance = False

            if self.crossed == 0 and can_move and can_advance:
                self.x -= self.speed
            elif self.crossed == 0 and not can_move and can_advance and vehicle_front - self.speed >= stop_line:
                self.x -= self.speed
            elif self.crossed == 1 and can_advance:
                self.x -= self.speed

            if self.crossed == 0 and vehicle_front <= stop_line:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if can_move:
                    self.has_entered_on_green = True

        elif self.direction == 'up':
            stop_line = stopLines[self.direction]
            vehicle_front = self.y

            can_advance = True
            if vehicle_ahead:
                if not vehicle_ahead.crossed:
                    min_y = vehicle_ahead.y + vehicle_ahead.currentImage.get_rect().height + gap
                    if vehicle_front - self.speed < min_y:
                        can_advance = False
                else:
                    min_y = vehicle_ahead.y + gap
                    if vehicle_front - self.speed < min_y:
                        can_advance = False

            if not vehicle_ahead:
                if self.crossed == 0:
                    if not can_move and vehicle_front - self.speed < stop_line:
                        can_advance = False

            if self.crossed == 0 and vehicle_ahead:
                next_pos = vehicle_front - self.speed
                if not can_move and next_pos < stop_line:
                    can_advance = False

            if self.crossed == 0 and can_move and can_advance:
                self.y -= self.speed
            elif self.crossed == 0 and not can_move and can_advance and vehicle_front - self.speed >= stop_line:
                self.y -= self.speed
            elif self.crossed == 1 and can_advance:
                self.y -= self.speed

            if self.crossed == 0 and vehicle_front <= stop_line:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if can_move:
                    self.has_entered_on_green = True

def generateVehicles():
    while True:
        vehicle_type = random.randint(0,4)
        lane_number = random.randint(0,2)
        will_turn = 0
        if lane_number == 2:
            temp = random.randint(0,4)
            if temp <= 2:
                will_turn = 1
            else:
                will_turn = 0
        temp = random.randint(0,999)
        direction_number = 0
        a = [400,800,900,1000]
        if temp < a[0]:
            direction_number = 0
        elif temp < a[1]:
            direction_number = 1
        elif temp < a[2]:
            direction_number = 2
        else:
            direction_number = 3

        direction = directionNumbers[direction_number]
        vehicleClass = vehicleTypes[vehicle_type]
        Vehicle(lane_number, vehicleClass, direction_number, direction, will_turn)
        time.sleep(random.uniform(0.7, 1.5))

def allocate_next_signal():
    global currentGreen
    # Only update waiting_times here, do not decrement allocation_time (done in update_signals)
    for i in range(noOfSignals):
        if allocation_time[i] > 0:
            waiting_times[i] = 0
        else:
            waiting_times[i] += 1

    # Waiting time priority logic
    for i in [0, 1, 2, 3]:
        if waiting_times[i] >= 96 and inflowCounts[i] > 0:
            inflow = inflowCounts[i]
            allocation_time[i] = (
                12 if inflow <= 4 else
                17 if inflow <= 6 else
                22 if inflow <= 8 else
                27
            )
            currentGreen = i
            return i, allocation_time[i]

    # Normal flow logic
    max_inflow = max(inflowCounts)
    if max_inflow > 0:
        max_index = inflowCounts.index(max_inflow)
        if waiting_times[max_index] >= 1:
            allocation_time[max_index] = (
                10 if max_inflow <= 4 else
                15 if max_inflow <= 6 else
                20 if max_inflow <= 8 else
                22
            )
            currentGreen = max_index
            return max_index, allocation_time[max_index]
    return None, 0

def update_signals():
    global currentGreen
    for i in range(noOfSignals):
        # Decrement allocation_time while green
        if signal_states[i] == 'green' and allocation_time[i] > 0:
            allocation_time[i] -= 1

        if signal_timers[i] > 0:
            signal_timers[i] -= 1
            if signal_timers[i] == 0:
                if signal_states[i] == 'yellow':
                    # If yellow was before green, now go green
                    if allocation_time[i] > 0:
                        signal_states[i] = 'green'
                        signal_timers[i] = allocation_time[i]
                    else:
                        # If yellow was before red, now go red
                        signal_states[i] = 'red'
                elif signal_states[i] == 'green':
                    # Green finished, go yellow before red
                    signal_states[i] = 'yellow'
                    signal_timers[i] = int(YELLOW_TIME)
                    allocation_time[i] = 0
                elif signal_states[i] == 'red':
                    pass  # Stay red until it's this direction's turn

    # If no signal is green or yellow, pick next to turn green using your allocation logic
    if all(signal_states[i] != 'green' and signal_states[i] != 'yellow' for i in range(noOfSignals)):
        next_green, green_time = allocate_next_signal()
        if next_green is not None and green_time > 0:
            signal_states[next_green] = 'yellow'
            signal_timers[next_green] = int(YELLOW_TIME)
            # allocation_time[next_green] is already set in allocate_next_signal()
            currentGreen = next_green
            waiting_times[next_green] = 0

def update_waiting_times():
    for i in range(noOfSignals):
        if signal_states[i] == 'red':
            waiting_times[i] += 1
        else:
            waiting_times[i] = 0

def main():
    global last_decrement_time
    threading.Thread(target=generateVehicles, daemon=True).start()
    clock = pygame.time.Clock()
    signalTexts = [""] * noOfSignals
    black = (0, 0, 0)
    white = (255, 255, 255)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update signals and waiting logic every second
        now = time.time()
        if now - last_decrement_time >= 1:
            update_signals()
            update_waiting_times()
            last_decrement_time = now

        screen.blit(background, (0,0))

        # Draw inflow and outflow lines for each direction
        line_color = (0,255,255)
        out_color = (255,0,0)
        # Right
        pygame.draw.line(screen, line_color, (inflowLines['right'], 350), (inflowLines['right'], 430), 2)
        pygame.draw.line(screen, out_color, (outflowLines['right'], 350), (outflowLines['right'], 430), 2)
        # Down
        pygame.draw.line(screen, line_color, (690, inflowLines['down']), (770, inflowLines['down']), 2)
        pygame.draw.line(screen, out_color, (690, outflowLines['down']), (770, outflowLines['down']), 2)
        # Left
        pygame.draw.line(screen, line_color, (inflowLines['left'], 430), (inflowLines['left'], 520), 2)
        pygame.draw.line(screen, out_color, (outflowLines['left'], 430), (outflowLines['left'], 520), 2)    
        # Up
        pygame.draw.line(screen, line_color, (600, inflowLines['up']), (690, inflowLines['up']), 2)
        pygame.draw.line(screen, out_color, (600, outflowLines['up']), (690, outflowLines['up']), 2)

        # Draw signals
        for i in range(noOfSignals):
            if signal_states[i] == 'green':
                screen.blit(greenSignal, signalCoods[i])
                signal_text = allocation_time[i]
            elif signal_states[i] == 'yellow':
                screen.blit(yellowSignal, signalCoods[i])
                signal_text = "YELLOW"
            else:
                screen.blit(redSignal, signalCoods[i])
                signal_text = "RED"
            signalTexts[i] = font.render(str(signal_text), True, white, black)
            screen.blit(signalTexts[i], signalTimerCoods[i])

        # Move and draw vehicles
        for vehicle in simulation:
            vehicle.move()
            vehicle.render(screen)

        # Display stats beside each signal
        for i in range(noOfSignals):
            dirn = directionNumbers[i]
            vehicle_count = sum(len(vehicles[dirn][lane]) for lane in range(3))
            stats_lines = [
                f"Direction: {dirn.capitalize()}",
                f"Waiting Time: {waiting_times[i]}",
                f"Allocation Time: {allocation_time[i]}",
                f"Inflow Count: {inflowCounts[i]}",
                f"Vehicle Count: {vehicle_count}"
            ]
            sx, sy = signalCoods[i]

            if i == 0:  # right
                offset = (-200, 0)
            elif i == 1:  # down
                offset = (60, 0)
            elif i == 2:  # left
                offset = (60, 0)
            elif i == 3:  # up
                offset = (-200, 0)
            for idx, line in enumerate(stats_lines):
                stat_surface = font.render(line, True, (255,255,255))
                screen.blit(stat_surface, (sx + offset[0], sy + offset[1] + idx*22))

        pygame.display.update()
        clock.tick(60)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()