# 🚦 Project-Simulation

A dynamic, visually-rich traffic intersection simulator built with **Python** and **Pygame**. This project models a four-way intersection with adaptive signal control, real-time vehicle flow, and even hardware integration for IoT/embedded systems. It’s the heart of your smart city traffic project!

---

## ✨ Features & Core Logics

### 1. 🛠️ Initialization and Setup

- **Pygame Window:** Launches a 1400x800 graphical window to display the intersection, signals, and vehicles in real time.
- **Image Handling:** Loads images for the background, signals, and vehicles. If an image is missing, it generates colored placeholders to avoid crashes and keep the simulation running.
- **Directory Creation:** Ensures all required image directories exist (`images/signals`, `images/right`, `images/left`, `images/up`, `images/down`) to prevent file errors and support easy asset management.

---

### 2. 🚦 Traffic Signal State Machine

- **Signal States:** Four signals (Right, Down, Left, Up), each with `Red`, `Yellow`, and `Green` states, managed by timers.
- **Adaptive Timing Logic:**
  - If a direction’s waiting time exceeds a threshold (e.g., 96 seconds) and there are vehicles waiting, it is given priority and extended green time.
  - Otherwise, the direction with the most waiting vehicles gets green, and the duration is proportional to the number of vehicles.
- **State Transitions:** The cycle follows `Green → Yellow → Red`, with Yellow as a short transition phase (3 seconds).
- **Automatic Transitions:** Signals transition automatically, ensuring only one green at a time.
- **Real-Time Hardware Sync:** Sends UDP commands to an ESP32 microcontroller, updating physical signals in sync with the simulation.

---

### 3. 🚗 Vehicle Simulation

- **Random Generation:** Vehicles (car, bus, truck, rickshaw, bike) spawn randomly in all directions and lanes, with logic for lane assignment and safe spacing.
- **Movement Rules:**
  - Vehicles move forward if the signal is green and the path ahead is clear.
  - They stop at the stop line if the signal is red or another vehicle is in front.
  - Inflow and outflow lines are tracked for each vehicle to update statistics.
- **Lane Management:** Vehicles maintain safe distances and adjust based on signals and other vehicles.
- **Crossing Logic:** Each vehicle tracks if it entered on green and updates inflow/outflow counts as it passes key lines.

---

### 4. 📊 Statistics and Visualization

- **Visual Display:** The intersection layout, traffic signals, vehicles, and road elements are drawn dynamically at 60 FPS.
- **Real-Time Stats (per signal):**
  - Direction name
  - Waiting time
  - Allocation (green) time
  - Inflow count (vehicles waiting)
  - Total vehicle count in that direction
- **Colored Lines:** Inflow (cyan) and outflow (red) lines are drawn for each direction to visualize vehicle counting logic.

---

### 5. 🔁 Main Loop & Multithreading

- **Event Handling:** Handles quit events to close the window cleanly.
- **Signal Updates:** Signal states and timers update every second, with adaptive logic for green allocation.
- **Vehicle Updates:** Vehicles move, stop, or wait based on logic and are redrawn at 60 FPS.
- **Multithreading:** Vehicle generation runs on a separate thread for smooth, non-blocking performance.

---

### 6. 🌐 ESP32 Hardware Integration

- **UDP Communication:** Sends real-time signal state changes to an ESP32 microcontroller, enabling physical signal control for IoT/embedded system integration.
- **Flexible Messaging:** Communicates lane, state, and duration for seamless hardware-software sync.

---

## 🧠 Technologies Used

- Python
- Pygame
- Multithreading
- UDP Networking (for hardware integration)