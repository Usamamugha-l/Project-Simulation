# 🚦 Project-Simulation

A dynamic traffic signal simulation using **Pygame** that visualizes intelligent signal control based on vehicle flow and wait times.

---

## 1. 🛠️ Initialization and Setup

- **Pygame Window:** Sets up a graphical window to display the intersection, signals, and vehicles.
- **Image Handling:** Loads images for the background, signals, and vehicles. If an image is missing, it generates colored placeholders to avoid crashes.
- **Directory Creation:** Ensures all required image directories exist to prevent file errors.

---

## 2. 🚦 Traffic Signal Logic

- **Signal States:** Four signals (Right, Down, Left, Up), each with Red, Yellow, and Green states and associated timers.
- **Adaptive Timing Logic:**
  - If a direction’s waiting time exceeds a threshold (e.g., 96 seconds) and there are vehicles waiting, it is given priority and extended green time.
  - Otherwise, the direction with the most waiting vehicles gets green, and the duration is proportional to the number of vehicles.
- **State Transitions:** The cycle follows `Green → Yellow → Red`, with Yellow as a short transition phase.

---

## 3. 🚗 Vehicle Simulation

- **Random Generation:** Vehicles (car, bus, truck, rickshaw, bike) spawn randomly in all directions and lanes.
- **Movement Rules:**
  - Vehicles move forward if the signal is green and the path ahead is clear.
  - They stop at the stop line if the signal is red or another vehicle is in front.
  - Inflow and outflow lines are tracked for each vehicle to update statistics.
- **Lane Management:** Vehicles maintain safe distances and adjust based on signals and other vehicles.

---

## 4. 📊 Statistics and Visualization

- **Visual Display:** The intersection layout, traffic signals, vehicles, and road elements are drawn dynamically.
- **Real-Time Stats (per signal):**
  - Direction name
  - Waiting time
  - Allocation (green) time
  - Inflow count (vehicles waiting)
  - Total vehicle count in that direction

---

## 5. 🔁 Main Loop & Threading

- **Event Handling:** Handles quit events to close the window cleanly.
- **Signal Updates:** Signal states and timers update every second.
- **Vehicle Updates:** Vehicles move, stop, or wait based on logic and are redrawn at 60 FPS.
- **Multithreading:** Vehicle generation runs on a separate thread for smooth performance.

---

## 🧠 Technologies Used

- Python
- Pygame
- Multithreading


