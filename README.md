# Project-Simulation
<b>1. Initialization and Setup<b>
Pygame Window: Sets up a graphical window to display the intersection, signals, and vehicles.
Image Handling: Loads images for the background, signals, and vehicles. If an image is missing, it creates a colored placeholder to avoid crashes.
Directory Creation: Ensures all required image directories exist, preventing errors if assets are missing.
2. Traffic Signal Logic
Signal States: Each of the four signals (right, down, left, up) can be red, yellow, or green, with timers for each state.
Adaptive Timing: Signal allocation is dynamic:
If a direction’s waiting time exceeds a threshold (e.g., 96 seconds) and there are vehicles waiting, it gets priority and a longer green time.
Otherwise, the direction with the most vehicles waiting gets the green, with green time based on the number of waiting vehicles.
State Transitions: Signals cycle through green → yellow → red, with yellow as a short transition state.
3. Vehicle Simulation
Random Generation: Vehicles of various types (car, bus, truck, rickshaw, bike) are spawned randomly in different lanes and directions.
Movement Rules: Each vehicle:
Moves forward if its signal is green and there’s enough space ahead.
Stops at the stop line if the signal is red or if another vehicle is in front.
Tracks whether it has crossed the inflow and outflow lines to update inflow counts.
Lane Management: Vehicles maintain safe gaps and update their positions based on the vehicle ahead and the current signal.
4. Statistics and Visualization
Drawing: The simulation draws the intersection, signals, inflow/outflow lines, and all vehicles.
Stats Display: Next to each signal, it shows:
Direction name
Waiting time
Allocation (green) time
Inflow count (vehicles waiting)
Total vehicle count in that direction
5. Main Loop
Event Handling: Listens for window close events.
Signal Updates: Every second, updates signal states and waiting times.
Vehicle Updates: Moves all vehicles and redraws the scene at 60 frames per second.
Threading: Vehicle generation runs in a separate thread to keep the simulation smooth.
